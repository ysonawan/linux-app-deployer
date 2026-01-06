from pathlib import Path

BASE_REPO_DIR = Path("/opt/repos")
BASE_DEPLOY_DIR = Path("/opt/app")

APPLICATIONS = {
    "famvest": {
        "git_url": "git@github.com/ysonawan/famvest.git",
        "branch": "main",
        "build_type": "maven",
        "artifact_path": "target/famvest-*.jar",
        "service_name": "famvest-app",
        "deploy_path": BASE_DEPLOY_DIR / "famvest",
        "symlink": "famvest.jar"
    },
    "netly": {
        "git_url": "git@github.com/ysonawan/netly.git",
        "branch": "main",
        "build_type": "maven",
        "artifact_path": "target/netly-*.jar",
        "service_name": "netly-app",
        "deploy_path": BASE_DEPLOY_DIR / "netly",
        "symlink": "netly.jar"
    },
    "duebook": {
        "git_url": "git@github.com/ysonawan/duebook.git",
        "branch": "main",
        "build_type": "maven",
        "artifact_path": "target/duebook-*.jar",
        "service_name": "duebook-app",
        "deploy_path": BASE_DEPLOY_DIR / "duebook",
        "symlink": "duebook.jar"
    }
}

ALLOWED_SERVICES = {"famvest-app", "netly-app", "duebook-app"}

BUILD_COMMANDS = {
    "maven": ["mvn", "clean", "package", "-DskipTests"]
}
