import os
import json
import datetime
import zoneinfo
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CREDS_PATH = os.path.join(os.path.dirname(__file__), "../secrets/google-calendar.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "../secrets/token.json")
SCOPES = ['https://www.googleapis.com/auth/calendar']

async def send_create_event_request(title: str, start_time: str, end_time: str, description: str = "") -> dict:
    """
    Sends a request to Google Calendar to create a new event.
    """
    # Check if we already have valid credentials stored
    creds = None
    if os.path.exists(TOKEN_PATH):
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            
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
    service = build('calendar', 'v3', credentials=creds)

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
