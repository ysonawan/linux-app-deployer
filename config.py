from pathlib import Path

BASE_REPO_DIR = Path("/opt/mcp/repos")
BASE_DEPLOY_DIR = Path("/opt/app")

APPLICATIONS = {
    "famvest": {
        "git_url": "https://github.com/ysonawan/famvest.git",
        "build_type": "maven",
        "artifact_path": "target/famvest-app-*.jar",
        "service_name": "famvest-app",
        "deploy_path": BASE_DEPLOY_DIR / "famvest-app"
    },
    "netly": {
        "git_url": "https://github.com/ysonawan/netly.git",
        "build_type": "maven",
        "artifact_path": "target/netly-app-*.jar",
        "service_name": "netly-app",
        "deploy_path": BASE_DEPLOY_DIR / "netly-app"
    },
    "duebook": {
        "git_url": "https://github.com/ysonawan/duebook.git",
        "build_type": "maven",
        "artifact_path": "target/duebook-app-*.jar",
        "service_name": "duebook-app",
        "deploy_path": BASE_DEPLOY_DIR / "duebook-app"
    },
}

ALLOWED_SERVICES = {"famvest-app", "netly-app", "duebook-app"}

BUILD_COMMANDS = {
    "maven": ["mvn", "clean", "package", "-DskipTests"]
}
