# =========================================================================
# DEPRECATED: This file is being phased out in favor of the modular structure.
# Please use the following modules instead:
# - adapter.calendar.auth - For Calendar authentication and service creation
# - adapter.calendar.events - For event creation, updating, and deletion
# - adapter.calendar.queries - For listing and searching calendar events
# =========================================================================

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

async def send_create_event_request(title: str, start_time: str, end_time: str, description: str = "", location: str = None, attendees: list = None) -> dict:
    """
    Sends a request to Google Calendar to create a new event.
    
    Args:
        title: Event title/summary
        start_time: Start time in ISO format
        end_time: End time in ISO format
        description: Event description (optional)
        location: Event location (optional)
        attendees: List of email addresses for attendees (optional)
        
    Returns:
        Dictionary with created event details
    """
    # Get the calendar service using our helper function
    service = get_calendar_service()

    # Use Eastern Time (EDT) explicitly since you mentioned events are 2 hours ahead
    # This assumes you're in Eastern Time Zone
    timezone_str = "America/New_York"
    print(f"[google_apis] Using timezone: {timezone_str}")
    
    # Create the base event object
    event = {
        'summary': title,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': timezone_str},
        'end': {'dateTime': end_time, 'timeZone': timezone_str},
    }
    
    # Add location if provided
    if location:
        event['location'] = location
    
    # Add attendees if provided
    if attendees and isinstance(attendees, list) and len(attendees) > 0:
        event['attendees'] = [{'email': email} for email in attendees]
        # Set guestsCanModify to True to allow attendees to modify the event
        event['guestsCanModify'] = True

    # Use sendUpdates='all' to send email notifications to all attendees
    created_event = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()

    # Prepare the response with basic event details
    response = {
        "event_id": created_event['id'],
        "summary": created_event['summary'],
        "start": created_event['start']['dateTime'],
        "end": created_event['end']['dateTime']
    }
    
    # Add location to response if it exists
    if 'location' in created_event:
        response['location'] = created_event['location']
    
    # Add attendees to response if they exist
    if 'attendees' in created_event:
        response['attendees'] = [attendee.get('email') for attendee in created_event['attendees']]
    
    return response

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

async def send_update_event_request(event_id: str, title: str = None, start_time: str = None, end_time: str = None, description: str = None, location: str = None, add_attendees: list = None, remove_attendees: list = None) -> dict:
    """
    Sends a request to Google Calendar to update an existing event.
    
    Args:
        event_id: ID of the event to update
        title: New title for the event (optional)
        start_time: New start time for the event (optional)
        end_time: New end time for the event (optional)
        description: New description for the event (optional)
        location: New location for the event (optional)
        add_attendees: List of email addresses to add as attendees (optional)
        remove_attendees: List of email addresses to remove from attendees (optional)
        
    Returns:
        Dictionary with updated event details
    """
    # Get the calendar service using our helper function
    service = get_calendar_service()
    
    try:
        # First, get the current event to preserve any fields we're not updating
        current_event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Create an updated event object, starting with the current event
        updated_event = current_event
        
        # Update fields that were provided
        if title is not None:
            updated_event['summary'] = title
            
        if description is not None:
            updated_event['description'] = description
            
        # Update location if provided
        if location is not None:
            updated_event['location'] = location
            
        # Use Eastern Time (EDT) for consistency with event creation
        timezone_str = "America/New_York"
        
        if start_time is not None:
            updated_event['start'] = {'dateTime': start_time, 'timeZone': timezone_str}
            
        if end_time is not None:
            updated_event['end'] = {'dateTime': end_time, 'timeZone': timezone_str}
            
        # Handle attendees
        if add_attendees or remove_attendees:
            # Get current attendees or initialize empty list
            current_attendees = updated_event.get('attendees', [])
            current_emails = [attendee.get('email') for attendee in current_attendees]
            
            # Add new attendees
            if add_attendees and isinstance(add_attendees, list):
                for email in add_attendees:
                    if email not in current_emails:  # Avoid duplicates
                        current_attendees.append({'email': email})
            
            # Remove attendees
            if remove_attendees and isinstance(remove_attendees, list):
                current_attendees = [attendee for attendee in current_attendees 
                                  if attendee.get('email') not in remove_attendees]
            
            # Update the event with modified attendees list
            updated_event['attendees'] = current_attendees
            
            # Set guestsCanModify to True to allow attendees to modify the event
            updated_event['guestsCanModify'] = True
        
        # Send the update request with sendUpdates='all' to notify all attendees
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=updated_event,
            sendUpdates='all'
        ).execute()
        
        # Prepare the response with basic event details
        response = {
            "success": True,
            "message": f"Event '{updated_event['summary']}' updated successfully.",
            "event_id": updated_event['id'],
            "summary": updated_event['summary'],
            "start": updated_event['start']['dateTime'],
            "end": updated_event['end']['dateTime']
        }
        
        # Add location to response if it exists
        if 'location' in updated_event:
            response['location'] = updated_event['location']
        
        # Add attendees to response if they exist
        if 'attendees' in updated_event:
            response['attendees'] = [attendee.get('email') for attendee in updated_event['attendees']]
        
        return response
    except Exception as e:
        print(f"Error updating event: {e}")
        return {
            "success": False,
            "message": f"Failed to update event: {str(e)}"
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
