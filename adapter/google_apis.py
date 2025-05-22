import os
import json
import datetime
import zoneinfo
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

CREDS_PATH = os.path.join(os.path.dirname(__file__), "../secrets/google-calendar.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "../secrets/token.json")
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Helper function to handle authentication and return a Google Calendar service object.
    Handles token caching and OAuth flow.
    """
    # Check if we already have valid credentials stored
    creds = None
    if os.path.exists(TOKEN_PATH):
        try:
            print("Loading existing credentials from token file")
            with open(TOKEN_PATH, 'r') as token_file:
                token_data = json.load(token_file)
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            
            # Check if credentials are expired and refresh if possible
            if creds.expired and creds.refresh_token:
                print("Refreshing expired credentials")
                creds.refresh(Request())
                # Save the refreshed credentials
                with open(TOKEN_PATH, 'w') as token_file:
                    token_file.write(creds.to_json())
        except Exception as e:
            print(f"Error loading credentials: {e}")
            creds = None
    
    # If we don't have valid credentials, run the OAuth flow
    if not creds or not hasattr(creds, 'valid') or not creds.valid:
        print("No valid credentials found, running OAuth flow")
        # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow steps
        flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
        
        # Run the OAuth flow to get credentials
        # This will open a browser window for authentication
        creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
    
    # Build the service with the credentials
    return build('calendar', 'v3', credentials=creds)

async def send_create_event_request(title: str, start_time: str, end_time: str, description: str = "") -> dict:
    """
    Sends a request to Google Calendar to create a new event.
    """
    # Get the calendar service using our helper function
    service = get_calendar_service()

    # Use Eastern Time (EDT) explicitly since you mentioned events are 2 hours ahead
    # This assumes you're in Eastern Time Zone
    timezone_str = "America/New_York"
    print(f"[google_apis] Using timezone: {timezone_str}")
    
    event = {
        'summary': title,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': timezone_str},
        'end': {'dateTime': end_time, 'timeZone': timezone_str},
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()

    return {
        "event_id": created_event['id'],
        "summary": created_event['summary'],
        "start": created_event['start']['dateTime'],
        "end": created_event['end']['dateTime']
    }

async def send_delete_event_request(event_id: str) -> dict:
    """
    Sends a request to Google Calendar to delete an event.
    """
    # Get the calendar service using our helper function
    service = get_calendar_service()
    
    # Delete the event
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return {
            "success": True,
            "message": f"Event with ID {event_id} successfully deleted."
        }
    except Exception as e:
        print(f"Error deleting event: {e}")
        return {
            "success": False,
            "message": f"Failed to delete event: {str(e)}"
        }

async def list_calendar_events(max_results: int = 10, search_query: str = None, time_min: str = None, time_max: str = None) -> dict:
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
    # Get the calendar service using our helper function
    service = get_calendar_service()
    
    # Prepare parameters for the list request
    params = {
        'calendarId': 'primary',
        'maxResults': max_results,
        'singleEvents': True,
        'orderBy': 'startTime'
    }
    
    # Add optional time filters if provided
    if time_min:
        params['timeMin'] = time_min
    else:
        # Default to now if no time_min provided
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        params['timeMin'] = now
        
    if time_max:
        params['timeMax'] = time_max
        
    # Add search query if provided
    if search_query:
        params['q'] = search_query
    
    try:
        # Execute the events list request
        events_result = service.events().list(**params).execute()
        events = events_result.get('items', [])
        
        # Format the events for easier consumption
        formatted_events = []
        for event in events:
            formatted_event = {
                'id': event['id'],
                'summary': event.get('summary', 'No Title'),
                'description': event.get('description', ''),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date')),
                'link': event.get('htmlLink', '')
            }
            formatted_events.append(formatted_event)
            
        return {
            'success': True,
            'events': formatted_events,
            'count': len(formatted_events)
        }
        
    except Exception as e:
        print(f"Error listing events: {e}")
        return {
            'success': False,
            'message': f"Failed to list events: {str(e)}",
            'events': [],
            'count': 0
        }
