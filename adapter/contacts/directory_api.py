"""
Google Directory API adapter for contact management.
"""

import os
import json
from googleapiclient.discovery import build
from ..common.auth import get_credentials

# If modifying these scopes, delete the token.pickle file
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user.readonly']

def get_directory_service():
    """
    Get an authenticated Google Directory API service.
    
    Returns:
        Directory API service or None if authentication fails
    """
    creds = get_credentials(SCOPES)
    if not creds:
        return None
    
    try:
        service = build('admin', 'directory_v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building directory service: {e}")
        return None

async def lookup_contact_in_directory(query):
    """
    Look up a contact in the Google Directory.
    
    Args:
        query: The search query (name or email)
        
    Returns:
        Dictionary with contact information or None if not found
    """
    try:
        # Get the directory service
        service = get_directory_service()
        if not service:
            return None
        
        # Try to find the user by email first
        try:
            user = service.users().get(userKey=query).execute()
            name = user.get('name', {}).get('fullName', 'Unknown')
            email = user.get('primaryEmail', '')
            
            if email:
                return {
                    "name": name,
                    "email": email,
                    "source": "directory"
                }
        except Exception:
            # Not found by email, try search
            pass
        
        # Search for the user by name
        results = service.users().list(
            customer='my_customer',
            query=f"name:{query}* OR email:{query}*",
            maxResults=1
        ).execute()
        
        users = results.get('users', [])
        
        if users:
            user = users[0]
            name = user.get('name', {}).get('fullName', 'Unknown')
            email = user.get('primaryEmail', '')
            
            if email:
                return {
                    "name": name,
                    "email": email,
                    "source": "directory"
                }
    
    except Exception as e:
        print(f"Error looking up contact in directory: {e}")
    
    return None

async def list_directory_contacts():
    """
    List all contacts from the Google Directory.
    
    Returns:
        List of contacts from the directory
    """
    directory_contacts = []
    
    try:
        # Get the directory service
        service = get_directory_service()
        if service:
            # Search for all users in the domain
            results = service.users().list(
                customer='my_customer',
                maxResults=100,
                orderBy='email'
            ).execute()
            
            users = results.get('users', [])
            
            # Process each user
            for user in users:
                name = user.get('name', {}).get('fullName', 'Unknown')
                email = user.get('primaryEmail', '')
                
                if email:  # Only include users with email addresses
                    directory_contacts.append({
                        "name": name,
                        "email": email,
                        "source": "directory"
                    })
    except Exception as e:
        print(f"Error fetching directory contacts: {e}")
    
    return directory_contacts
