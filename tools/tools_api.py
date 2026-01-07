"""
Standalone tool implementations for API access.
These are extracted from the MCP tools to allow direct function calls via the API.
"""
import subprocess
import shutil
from config import (
    BASE_REPO_DIR,
    APPLICATIONS,
    BUILD_COMMANDS,
    ALLOWED_SERVICES
)
from logging_config import get_logger

logger = get_logger(__name__)


# -------------------------
# Utility helpers
# -------------------------
def _run(cmd, cwd=None, timeout=600):
    """Execute a shell command and return results"""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return {"code": p.returncode, "stdout": p.stdout[-4000:], "stderr": p.stderr[-4000:]}
    except subprocess.TimeoutExpired:
        logger.warning(f"Command timed out after {timeout} seconds: {' '.join(cmd)}")
        return {"code": -1, "stdout": "", "stderr": f"Command timed out after {timeout} seconds"}


def require_application(application_name: str) -> None:
    """Validate that application is allowed"""
    if application_name not in APPLICATIONS:
        logger.warning(f"Attempted access to unauthorized application: {application_name}")
        raise ValueError(f"Application '{application_name}' not allowed")
    logger.debug(f"Application validation passed: {application_name}")


def require_service(service: str) -> None:
    """Validate that service is allowed"""
    if service not in ALLOWED_SERVICES:
        logger.warning(f"Attempted access to unauthorized service: {service}")
        raise ValueError(f"Service '{service}' not allowed")
    logger.debug(f"Service validation passed: {service}")


def get_artifact_file(application_name: str):
    """Get the artifact file for an application"""
    app_cfg = APPLICATIONS[application_name]
    artifact_pattern = BASE_REPO_DIR / application_name / app_cfg["artifact_path"]

    if '*' in str(artifact_pattern):
        artifacts = list(artifact_pattern.parent.glob(artifact_pattern.name))
        if not artifacts:
            raise ValueError("No artifact found matching pattern")
        # Sort by modification time descending (newest first)
        artifacts.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        artifact = artifacts[0]
        if len(artifacts) > 1:
            logger.info(f"Multiple artifacts found, using the newest: {artifact}")
    else:
        artifact = artifact_pattern

    return artifact


# ========================
# API TOOLS (Standalone)
# ========================

def get_app_deployment_configuration() -> dict:
    """Get application deployment configuration"""
    logger.debug("Retrieving deployment configuration")
    return {"applications": APPLICATIONS}


def checkout_repository(application_name: str) -> dict:
    """Clone or update repository safely"""
    logger.info(
        "Checking out application source code",
        extra={"extra_fields": {"application_name": application_name}}
    )

    require_application(application_name)

    app_cfg = APPLICATIONS[application_name]
    repo_path = BASE_REPO_DIR / application_name
    repo_path.parent.mkdir(parents=True, exist_ok=True)

    if not repo_path.exists():
        result = _run(["git", "clone", "-b", app_cfg["branch"], app_cfg["git_url"], str(repo_path)])
    else:
        _run(["git", "fetch"], cwd=repo_path)
        _run(["git", "checkout", app_cfg["branch"]], cwd=repo_path)
        result = _run(["git", "pull"], cwd=repo_path)

    return {"success": result["code"] == 0, "details": result}


def build_application(application_name: str) -> dict:
    """Build application using predefined build system"""
    logger.info(
        "Building application",
        extra={"extra_fields": {"application_name": application_name}}
    )

    require_application(application_name)
    if application_name not in APPLICATIONS:
        raise ValueError("Repository not allowed")

    app_cfg = APPLICATIONS[application_name]
    repo_path = BASE_REPO_DIR / application_name
    cmd = BUILD_COMMANDS[app_cfg["build_type"]]

    if not cmd:
        raise ValueError("Unsupported build type")

    result = _run(cmd, cwd=repo_path)
    return {"success": result["code"] == 0, "logs": result}


def verify_artifact(application_name: str) -> dict:
    """Verify build artifact exists and is non-empty"""
    logger.info(
        "Verifying artifact",
        extra={"extra_fields": {"application_name": application_name}}
    )

    require_application(application_name)

    try:
        artifact = get_artifact_file(application_name)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    if artifact.stat().st_size == 0:
        return {"success": False, "error": "Artifact size is zero"}

    return {"success": True, "artifact": str(artifact), "size_bytes": artifact.stat().st_size}


