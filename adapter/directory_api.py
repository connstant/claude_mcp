# =========================================================================
# DEPRECATED: This file is being phased out in favor of the modular structure.
# Please use the following modules instead:
# - adapter.contacts.directory_api - For Google Directory API integration
# - adapter.contacts.fallback - For fallback contacts management
# - adapter.contacts.resolution - For contact resolution and name aliases
# - adapter.common.auth - For OAuth and token management
# =========================================================================

import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Try to import fuzzywuzzy, but provide fallback if not available
try:
    from fuzzywuzzy import fuzz, process
    FUZZY_MATCHING_AVAILABLE = True
except ImportError:
    print("Warning: fuzzywuzzy package not found. Fuzzy matching will be disabled.")
    FUZZY_MATCHING_AVAILABLE = False
    
    # Create dummy functions to prevent errors
    class DummyFuzz:
        @staticmethod
        def token_sort_ratio(a, b):
            return 100 if a.lower() == b.lower() else 0
    
    class DummyProcess:
        @staticmethod
        def extract(query, choices, scorer=None, limit=5):
            # Simple exact matching as fallback
            results = []
            for choice in choices:
                if query.lower() in choice.lower():
                    results.append((choice, 100))
            return results[:limit]
    
    fuzz = DummyFuzz()
    process = DummyProcess()

