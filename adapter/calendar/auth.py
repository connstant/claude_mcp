"""
Authentication utilities for Google Calendar API.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Calendar API requires specific scope
CREDS_PATH = os.path.join(os.path.dirname(__file__), "../../secrets/google-calendar.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "../../secrets/token.json")
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
    
    # Build and return the service object
    service = build('calendar', 'v3', credentials=creds)
    return service
