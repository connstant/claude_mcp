from mcp.server.fastmcp import FastMCP
from tools import weather

# Initialize FastMCP server
mcp = FastMCP("claude_mcp")

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state."""
    return await weather.get_alerts(state)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location."""
    return await weather.get_forecast(latitude, longitude)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")