# Directory API requires additional scope
DIRECTORY_SCOPES = ['https://www.googleapis.com/auth/directory.readonly']
CREDS_PATH = os.path.join(os.path.dirname(__file__), "../secrets/google-directory.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "../secrets/directory-token.json")
ALIASES_PATH = os.path.join(os.path.dirname(__file__), "../secrets/name-aliases.json")

# Fallback contact list if Directory API is not available
FALLBACK_CONTACTS = [
    {"name": "John Smith", "email": "john.smith@example.com"},
    {"name": "Jane Doe", "email": "jane.doe@example.com"},
    {"name": "Bob Johnson", "email": "bob.johnson@example.com"},
    {"name": "Alice Williams", "email": "alice.williams@example.com"},
    {"name": "Charlie Brown", "email": "charlie.brown@example.com"},
    {"name": "David Miller", "email": "david.miller@example.com"},
    {"name": "Eva Davis", "email": "eva.davis@example.com"},
    {"name": "Frank Wilson", "email": "frank.wilson@example.com"},
    {"name": "Grace Taylor", "email": "grace.taylor@example.com"}
]

# Path to save fallback contacts
FALLBACK_CONTACTS_PATH = os.path.join(os.path.dirname(__file__), "../secrets/fallback-contacts.json")

# Function to ensure fallback contacts file exists and is properly initialized
def ensure_fallback_contacts_file():
    """
    Ensures that the fallback contacts file exists and is properly initialized.
    If the file doesn't exist, creates it with default contacts.
    If the file exists but is invalid, resets it with default contacts.
    
    Returns:
        bool: True if the file exists and is valid, False otherwise
    """
    global FALLBACK_CONTACTS
    
    try:
        # Ensure the secrets directory exists
        os.makedirs(os.path.dirname(FALLBACK_CONTACTS_PATH), exist_ok=True)
        
        if os.path.exists(FALLBACK_CONTACTS_PATH):
            # File exists, try to load it
            try:
                with open(FALLBACK_CONTACTS_PATH, 'r') as f:
                    loaded_contacts = json.load(f)
                    if isinstance(loaded_contacts, list):
                        FALLBACK_CONTACTS = loaded_contacts
                        print(f"Loaded {len(FALLBACK_CONTACTS)} fallback contacts from {FALLBACK_CONTACTS_PATH}")
                        return True
                    else:
                        print(f"Invalid format in {FALLBACK_CONTACTS_PATH}, using default contacts")
                        # File exists but has invalid format, reset it
                        with open(FALLBACK_CONTACTS_PATH, 'w') as f:
                            json.dump(FALLBACK_CONTACTS, f, indent=2)
                        print(f"Reset fallback contacts file with default contacts")
                        return True
            except Exception as e:
                print(f"Error loading fallback contacts from {FALLBACK_CONTACTS_PATH}: {e}")
                # File exists but has errors, reset it
                with open(FALLBACK_CONTACTS_PATH, 'w') as f:
                    json.dump(FALLBACK_CONTACTS, f, indent=2)
                print(f"Reset fallback contacts file with default contacts due to error")
                return True
        else:
            # File doesn't exist, create it
            with open(FALLBACK_CONTACTS_PATH, 'w') as f:
                json.dump(FALLBACK_CONTACTS, f, indent=2)
            print(f"Created new fallback contacts file with default contacts")
            return True
    except Exception as e:
        print(f"Error ensuring fallback contacts file: {e}")
        return False

# Initialize fallback contacts on module import
try:
    ensure_fallback_contacts_file()
except Exception as e:
    print(f"Error initializing fallback contacts: {e}")

# Function to save fallback contacts
def save_fallback_contacts():
    """
    Save the current fallback contacts to the JSON file in secrets directory.
    Creates the file if it doesn't exist.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure the secrets directory exists
        os.makedirs(os.path.dirname(FALLBACK_CONTACTS_PATH), exist_ok=True)
        
        with open(FALLBACK_CONTACTS_PATH, 'w') as f:
            json.dump(FALLBACK_CONTACTS, f, indent=2)
        print(f"Saved {len(FALLBACK_CONTACTS)} fallback contacts to {FALLBACK_CONTACTS_PATH}")
        return True
    except Exception as e:
        print(f"Error saving fallback contacts to {FALLBACK_CONTACTS_PATH}: {e}")
        # Try to recreate the file with current contacts
        try:
            os.makedirs(os.path.dirname(FALLBACK_CONTACTS_PATH), exist_ok=True)
            with open(FALLBACK_CONTACTS_PATH, 'w') as f:
                json.dump(FALLBACK_CONTACTS, f, indent=2)
            print(f"Successfully recreated fallback contacts file after error")
            return True
        except Exception as e2:
            print(f"Failed to recreate fallback contacts file: {e2}")
            return False

# In-memory cache for contacts and aliases
contact_cache = {}
name_aliases = {}

# Load aliases from file if it exists
def load_aliases():
    """
    Load name aliases from the JSON file in secrets directory.
    If the file doesn't exist, returns an empty dictionary.
    """
    global name_aliases
    try:
        if os.path.exists(ALIASES_PATH):
            with open(ALIASES_PATH, 'r') as f:
                name_aliases = json.load(f)
            print(f"Loaded {len(name_aliases)} name aliases from {ALIASES_PATH}")
        else:
            print(f"No aliases file found at {ALIASES_PATH}, starting with empty aliases")
            name_aliases = {}
    except Exception as e:
        print(f"Error loading aliases from {ALIASES_PATH}: {e}")
        name_aliases = {}

# Save aliases to file
def save_aliases():
    """
    Save the current name aliases to the JSON file in secrets directory.
    Creates the file if it doesn't exist.
    """
    try:
        # Ensure the secrets directory exists
        os.makedirs(os.path.dirname(ALIASES_PATH), exist_ok=True)
        
        with open(ALIASES_PATH, 'w') as f:
            json.dump(name_aliases, f, indent=2)
        print(f"Saved {len(name_aliases)} name aliases to {ALIASES_PATH}")
        return True
    except Exception as e:
        print(f"Error saving aliases to {ALIASES_PATH}: {e}")
        return False

# Load aliases at module import time
load_aliases()

# Fuzzy matching threshold (0-100, higher is more strict)
FUZZY_MATCH_THRESHOLD = 70

def get_directory_service():
    """
    Helper function to handle authentication and return a Google Directory service object.
    Handles token caching and OAuth flow.
    """
    # Check if we already have valid credentials stored
    creds = None
    if os.path.exists(TOKEN_PATH):
        try:
            print("Loading existing directory credentials from token file")
            with open(TOKEN_PATH, 'r') as token_file:
                token_data = json.load(token_file)
                creds = Credentials.from_authorized_user_info(token_data, DIRECTORY_SCOPES)
            
            # Check if credentials are expired and refresh if possible
            if creds.expired and creds.refresh_token:
                print("Refreshing expired directory credentials")
                creds.refresh(Request())
                # Save the refreshed credentials
                with open(TOKEN_PATH, 'w') as token_file:
                    token_file.write(creds.to_json())
        except Exception as e:
            print(f"Error loading directory credentials: {e}")
            creds = None
    
    # If we don't have valid credentials, run the OAuth flow
    if not creds or not hasattr(creds, 'valid') or not creds.valid:
        try:
            print("No valid directory credentials found, running OAuth flow")
            # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow steps
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, DIRECTORY_SCOPES)
            
            # Run the OAuth flow to get credentials - this will open a browser window for authentication
            creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(TOKEN_PATH, 'w') as token_file:
                token_file.write(creds.to_json())
        except Exception as e:
            print(f"Error running OAuth flow: {e}")
            return None
    
    # Build and return the service
    try:
        return build('admin', 'directory_v1', credentials=creds)
    except Exception as e:
        print(f"Error building directory service: {e}")
        return None

async def search_directory_contacts(name: str):
    """
    Search for contacts in Google Directory by name.
    Falls back to local contact list if Directory API is unavailable.
    
    Args:
        name: The name or partial name to search for
        
    Returns:
        List of matching contacts with name and email
    """
    # Check cache first for frequent contacts
    name_lower = name.lower()
    if name_lower in contact_cache:
        print(f"Returning cached results for '{name}'")
        return contact_cache[name_lower]
    
    try:
        # Try to use the Directory API
        service = get_directory_service()
        
        if service:
            print(f"Searching directory for '{name}'")
            
            # Query the Directory API for users matching the name
            # We'll search in both primary email and name fields
            query = f"name:'{name}*' OR email:'{name}*'"
            
            try:
                results = service.users().list(
                    customer='my_customer',  # 'my_customer' for the domain the service account belongs to
                    query=query,
                    orderBy='email',
                    projection='basic',  # Only get basic user info (name, email)
                    maxResults=10
                ).execute()
                
                users = results.get('users', [])
                
                if users:
                    # Format the results
                    contacts = []
                    user_names = []
                    
                    # First collect all users and their names for fuzzy matching
                    for user in users:
                        if 'name' in user and 'primaryEmail' in user:
                            full_name = user['name'].get('fullName', 'Unknown')
                            user_names.append(full_name)
                            contacts.append({
                                'name': full_name,
                                'email': user['primaryEmail'],
                                'source': 'directory'
                            })
                    
                    # Apply ranking to the results
                    if contacts:
                        scored_contacts = []
                        
                        if FUZZY_MATCHING_AVAILABLE:
                            # Use fuzzy matching if available
                            # Get fuzzy match scores for all contacts
                            fuzzy_scores = process.extract(name, user_names, scorer=fuzz.token_sort_ratio)
                            
                            # Add scores to contacts
                            for i, contact in enumerate(contacts):
                                # Find the score for this contact
                                for match_name, score in fuzzy_scores:
                                    if contact['name'] == match_name:
                                        scored_contact = contact.copy()
                                        scored_contact['score'] = score
                                        scored_contacts.append(scored_contact)
                                        break
                        else:
                            # Simple substring matching as fallback
                            for contact in contacts:
                                contact_name = contact['name'].lower()
                                name_lower = name.lower()
                                
                                # Assign scores based on match type
                                if contact_name == name_lower:
                                    # Exact match
                                    score = 100
                                elif name_lower in contact_name:
                                    # Substring match
                                    score = 85
                                elif contact_name in name_lower:
                                    # Reverse substring match
                                    score = 75
                                else:
                                    # Default score
                                    score = 50
                                
                                scored_contact = contact.copy()
                                scored_contact['score'] = score
                                scored_contacts.append(scored_contact)
                        
                        # Sort by score (highest first)
                        scored_contacts.sort(key=lambda x: x.get('score', 0), reverse=True)
                        
                        # Cache the results for future use
                        contact_cache[name_lower] = scored_contacts
                        return scored_contacts
                else:
                    print(f"No users found matching '{name}' in directory")
            except Exception as e:
                print(f"Error querying Directory API: {e}")
                # Continue to fallback contacts
        else:
            print("Directory API service unavailable, using fallback contacts")
    
    except Exception as e:
        print(f"Error searching directory: {e}")
    
    # Fallback to local contacts if Directory API search failed or returned no results
    print(f"Using fallback contacts for '{name}'")
    
    # Filter fallback contacts based on the search term
    name_lower = name.lower()
    matching_contacts = []
    
    # First check aliases
    if name_lower in name_aliases:
        email = name_aliases[name_lower]
        # Find the contact with this email if possible
        for contact in FALLBACK_CONTACTS:
            if contact["email"].lower() == email.lower():
                matching_contacts.append({
                    "name": contact["name"],
                    "email": contact["email"],
                    "source": "alias"
                })
                break
        # If not found in contacts but we have the email, create a contact
        if not matching_contacts:
            matching_contacts.append({
                "name": name,
                "email": email,
                "source": "alias"
            })
    
    # Then check fallback contacts
    if not matching_contacts:
        for contact in FALLBACK_CONTACTS:
            if (name_lower in contact["name"].lower() or 
                name_lower in contact["email"].lower()):
                matching_contacts.append({
                    "name": contact["name"],
                    "email": contact["email"],
                    "source": "fallback"
                })
    
    # If no exact matches, try fuzzy matching
    if not matching_contacts:
        fuzzy_matches = fuzzy_match_contacts(name, FALLBACK_CONTACTS)
        for match in fuzzy_matches:
            matching_contacts.append({
                "name": match["name"],
                "email": match["email"],
                "source": "fuzzy_fallback",
                "score": match["score"]
            })
    
    # Cache and return results
    if matching_contacts:
        contact_cache[name_lower] = matching_contacts
    
    return matching_contacts

def fuzzy_match_contacts(name, contact_list):
    """
    Use fuzzy string matching to find contacts that approximately match the search term.
    Falls back to simple substring matching if fuzzy matching is not available.
    
    Args:
        name: The name to search for
        contact_list: List of contacts to search within
        
    Returns:
        List of matching contacts with match scores
    """
    matches = []
    name_lower = name.lower()
    
    # Extract just the names for matching
    names = [contact["name"] for contact in contact_list]
    
    if FUZZY_MATCHING_AVAILABLE:
        # Use fuzzy matching if available
        # Find the best matches using process.extract which returns multiple matches
        fuzzy_matches = process.extract(name, names, scorer=fuzz.token_sort_ratio, limit=5)
        
        # Only keep matches above the threshold
        for match_name, score in fuzzy_matches:
            if score >= FUZZY_MATCH_THRESHOLD:
                # Find the original contact with this name
                for contact in contact_list:
                    if contact["name"] == match_name:
                        # Add the match with its score
                        matches.append({
                            "name": contact["name"],
                            "email": contact["email"],
                            "score": score
                        })
                        break
    else:
        # Fallback to simple substring matching
        for contact in contact_list:
            contact_name = contact["name"].lower()
            if name_lower in contact_name or contact_name in name_lower:
                # Simple matching gives a score of 80 (above threshold but below exact match)
                matches.append({
                    "name": contact["name"],
                    "email": contact["email"],
                    "score": 80
                })
    
    # Sort by score (highest first)
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches

def add_contact_to_cache(name: str, email: str):
    """
    Add a contact to the cache for future quick lookups.
    
    Args:
        name: The contact's full name
        email: The contact's email address
    """
    name_lower = name.lower()
    contact = {"name": name, "email": email, "source": "user_selected"}
    
    # Check if this name is already in cache
    if name_lower in contact_cache:
        # Check if this exact contact already exists
        for existing in contact_cache[name_lower]:
            if existing["email"] == email:
                # Move this contact to the front of the list to prioritize it
                contact_cache[name_lower].remove(existing)
                contact_cache[name_lower].insert(0, contact)
                return
        
        # If not found, add it to the front of the list
        contact_cache[name_lower].insert(0, contact)
    else:
        # Create a new entry
        contact_cache[name_lower] = [contact]

# Dictionary to store user-defined aliases
name_aliases = {}

# Load aliases from file if it exists
try:
    if os.path.exists(ALIASES_PATH):
        with open(ALIASES_PATH, 'r') as f:
            name_aliases = json.load(f)
        print(f"Loaded {len(name_aliases)} name aliases from {ALIASES_PATH}")
    else:
        print(f"No aliases file found at {ALIASES_PATH}, starting with empty aliases")
except Exception as e:
    print(f"Error loading aliases from {ALIASES_PATH}: {e}")

async def add_name_alias(alias: str, email: str):
    """
    Add a name alias for a specific email address.
    This allows using friendly names instead of email addresses.
    
    Args:
        alias: The friendly name or alias to use
        email: The email address it should resolve to
        
    Returns:
        Dictionary with status and the added alias
    """
    name_aliases[alias.lower()] = email
    
    # Save aliases to file
    try:
        # Ensure the secrets directory exists
        os.makedirs(os.path.dirname(ALIASES_PATH), exist_ok=True)
        
        with open(ALIASES_PATH, 'w') as f:
            json.dump(name_aliases, f, indent=2)
        print(f"Saved {len(name_aliases)} name aliases to {ALIASES_PATH}")
        save_success = True
    except Exception as e:
        print(f"Error saving aliases to {ALIASES_PATH}: {e}")
        save_success = False
    
    return {
        "status": "success" if save_success else "warning",
        "message": f"Added alias '{alias}' for '{email}'" + 
                  ("" if save_success else " (but failed to save to file)"),
        "saved_to_file": save_success
    }

def get_email_from_alias(alias: str):
    """
    Get an email address from a name alias if it exists.
    
    Args:
        alias: The alias to look up
        
    Returns:
        Email address if found, None otherwise
    """
    return name_aliases.get(alias.lower())


async def list_name_aliases():
    """
    List all currently defined name aliases.
    
    Returns:
        Dictionary with alias-email mappings
    """
    # Create a copy of the aliases to return
    aliases_list = []
    
    for alias, email in name_aliases.items():
        aliases_list.append({
            "alias": alias,
            "email": email
        })
    
    return {
        "aliases": aliases_list,
        "count": len(aliases_list)
    }


async def list_all_contacts():
    """
    List all available contacts from both directory and fallback sources.
    
    Returns:
        Dictionary with contacts grouped by source
    """
    # Ensure the fallback contacts file exists before proceeding
    ensure_fallback_contacts_file()
    
    # Try to get directory contacts first
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
                        "email": email
                    })
                    
                    # Also add to the cache for future lookups
                    add_contact_to_cache(name, email)
    except Exception as e:
        print(f"Error fetching directory contacts: {e}")
    
    # Get fallback contacts
    fallback_contacts = []
    for i, contact in enumerate(FALLBACK_CONTACTS):
        fallback_contacts.append({
            "id": i,
            "name": contact.get("name", ""),
            "email": contact.get("email", "")
        })
    
    # Get aliases
    aliases = []
    for alias, email in name_aliases.items():
        aliases.append({
            "alias": alias,
            "email": email
        })
    
    return {
        "status": "success",
        "directory_contacts": directory_contacts,
        "fallback_contacts": fallback_contacts,
        "aliases": aliases,
        "directory_available": len(directory_contacts) > 0
    }

async def edit_fallback_contact(contact_id: int, new_name: str = None, new_email: str = None):
    """
    Edit a fallback contact by ID.
    
    Args:
        contact_id: The ID of the contact to edit (index in the FALLBACK_CONTACTS list)
        new_name: Optional new name for the contact
        new_email: Optional new email for the contact
        
    Returns:
        Dictionary with status and the updated contact information
    """
    global FALLBACK_CONTACTS
    
    # Ensure the fallback contacts file exists before proceeding
    ensure_fallback_contacts_file()
    
    # Check if the contact ID is valid
    if contact_id < 0 or contact_id >= len(FALLBACK_CONTACTS):
        return {
            "status": "error",
            "message": f"Invalid contact ID: {contact_id}. Valid range is 0-{len(FALLBACK_CONTACTS)-1}"
        }
    
    # Get the current contact
    current_contact = FALLBACK_CONTACTS[contact_id]
    
    # Create a copy for comparison
    old_contact = {
        "name": current_contact.get("name", ""),
        "email": current_contact.get("email", "")
    }
    
    # Update the contact with new values if provided
    if new_name is not None:
        current_contact["name"] = new_name
    
    if new_email is not None:
        current_contact["email"] = new_email
    
    # Save the updated contacts to file
    save_success = save_fallback_contacts()
    
    # Clear the contact cache since we've updated a contact
    contact_cache.clear()
    
    return {
        "status": "success" if save_success else "warning",
        "message": f"Updated contact ID {contact_id}" + 
                  ("" if save_success else " but failed to save to file"),
        "old_contact": old_contact,
        "updated_contact": current_contact,
        "contact_id": contact_id,
        "saved_to_file": save_success
    }


async def add_fallback_contact(name: str, email: str):
    """
    Add a new fallback contact.
    
    Args:
        name: The name of the new contact
        email: The email of the new contact
        
    Returns:
        Dictionary with status and the new contact information
    """
    global FALLBACK_CONTACTS
    
    # Ensure the fallback contacts file exists before proceeding
    ensure_fallback_contacts_file()
    
    # Create the new contact
    new_contact = {
        "name": name,
        "email": email
    }
    
    # Add to the fallback contacts list
    FALLBACK_CONTACTS.append(new_contact)
    
    # Save the updated contacts to file
    save_success = save_fallback_contacts()
    
    # Clear the contact cache since we've added a contact
    contact_cache.clear()
    
    return {
        "status": "success" if save_success else "warning",
        "message": f"Added new contact: {name} <{email}>" + 
                  ("" if save_success else " but failed to save to file"),
        "new_contact": new_contact,
        "contact_id": len(FALLBACK_CONTACTS) - 1,
        "saved_to_file": save_success
    }


async def delete_fallback_contact(contact_id: int):
    """
    Delete a fallback contact by ID.
    
    Args:
        contact_id: The ID of the contact to delete (index in the FALLBACK_CONTACTS list)
        
    Returns:
        Dictionary with status and the deleted contact information
    """
    global FALLBACK_CONTACTS
    
    # Ensure the fallback contacts file exists before proceeding
    ensure_fallback_contacts_file()
    
    # Check if the contact ID is valid
    if contact_id < 0 or contact_id >= len(FALLBACK_CONTACTS):
        return {
            "status": "error",
            "message": f"Invalid contact ID: {contact_id}. Valid range is 0-{len(FALLBACK_CONTACTS)-1}"
        }
    
    # Get the contact to be deleted
    deleted_contact = FALLBACK_CONTACTS[contact_id]
    
    # Remove the contact from the list
    FALLBACK_CONTACTS.pop(contact_id)
    
    # Save the updated contacts to file
    save_success = save_fallback_contacts()
    
    # Clear the contact cache since we've deleted a contact
    contact_cache.clear()
    
    return {
        "status": "success" if save_success else "warning",
        "message": f"Deleted contact ID {contact_id}" + 
                  ("" if save_success else " but failed to save to file"),
        "deleted_contact": deleted_contact,
        "saved_to_file": save_success
    }

async def resolve_name_to_email(name: str):
    """
    Try to resolve a name directly to an email without requiring user selection.
    Checks aliases first, then tries exact matches in cache, then uses fuzzy matching.
    
    Args:
        name: Name or alias to resolve
        
    Returns:
        Email address if a single clear match is found, None otherwise
    """
    # Check if this is a known alias
    email = get_email_from_alias(name)
    if email:
        return email
    
    # Check if we have an exact match in the cache
    name_lower = name.lower()
    if name_lower in contact_cache:
        contacts = contact_cache[name_lower]
        # If there's only one match, return it directly
        if len(contacts) == 1:
            return contacts[0]["email"]
        # If multiple matches but one has a high score, use that one
        elif len(contacts) > 1:
            # Check if any contact has a score attribute (from fuzzy matching)
            scored_contacts = [c for c in contacts if "score" in c]
            if scored_contacts:
                # Sort by score
                scored_contacts.sort(key=lambda x: x["score"], reverse=True)
                # If the top match has a very high score (90+), use it
                if scored_contacts[0]["score"] >= 90:
                    return scored_contacts[0]["email"]
    
    # Try matching against fallback contacts
    # This will use fuzzy matching if available, or simple matching if not
    matches = fuzzy_match_contacts(name, FALLBACK_CONTACTS)
    if matches and matches[0]["score"] >= 90:
        return matches[0]["email"]
    
    # No direct resolution possible
    return None
