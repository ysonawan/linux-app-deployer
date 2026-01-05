from logging_config import setup_logging
from fastmcp import FastMCP

# Initialize logging before anything else
logger = setup_logging()
logger.info("Initializing MCP Server: linux-app-deployer")

mcp = FastMCP("linux-app-deployer", instructions="Linux deployment MCP server for controlled operations.")

from tools.linux_app_deployer import setup_tools
from resources.resources import setup_resources
from prompts.prompts import setup_prompts

# Register all components
setup_tools(mcp)
setup_resources(mcp)
setup_prompts(mcp)

if __name__ == "__main__":
    try:
        logger.info("Starting MCP server on port 8001 with streamable-http transport")
        mcp.run(transport="streamable-http", port=8001)
    except KeyboardInterrupt:
        logger.info("MCP server interrupted by user")
    except Exception as e:
        logger.critical("MCP server encountered a critical error", exc_info=True)
        raise
