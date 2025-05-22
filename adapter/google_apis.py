import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CREDS_PATH = os.path.join(os.path.dirname(__file__), "../secrets/google-calendar.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "../secrets/token.json")
SCOPES = ['https://www.googleapis.com/auth/calendar']

async def send_create_event_request(title: str, start_time: str, end_time: str, description: str = "") -> dict:
    """
    Sends a request to Google Calendar to create a new event.
    """
    # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow steps
    flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
    
    # Run the OAuth flow to get credentials
    # This will open a browser window for authentication
    creds = flow.run_local_server(port=0)
    
    # Save the credentials for future use
    with open(TOKEN_PATH, 'w') as token:
        token.write(creds.to_json())
    
    # Build the service with the credentials
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': title,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_time, 'timeZone': 'America/New_York'},
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()

    return {
        "event_id": created_event['id'],
        "summary": created_event['summary'],
        "start": created_event['start']['dateTime'],
        "end": created_event['end']['dateTime']
    }
