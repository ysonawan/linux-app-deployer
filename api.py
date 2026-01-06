"""
FastAPI server that exposes MCP tools as REST API endpoints.
This allows tools to be accessed via HTTP for UI integration.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import os
from logging_config import get_logger

from tools.tools_api import (
    get_app_deployment_configuration,
    checkout_repository,
    build_application,
    verify_artifact,
    deploy_artifact,
    restart_application,
    get_application_status,
    get_recent_logs,
)
from api_config import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    ENABLE_CORS,
    CORS_ORIGINS,
    CORS_CREDENTIALS,
    CORS_METHODS,
    CORS_HEADERS,
)

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Add CORS middleware for UI integration
if ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_CREDENTIALS,
        allow_methods=CORS_METHODS,
        allow_headers=CORS_HEADERS,
    )


# ========================
# Health & Info Endpoints
# ========================
@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "healthy"}


# ========================
# Configuration Endpoints
# ========================
@app.get("/api/v1/configuration")
async def get_deployment_configuration() -> Dict[str, Any]:
    """
    Get application deployment configuration and available applications.
    """
    try:
        logger.info("Deployment configuration requested")
        config = get_app_deployment_configuration()
        return {"success": True, "data": config}
    except Exception as e:
        logger.error("Error fetching deployment configuration", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# Repository Operations
# ========================
@app.post("/api/v1/repository/checkout/{application_name}")
async def checkout_repo(application_name: str) -> Dict[str, Any]:
    """
    Clone or update repository for the specified application.

    Args:
        application_name: Name of the application
    """
    try:
        logger.info(f"Repository checkout requested for {application_name}")
        result = checkout_repository(application_name)
        return {"success": result.get("success"), "data": result}
    except ValueError as e:
        logger.warning(f"Invalid application: {application_name}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.error("Error checking out repository", exc_info=True)
        raise HTTPException(status_code=500, detail="Error checking out repository")


# ========================
# Build Operations
# ========================
@app.post("/api/v1/build/application/{application_name}")
async def build_app(application_name: str) -> Dict[str, Any]:
    """
    Build application using predefined build system.

    Args:
        application_name: Name of the application to build
    """
    try:
        logger.info(f"Application build requested for {application_name}")
        result = build_application(application_name)
        return {"success": result.get("success"), "data": result}
    except ValueError as e:
        logger.warning(f"Invalid application: {application_name}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.error("Error building application", exc_info=True)
        raise HTTPException(status_code=500, detail="Error building application")


@app.post("/api/v1/artifact/verify/{application_name}")
async def verify_app_artifact(application_name: str) -> Dict[str, Any]:
    """
    Verify build artifact exists and is non-empty.

    Args:
        application_name: Name of the application
    """
    try:
        logger.info(f"Artifact verification requested for {application_name}")
        result = verify_artifact(application_name)
        return {"success": result.get("success"), "data": result}
    except ValueError as e:
        logger.warning(f"Invalid application: {application_name}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.error("Error verifying artifact", exc_info=True)
        raise HTTPException(status_code=500, detail="Error verifying artifact")


# ========================
# Deployment Operations
# ========================
@app.post("/api/v1/deployment/deploy/{application_name}")
async def deploy_app(application_name: str) -> Dict[str, Any]:
    """
    Deploy artifact to deployment directory with backup.

    Args:
        application_name: Name of the application to deploy
    """
    try:
        logger.info(f"Deployment requested for {application_name}")
        result = deploy_artifact(application_name)
        return {"success": result.get("success"), "data": result}
    except ValueError as e:
        logger.warning(f"Invalid application or artifact: {application_name}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.error("Error deploying artifact", exc_info=True)
        raise HTTPException(status_code=500, detail="Error deploying artifact")


@app.post("/api/v1/application/restart/{application_name}")
async def restart_app(application_name: str) -> Dict[str, Any]:
    """
    Restart systemd service for the application.

    Args:
        application_name: Name of the application to restart
    """
    try:
        logger.info(f"Application restart requested for {application_name}")
        result = restart_application(application_name)
        return {"success": result.get("success"), "data": result}
    except ValueError as e:
        logger.warning(f"Invalid application or service: {application_name}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.error("Error restarting application", exc_info=True)
        raise HTTPException(status_code=500, detail="Error restarting application")


# ========================
# Status & Monitoring
# ========================
@app.get("/api/v1/application/status/{application_name}")
async def get_app_status(application_name: str) -> Dict[str, Any]:
    """
    Get systemd service status for the application.

    Args:
        application_name: Name of the application
    """
    try:
        logger.info(f"Application status requested for {application_name}")
        result = get_application_status(application_name)
        return {"success": True, "data": result}
    except ValueError as e:
        logger.warning(f"Invalid application: {application_name}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.error("Error fetching application status", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching application status")


@app.get("/api/v1/application/logs/{application_name}")
async def get_app_logs(
    application_name: str,
    lines: int = Query(100, ge=1, le=10000)
) -> Dict[str, Any]:
    """
    Fetch recent logs for the application service.

    Args:
        application_name: Name of the application
        lines: Number of log lines to retrieve (1-10000, default: 100)
    """
    try:
        logger.info(f"Recent logs requested for {application_name} ({lines} lines)")
        result = get_recent_logs(application_name, lines)
        return {"success": True, "data": result}
    except ValueError as e:
        logger.warning(f"Invalid application: {application_name}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.error("Error fetching application logs", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching application logs")


# ========================
# Workflow Endpoints
# ========================
@app.post("/api/v1/deployment/workflow/full-deploy/{application_name}")
async def full_deployment_workflow(application_name: str) -> Dict[str, Any]:
    """
    Execute full deployment workflow for an application.
    Steps: checkout → build → verify → deploy → restart → status

    Args:
        application_name: Name of the application to deploy
    """
    try:
        logger.info(f"Full deployment workflow started for {application_name}")
        application_name = application_name

        workflow_results = {
            "application": application_name,
            "workflow": "full-deploy",
            "steps": {}
        }

        # Step 1: Checkout
        try:
            logger.info("Workflow step 1/6: Checkout repository")
            workflow_results["steps"]["checkout"] = checkout_repository(application_name)
            if not workflow_results["steps"]["checkout"].get("success"):
                workflow_results["status"] = "failed"
                workflow_results["failed_step"] = "checkout"
                return {"success": False, "data": workflow_results}
        except Exception as e:
            logger.error("Workflow step 1 failed: checkout", exc_info=True)
            workflow_results["steps"]["checkout"] = {"error": str(e)}
            workflow_results["status"] = "failed"
            workflow_results["failed_step"] = "checkout"
            return {"success": False, "data": workflow_results}

        # Step 2: Build
        try:
            logger.info("Workflow step 2/6: Build application")
            workflow_results["steps"]["build"] = build_application(application_name)
            if not workflow_results["steps"]["build"].get("success"):
                workflow_results["status"] = "failed"
                workflow_results["failed_step"] = "build"
                return {"success": False, "data": workflow_results}
        except Exception as e:
            logger.error("Workflow step 2 failed: build", exc_info=True)
            workflow_results["steps"]["build"] = {"error": str(e)}
            workflow_results["status"] = "failed"
            workflow_results["failed_step"] = "build"
            return {"success": False, "data": workflow_results}

        # Step 3: Verify
        try:
            logger.info("Workflow step 3/6: Verify artifact")
            workflow_results["steps"]["verify"] = verify_artifact(application_name)
            if not workflow_results["steps"]["verify"].get("success"):
                workflow_results["status"] = "failed"
                workflow_results["failed_step"] = "verify"
                return {"success": False, "data": workflow_results}
        except Exception as e:
            logger.error("Workflow step 3 failed: verify", exc_info=True)
            workflow_results["steps"]["verify"] = {"error": str(e)}
            workflow_results["status"] = "failed"
            workflow_results["failed_step"] = "verify"
            return {"success": False, "data": workflow_results}

        # Step 4: Deploy
        try:
            logger.info("Workflow step 4/6: Deploy artifact")
            workflow_results["steps"]["deploy"] = deploy_artifact(application_name)
            if not workflow_results["steps"]["deploy"].get("success"):
                workflow_results["status"] = "failed"
                workflow_results["failed_step"] = "deploy"
                return {"success": False, "data": workflow_results}
        except Exception as e:
            logger.error("Workflow step 4 failed: deploy", exc_info=True)
            workflow_results["steps"]["deploy"] = {"error": str(e)}
            workflow_results["status"] = "failed"
            workflow_results["failed_step"] = "deploy"
            return {"success": False, "data": workflow_results}

        # Step 5: Restart
        try:
            logger.info("Workflow step 5/6: Restart application")
            workflow_results["steps"]["restart"] = restart_application(application_name)
            if not workflow_results["steps"]["restart"].get("success"):
                workflow_results["status"] = "failed"
                workflow_results["failed_step"] = "restart"
                return {"success": False, "data": workflow_results}
        except Exception as e:
            logger.error("Workflow step 5 failed: restart", exc_info=True)
            workflow_results["steps"]["restart"] = {"error": str(e)}
            workflow_results["status"] = "failed"
            workflow_results["failed_step"] = "restart"
            return {"success": False, "data": workflow_results}

        # Step 6: Status
        try:
            logger.info("Workflow step 6/6: Get application status")
            workflow_results["steps"]["status"] = get_application_status(application_name)
        except Exception as e:
            logger.error("Workflow step 6 failed: status", exc_info=True)
            workflow_results["steps"]["status"] = {"error": str(e)}

        workflow_results["status"] = "completed"
        logger.info(f"Full deployment workflow completed successfully for {application_name}")
        return {"success": True, "data": workflow_results}

    except Exception:
        logger.error("Unexpected error in deployment workflow", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error in deployment workflow")


# ========================
# Root endpoint
# ========================
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with API information"""
    return {
        "service": "Linux App Deployer API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn

    api_port = int(os.getenv("API_PORT", 8002))
    api_host = os.getenv("API_HOST", "127.0.0.1")
    logger.info(f"Starting FastAPI server on {api_host}:{api_port}")

    uvicorn.run(
        app,
        host=api_host,
        port=api_port,
        log_config=None  # Use our custom logging
    )

