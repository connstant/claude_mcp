from mcp.server.fastmcp import FastMCP as MCP
from tools.weather import get_forecast, get_alerts
from tools.calendar import create_event, delete_event, list_events, find_and_delete_event, update_event, find_and_update_event
from tools.time_tools import get_current_time, get_current_date, get_timezone
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

# Calendar tools
@mcp.tool()
async def add_calendar_event(summary: str, start_time: str, end_time: str, description: str = "", location: str = None, attendees: list = None) -> dict:
    """Create a new Google Calendar event with optional location and attendees."""
    return await create_event(summary, start_time, end_time, description, location, attendees)

@mcp.tool()
async def delete_calendar_event(event_id: str) -> dict:
    """Delete a Google Calendar event by its ID."""
    return await delete_event(event_id)

@mcp.tool()
async def list_calendar_events(max_results: int = 10, search_query: str = None, time_min: str = None, time_max: str = None) -> dict:
    """List calendar events with optional filtering."""
    return await list_events(max_results, search_query, time_min, time_max)

@mcp.tool()
async def find_and_delete_calendar_event(title: str = None, description: str = None, start_date: str = None) -> dict:
    """Find and delete a calendar event based on search criteria (title, description, date)."""
    return await find_and_delete_event(title, description, start_date)

@mcp.tool()
async def update_calendar_event(event_id: str, title: str = None, start_time: str = None, end_time: str = None, 
                             description: str = None, location: str = None, add_attendees: list = None, remove_attendees: list = None) -> dict:
    """Update an existing calendar event by its ID, with support for location and attendees management."""
    return await update_event(event_id, title, start_time, end_time, description, location, add_attendees, remove_attendees)

@mcp.tool()
async def find_and_update_calendar_event(title: str = None, description: str = None, start_date: str = None, 
                                       new_title: str = None, new_start_time: str = None, new_end_time: str = None, 
                                       new_description: str = None, new_location: str = None,
                                       add_attendees: list = None, remove_attendees: list = None) -> dict:
    """Find and update a calendar event based on search criteria, with support for location and attendees management."""
    return await find_and_update_event(title, description, start_date, new_title, new_start_time, new_end_time, 
                                     new_description, new_location, add_attendees, remove_attendees)

# Time tools
@mcp.tool()
def current_time() -> str:
    """Get the current date and time."""
    return get_current_time()

@mcp.tool()
def current_date() -> str:
    """Get the current date."""
    return get_current_date()

@mcp.tool()
def current_timezone() -> str:
    """Get the current timezone."""
    return get_timezone()

if __name__ == "__main__":
    try:
        print("Starting MCP server...", file=sys.stderr)
        mcp.run()
    except Exception as e:
        print("Startup error:", e, file=sys.stderr)
        raise
