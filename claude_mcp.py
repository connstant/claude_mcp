from mcp.server.fastmcp import FastMCP as MCP
from tools.weather import get_forecast, get_alerts
from tools.calendar_tools import create_event
import sys

# Initialize MCP instance
mcp = MCP()

# Weather tools
@mcp.tool()
async def get_weather_alerts(state: str) -> str:
    """Get weather alerts for a US state."""
    return await get_alerts(state)

@mcp.tool()
async def get_weather_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location."""
    return await get_forecast(latitude, longitude)

# Calendar tool
@mcp.tool()
async def add_event(summary: str, start_time: str, end_time: str, description: str = "") -> dict:
    """Create a new Google Calendar event."""
    return await create_event(summary, start_time, end_time, description)

if __name__ == "__main__":
    try:
        print("Starting MCP server...", file=sys.stderr)
        mcp.run()
    except Exception as e:
        print("Startup error:", e, file=sys.stderr)
        raise
