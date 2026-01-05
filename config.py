from pathlib import Path

BASE_REPO_DIR = Path("/opt/mcp/repos")
BASE_DEPLOY_DIR = Path("/opt/app")

APPLICATIONS = {
    "famvest": {
        "git_url": "https://github.com/ysonawan/famvest.git",
        "branch": "main",
        "build_type": "maven",
        "artifact_path": "target/famvest-*.jar",
        "service_name": "famvest",
        "deploy_path": BASE_DEPLOY_DIR / "famvest"
    },
    "netly": {
        "git_url": "https://github.com/ysonawan/netly.git",
        "branch": "main",
        "build_type": "maven",
        "artifact_path": "target/netly-*.jar",
        "service_name": "netly",
        "deploy_path": BASE_DEPLOY_DIR / "netly"
    },
    "duebook": {
        "git_url": "https://github.com/ysonawan/duebook.git",
        "branch": "main",
        "build_type": "maven",
        "artifact_path": "target/duebook-*.jar",
        "service_name": "duebook",
        "deploy_path": BASE_DEPLOY_DIR / "duebook"
    }
}

ALLOWED_SERVICES = {"famvest", "netly", "duebook"}

BUILD_COMMANDS = {
    "maven": ["mvn", "clean", "package", "-DskipTests"]
}
