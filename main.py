from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b + b

if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8001)
