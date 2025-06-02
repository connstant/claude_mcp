"""
Authentication utilities for Google APIs.
"""

import os
import json
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Path to save token
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "../../secrets/token.pickle")

# Path to client secrets file
CLIENT_SECRETS_PATH = os.path.join(os.path.dirname(__file__), "../../secrets/google-directory.json")

def get_credentials(scopes):
    """
    Get OAuth credentials for Google APIs.
    
    Args:
        scopes: List of OAuth scopes to request
        
    Returns:
        Google OAuth credentials or None if authentication fails
    """
    creds = None
    
    # Try to load credentials from token file
    if os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            print(f"Error loading token from {TOKEN_PATH}: {e}")
    
    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None
        
        # If still no valid credentials, need to authenticate
        if not creds:
            try:
                if os.path.exists(CLIENT_SECRETS_PATH):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CLIENT_SECRETS_PATH, scopes)
                    creds = flow.run_local_server(port=0)
                else:
                    print(f"Client secrets file not found at {CLIENT_SECRETS_PATH}")
                    return None
            except Exception as e:
                print(f"Error during authentication flow: {e}")
                return None
        
        # Save the credentials for the next run
        try:
            os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
        except Exception as e:
            print(f"Error saving token to {TOKEN_PATH}: {e}")
    
    return creds