def deploy_artifact(application_name: str) -> dict:
    """Copy artifact to deployment directory with backup"""
    logger.info(
        "Deploying artifact",
        extra={"extra_fields": {"application_name": application_name}}
    )
    try:
        require_application(application_name)

        app_cfg = APPLICATIONS[application_name]
        try:
            artifact = get_artifact_file(application_name)
        except ValueError as e:
            logger.error(
                "Artifact not found for deployment",
                extra={"extra_fields": {"application_name": application_name, "error": str(e)}}
            )
            raise ValueError("Artifact not found, build first")

        deploy_dir = app_cfg['deploy_path']
        deploy_dir.mkdir(parents=True, exist_ok=True)

        target = deploy_dir / artifact.name
        backup = deploy_dir / f"{artifact.name}.bak"

        if target.exists():
            logger.info(
                "Creating backup of existing deployment",
                extra={"extra_fields": {"application_name": application_name, "backup": str(backup)}}
            )
            shutil.move(target, backup)

        logger.info(
            "Copying artifact to deployment directory",
            extra={"extra_fields": {
                "application_name": application_name,
                "source": str(artifact),
                "target": str(target)
            }}
        )
        shutil.copy2(artifact, target)

        # Manage symlink if configured
        if "symlink" in app_cfg:
            symlink_path = deploy_dir / app_cfg["symlink"]
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()
                logger.info(
                    "Removed old symlink",
                    extra={"extra_fields": {"application_name": application_name, "symlink": str(symlink_path)}}
                )
            symlink_path.symlink_to(target)
            logger.info(
                "Created symlink",
                extra={"extra_fields": {
                    "application_name": application_name,
                    "symlink": str(symlink_path),
                    "points_to": str(target)
                }}
            )

        logger.info(
            "Artifact deployed successfully",
            extra={"extra_fields": {"application_name": application_name, "deployed_to": str(target)}}
        )
        return {"success": True, "deployed_to": str(target), "backup": str(backup) if backup.exists() else None}
    except Exception:
        logger.error("Error during artifact deployment", exc_info=True)
        raise


def restart_application(application_name: str) -> dict:
    """Restart systemd service"""
    logger.info(
        "Restarting application service",
        extra={"extra_fields": {"application_name": application_name}}
    )

    try:
        require_application(application_name)
        app_cfg = APPLICATIONS[application_name]
        service_name = app_cfg["service_name"]
        require_service(service_name)
        result = _run(["systemctl", "restart", service_name])

        success = result["code"] == 0
        if success:
            logger.info(
                "Service restarted successfully",
                extra={"extra_fields": {"service": service_name}}
            )
        else:
            logger.error(
                "Service restart failed",
                extra={"extra_fields": {"service": service_name, "code": result["code"]}}
            )
        return {"service": service_name, "success": success, "details": result}
    except Exception:
        logger.error("Error restarting service", exc_info=True)
        raise

def stop_application(application_name: str) -> dict:
    """Stop systemd service"""
    logger.info(
        "Stopping application service",
        extra={"extra_fields": {"application_name": application_name}}
    )

    try:
        require_application(application_name)
        app_cfg = APPLICATIONS[application_name]
        service_name = app_cfg["service_name"]
        require_service(service_name)
        result = _run(["systemctl", "stop", service_name])

        success = result["code"] == 0
        if success:
            logger.info(
                "Service stopped successfully",
                extra={"extra_fields": {"service": service_name}}
            )
        else:
            logger.error(
                "Service stopped failed",
                extra={"extra_fields": {"service": service_name, "code": result["code"]}}
            )
        return {"service": service_name, "success": success, "details": result}
    except Exception:
        logger.error("Error stopping service", exc_info=True)
        raise

def get_application_status(application_name: str) -> dict:
    """Get systemd service status"""
    logger.info(
        "Getting application status",
        extra={"extra_fields": {"application_name": application_name}}
    )

    try:
        require_application(application_name)
        app_cfg = APPLICATIONS[application_name]
        service_name = app_cfg["service_name"]
        require_service(service_name)
        logger.debug(
            "Fetching application status",
            extra={"extra_fields": {"service_name": service_name}}
        )
        result = _run(["systemctl", "status", service_name, "--no-pager"])
        logger.debug(
            "Application status fetched",
            extra={"extra_fields": {"service": service_name}}
        )
        return {"service": service_name, "status": result}
    except Exception:
        logger.error("Error fetching service status", exc_info=True)
        raise


def get_recent_logs(application_name: str, lines: int = 100) -> dict:
    """Fetch recent logs safely"""
    logger.info(
        "Getting recent logs",
        extra={"extra_fields": {"application_name": application_name}}
    )

    try:
        require_application(application_name)
        app_cfg = APPLICATIONS[application_name]
        service_name = app_cfg["service_name"]
        require_service(service_name)
        logger.debug(
            "Fetching recent logs",
            extra={"extra_fields": {"service_name": service_name, "lines": lines}}
        )
        result = _run(["journalctl", "-u", service_name, "-n", str(lines), "--no-pager"])
        logger.debug(
            "Recent logs fetched",
            extra={"extra_fields": {"service": service_name}}
        )
        return {"service": service_name, "logs": result}
    except Exception:
        logger.error("Error fetching service logs", exc_info=True)
        raise

def get_all_services_status_on_server() -> dict:
    """List all systemd services on the server"""
    logger.info("Listing running services")
    try:
        result = _run(["systemctl", "list-units", "--type=service", "--no-pager"])
        logger.debug("Running services fetched")
        return {"running services": result["stdout"]}
    except Exception:
        logger.error("Error fetching running services", exc_info=True)
        raise

def get_server_health_summary() -> dict:
    """Fetch server health summary including CPU, memory, disk, load average"""
    logger.info("Fetching server health summary")
    try:
        load_result = _run(["uptime"])
        mem_result = _run(["free", "-h"])
        disk_result = _run(["df", "-h"])
        cpu_result = _run(["vmstat", "1", "2"])

        return {
            "load_average": load_result["stdout"],
            "memory": mem_result["stdout"],
            "disk": disk_result["stdout"],
            "cpu": cpu_result["stdout"]
        }
    except Exception:
        logger.error("Error fetching server health summary", exc_info=True)
        raise
