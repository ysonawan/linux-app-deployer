import shutil
import psutil

from config import APPLICATIONS
from logging_config import get_logger

logger = get_logger(__name__)

def setup_resources(mcp):
    @mcp.resource("resource://system-health")
    def system_health() -> dict:
        """Provides a system health information."""
        try:
            disk = shutil.disk_usage("/")._asdict()
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()._asdict()
            logger.debug("System health check completed")

            return {"disk": disk, "cpu_percent": cpu, "memory": memory}
        except Exception:
            logger.error("Error checking system health", exc_info=True)
            raise

    @mcp.resource("resource://deployment-config")
    def deployment_config() -> dict:
        """Provides a application deployment configuration."""
        logger.debug("Retrieving deployment configuration")
        return {"applications": APPLICATIONS}
