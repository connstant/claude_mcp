#!/usr/bin/env python
"""Enhanced MCP Server with dual transport support (HTTP and stdio).
Supports both remote API access and Claude Desktop integration.
"""
import asyncio
import logging
import platform
import sys
import threading
from typing import List, Optional

from fastapi import FastAPI, Request, Security, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mcp.server.fastmcp import FastMCP
import uvicorn

# Import all tools
from tools.weather import get_forecast, get_alerts
from tools.calendar import create_event, delete_event, list_events, find_and_delete_event, update_event, find_and_update_event
from tools.calendar.smart_create_event import smart_create_event
from tools.contacts.search_person import search_person
from tools.contacts.select_contact import select_contact
from tools.contacts.add_name_alias import add_name_alias
from tools.contacts.add_contact import add_contact
from tools.time import get_current_time, get_current_date, get_timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import json

# Define the port and API token for HTTP transport
PORT = 6921  # Default port, can be changed via command line
API_TOKEN = os.environ.get("MCP_API_TOKEN", "ROCKY_MCP_TOKEN_2025")  # Get from env var with fallback

# Define security scheme for Swagger UI
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verify the authorization token.
    This function is used by FastAPI to show the Authorize button in Swagger UI.
    The actual authentication is handled by the middleware.
    """
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authorization token")
    return credentials.credentials


class AuthMiddleware(BaseHTTPMiddleware):
    """Simple Middleware to authenticate API requests using token from headers."""

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for root path, health endpoint, documentation, and RPC endpoint (handled by dependency)
        path = request.url.path
        if path == "/" or path.startswith("/health") or path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json") or path.startswith("/rpc"):
            return await call_next(request)

        # Get token from header
        auth_header = request.headers.get("Authorization", "")

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Missing or invalid authorization token")
            return JSONResponse(
                {"detail": "Invalid or missing authorization token"},
                status_code=401,
            )

        token = auth_header.replace("Bearer ", "")
        if token != API_TOKEN:
            logger.warning("Invalid authorization token")
            return JSONResponse(
                {"detail": "Invalid authorization token"},
                status_code=401,
            )
        logger.info("Authorization token is valid")
        # Token is valid, proceed with the request
        return await call_next(request)


def create_mcp_server():
    """Factory function to create MCP server with all tools."""
    mcp = FastMCP("MCP Server")

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
        
    # Time tools
    @mcp.tool()
    async def current_time() -> str:
        """Get the current date and time."""
        return get_current_time()

    @mcp.tool()
    async def current_date() -> str:
        """Get the current date."""
        return get_current_date()

    @mcp.tool()
    async def current_timezone() -> str:
        """Get the current timezone."""
        return get_timezone()

    @mcp.tool()
    async def find_and_update_calendar_event(title: str = None, description: str = None, start_date: str = None, 
                                           new_title: str = None, new_start_time: str = None, new_end_time: str = None, 
                                           new_description: str = None, new_location: str = None,
                                           add_attendees: list = None, remove_attendees: list = None) -> dict:
        """Find and update a calendar event based on search criteria, with support for location and attendees management."""
        return await find_and_update_event(title, description, start_date, new_title, new_start_time, new_end_time, 
                                          new_description, new_location, add_attendees, remove_attendees)

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


    # Contact tools
    @mcp.tool()
    async def search_contact(name: str) -> list:
        """Search for a contact by name."""
        return await search_person(name)
        
    @mcp.tool()
    async def select_contact_from_results(contact_id: int, search_results: dict) -> dict:
        """Select a specific contact from previous search results by ID."""
        return await select_contact(contact_id, search_results)
        
    @mcp.tool()
    async def create_name_alias(alias: str, email: str) -> dict:
        """Create a name alias for quick reference (e.g., 'my manager' -> 'manager@company.com')."""
        return await add_name_alias(alias, email)
        
    @mcp.tool()
    async def add_new_contact(name: str, email: str) -> dict:
        """Add a new fallback contact with the given name and email."""
        return await add_contact(name, email)
        
    @mcp.tool()
    async def list_name_aliases() -> dict:
        """List all currently defined name aliases and their corresponding email addresses."""
        from tools.contacts import list_name_aliases
        return await list_name_aliases()

    @mcp.tool()
    async def list_contacts() -> dict:
        """List all available contacts from both directory and fallback sources."""
        from tools.contacts import list_contacts as get_contacts
        return await get_contacts()

    @mcp.tool()
    async def edit_contact(contact_id: int, new_name: str = None, new_email: str = None) -> dict:
        """Edit an existing fallback contact by ID."""
        from tools.contacts import edit_contact as edit_fallback_contact
        return await edit_fallback_contact(contact_id, new_name, new_email)
        
    @mcp.tool()
    async def delete_contact(contact_id: int) -> dict:
        """Delete a fallback contact by ID."""
        from tools.contacts import delete_contact as delete_fallback_contact
        return await delete_fallback_contact(contact_id)

    # Smart calendar tools
    @mcp.tool()
    async def smart_add_calendar_event(summary: str, start_time: str, end_time: str, 
                                    description: str = "", location: str = None, 
                                    attendee_names: list = None) -> dict:
        """
        Create a calendar event with smart name resolution for attendees.
        
        Instead of requiring email addresses, you can provide names that will be resolved to emails.
        Any names that cannot be automatically resolved will be returned as unresolved_attendees.
        """
        return await smart_create_event(summary, start_time, end_time, description, location, attendee_names)

    # Example tools from simple-mcp-server
    @mcp.tool()
    async def hello_world(name: str = "World", delay: int = 0) -> dict:
        """A simple hello world tool that returns a greeting.

        Args:
            name: Name to greet
            delay: Optional delay in seconds

        Returns:
            A greeting message
        """
        logger.info(f"hello_world called with name={name}, delay={delay}")
        if delay > 0:
            await asyncio.sleep(delay)
        return {"message": f"Hello, {name}!"}

    @mcp.tool()
    def get_version() -> dict:
        """Get server version information."""
        logger.info("get_version called")
        return {"version": "1.0.0", "name": "MCP Server", "api_version": "FastMCP 2.5.1"}

    @mcp.tool()
    def system_info() -> dict:
        """Get basic system information."""
        logger.info("system_info called")
        return {
            "python_version": platform.python_version(),
            "system": platform.system(),
            "platform": platform.platform(),
            "mcp_version": "1.0.0",
        }

    return mcp


def run_http_server(port=PORT):
    """Run HTTP server in a separate thread."""
    mcp_http = create_mcp_server()
    logger.info(f"Starting HTTP server on port {port}")
    
    # Create FastAPI app with metadata for documentation
    app = FastAPI(
        title="MCP Server API",
        description="MCP Server with HTTP API for calendar, weather, contacts, and time tools",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Add authentication middleware
    app.add_middleware(AuthMiddleware)
    
    # Create a root path handler
    @app.get("/",
             summary="API Root",
             description="Root path of the API",
             tags=["System"])
    async def root():
        """Returns basic information about the MCP Server API.
        
        This endpoint is not authenticated and provides links to documentation.
        
        Returns:
            dict: A JSON object with basic API information
        """
        return {
            "name": "MCP Server API",
            "version": "1.0.0",
            "description": "MCP Server with HTTP API for calendar, weather, contacts, and time tools",
            "documentation": "/docs",
            "health": "/health"
        }
    
    # Create a health check endpoint
    @app.get("/health", 
             summary="Health Check",
             description="Check if the MCP Server is running properly",
             tags=["System"])
    async def health_check():
        """Returns the health status of the MCP Server.
        
        This endpoint is not authenticated and can be used for monitoring.
        
        Returns:
            dict: A JSON object with status and message fields
        """
        return {"status": "ok", "message": "MCP Server is running"}
    
    # Create an authenticated JSON-RPC endpoint
    @app.post("/rpc",
              summary="JSON-RPC API Endpoint",
              description="Main API endpoint for MCP Server JSON-RPC requests",
              tags=["API"])
    async def rpc_endpoint(request: Request, token: str = Depends(verify_token)):
        """Handle JSON-RPC requests for the MCP Server.
        
        This endpoint requires authentication via Bearer token in the Authorization header.
        Supports standard JSON-RPC 2.0 format with method, params, and id fields.
        
        Available methods:
        - get_version: Returns the MCP Server version information
        - list_tools: Returns a list of available tools
        
        Calendar Tools:
        - create_calendar_event: Create a new calendar event
        - update_calendar_event: Update an existing calendar event
        - delete_calendar_event: Delete a calendar event by ID
        - find_and_update_calendar_event: Find and update events by criteria
        - find_and_delete_calendar_event: Find and delete events by criteria
        - list_calendar_events: List upcoming calendar events
        - smart_create_calendar_event: Create event with attendee name resolution
        
        Contact Tools:
        - search_person: Search for a person in the directory
        - select_contact: Select a contact from search results
        - add_name_alias: Add a personal alias for a contact
        - add_contact: Add a new contact to the fallback contacts
        
        Time Tools:
        - current_time: Get the current date and time
        - current_date: Get the current date
        - current_timezone: Get the current timezone information
        
        Weather Tools:
        - get_weather_forecast: Get weather forecast for a location
        - get_weather_alerts: Get weather alerts for a location
        
        Args:
            request (Request): The incoming HTTP request with JSON-RPC payload
            
        Returns:
            JSONResponse: A JSON-RPC 2.0 formatted response
        """
        
        # Authentication already handled by middleware
        # Process the JSON-RPC request
        body = await request.body()
        # Convert the body to a string if it's bytes
        if isinstance(body, bytes):
            body_str = body.decode('utf-8')
        else:
            body_str = body
            
        # Parse the JSON-RPC request
        try:
            data = json.loads(body_str)
            method = data.get('method')
            params = data.get('params', {})
            request_id = data.get('id')
            
            # Call the appropriate MCP method
            if method == 'get_version':
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "version": "1.0.0",
                        "name": "MCP Server"
                    }
                })
            elif method == 'list_tools':
                tools = await mcp_http.list_tools()
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": tools
                })
            else:
                # For other methods, we'll need to implement them
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
                    }
                })
        except Exception as e:
            logger.error(f"Error processing JSON-RPC request: {e}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }, status_code=400)
    
    # Run the FastAPI app with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)


def run_stdio_server():
    """Run stdio server in main thread."""
    mcp_stdio = create_mcp_server()
    logger.info("Starting stdio server")
    mcp_stdio.run(transport="stdio")


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server with dual transport support")
    parser.add_argument("--http-only", action="store_true", help="Run with HTTP transport only")
    parser.add_argument("--stdio-only", action="store_true", help="Run with stdio transport only")
    parser.add_argument("--port", type=int, default=PORT, help=f"HTTP port (default: {PORT})")
    args = parser.parse_args()
    
    if args.http_only:
        # HTTP only
        logger.info("Starting MCP Server with HTTP transport only")
        run_http_server(port=args.port)
    elif args.stdio_only:
        # Stdio only
        logger.info("Starting MCP Server with stdio transport only")
        run_stdio_server()
    else:
        # BOTH simultaneously
        logger.info("Starting MCP Server with BOTH transports")

        # Start HTTP server in background thread
        http_thread = threading.Thread(target=lambda: run_http_server(port=args.port), daemon=True)
        http_thread.start()

        # Run stdio in main thread
        run_stdio_server()
