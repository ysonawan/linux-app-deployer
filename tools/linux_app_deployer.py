"""
MCP Tools setup module.
Uses the tools_api module for implementation to allow code sharing with FastAPI.
"""
from tools.tools_api import (
    get_app_deployment_configuration,
    checkout_repository,
    build_application,
    verify_artifact,
    deploy_artifact,
    restart_application,
    get_application_status,
    get_recent_logs,
    get_running_services,
    get_server_health_summary
)


# -------------------------
# MCP TOOLS SETUP
# -------------------------
def setup_tools(mcp):
    """Register all tools with the MCP server"""

    @mcp.tool()
    def get_app_deployment_configuration_tool() -> dict:
        """Get application deployment configuration."""
        return get_app_deployment_configuration()

    @mcp.tool()
    def checkout_repository_tool(application_name: str) -> dict:
        """Clone or update repository safely."""
        return checkout_repository(application_name)

    @mcp.tool()
    def build_application_tool(application_name: str) -> dict:
        """Build application using predefined build system."""
        return build_application(application_name)

    @mcp.tool()
    def verify_artifact_tool(application_name: str) -> dict:
        """Verify build artifact exists and is non-empty."""
        return verify_artifact(application_name)

    @mcp.tool()
    def deploy_artifact_tool(application_name: str) -> dict:
        """Copy artifact to deployment directory with backup."""
        return deploy_artifact(application_name)

    @mcp.tool()
    def restart_application_tool(application_name: str) -> dict:
        """Restart application using systemd service."""
        return restart_application(application_name)

    @mcp.tool()
    def stop_application_tool(application_name: str) -> dict:
        """Stop application using systemd service."""
        return stop_application_tool(application_name)

    @mcp.tool()
    def get_application_status_tool(application_name: str) -> dict:
        """Get application status using systemd service status."""
        return get_application_status(application_name)

    @mcp.tool()
    def get_recent_logs_tool(application_name: str, lines: int = 100) -> dict:
        """Fetch recent logs safely."""
        return get_recent_logs(application_name, lines)

    @mcp.tool()
    def get_running_services_tool() -> dict:
        """List running systemd services on the server"""
        return get_running_services()

    @mcp.tool()
    def get_server_health_summary_tool() -> dict:
        """Fetch server health summary including CPU, memory, disk, load average"""
        return get_server_health_summary()
