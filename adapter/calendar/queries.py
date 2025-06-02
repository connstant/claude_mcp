"""
Query utilities for Google Calendar API.
Handles listing and searching calendar events.
"""

import datetime
import zoneinfo
from adapter.calendar.auth import get_calendar_service

async def list_calendar_events(max_results: int = 10, search_query: str = None, 
                             time_min: str = None, time_max: str = None):
    """
    Lists calendar events with optional filtering.
    
    Args:
        max_results: Maximum number of events to return
        search_query: Text to search for in event summary/description
        time_min: Earliest time to include (ISO format)
        time_max: Latest time to include (ISO format)
    
    Returns:
        Dictionary with events and metadata
    """
    service = get_calendar_service()
    
    # Set up default time range if not specified
    if not time_min:
        # Default to now
        now = datetime.datetime.now(zoneinfo.ZoneInfo("UTC"))
        time_min = now.isoformat()
    
    if not time_max:
        # Default to 7 days from now
        if isinstance(time_min, str):
            try:
                time_min_dt = datetime.datetime.fromisoformat(time_min.replace('Z', '+00:00'))
                time_max_dt = time_min_dt + datetime.timedelta(days=7)
                time_max = time_max_dt.isoformat()
            except ValueError:
                # If we can't parse the time_min, just use 7 days from now
                time_max_dt = datetime.datetime.now(zoneinfo.ZoneInfo("UTC")) + datetime.timedelta(days=7)
                time_max = time_max_dt.isoformat()
        else:
            time_max_dt = datetime.datetime.now(zoneinfo.ZoneInfo("UTC")) + datetime.timedelta(days=7)
            time_max = time_max_dt.isoformat()
    
    # Build the query parameters
    params = {
        'calendarId': 'primary',
        'timeMin': time_min,
        'timeMax': time_max,
        'maxResults': max_results,
        'singleEvents': True,
        'orderBy': 'startTime'
    }
    
    # Add search query if provided
    if search_query:
        params['q'] = search_query
    
    try:
        # Call the Calendar API to list events
        events_result = service.events().list(**params).execute()
        events = events_result.get('items', [])
        
        # Format the response
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            formatted_event = {
                'id': event['id'],
                'summary': event.get('summary', 'No title'),
                'start': start,
                'end': end,
                'location': event.get('location', ''),
                'description': event.get('description', ''),
                'html_link': event.get('htmlLink', ''),
                'attendees': event.get('attendees', [])
            }
            
            formatted_events.append(formatted_event)
        
        return {
            'status': 'success',
            'message': f"Found {len(formatted_events)} events",
            'events': formatted_events,
            'count': len(formatted_events)
        }
    except Exception as e:
        print(f"Error listing events: {e}")
        return {
            'status': 'error',
            'message': f"Failed to list events: {str(e)}",
            'events': [],
            'count': 0
        }
