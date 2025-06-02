"""
Fallback contacts management for when Directory API is unavailable.
"""

import os
import json

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

# Default fallback contacts
DEFAULT_FALLBACK_CONTACTS = [
    {
        "name": "Kevin Dai",
        "email": "kevindai02@gmail.com"
    }
]

# Global variable to store fallback contacts
FALLBACK_CONTACTS = DEFAULT_FALLBACK_CONTACTS.copy()

# Path to save fallback contacts
FALLBACK_CONTACTS_PATH = os.path.join(os.path.dirname(__file__), "../../secrets/fallback-contacts.json")

# Threshold for fuzzy matching
FUZZY_MATCH_THRESHOLD = 70

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

def get_all_fallback_contacts():
    """
    Get all fallback contacts.
    
    Returns:
        List of fallback contacts
    """
    # Ensure the fallback contacts file exists before proceeding
    ensure_fallback_contacts_file()
    
    fallback_contacts = []
    for i, contact in enumerate(FALLBACK_CONTACTS):
        fallback_contacts.append({
            "id": i,
            "name": contact.get("name", ""),
            "email": contact.get("email", ""),
            "source": "fallback"
        })
    
    return fallback_contacts

async def lookup_fallback_contact(query):
    """
    Look up a contact in the fallback contacts.
    
    Args:
        query: The search query (name or email)
        
    Returns:
        Dictionary with contact information or None if not found
    """
    # Ensure the fallback contacts file exists before proceeding
    ensure_fallback_contacts_file()
    
    query = query.lower()
    
    for i, contact in enumerate(FALLBACK_CONTACTS):
        name = contact.get("name", "").lower()
        email = contact.get("email", "").lower()
        
        if query in name or query in email:
            return {
                "id": i,
                "name": contact.get("name", ""),
                "email": contact.get("email", ""),
                "source": "fallback"
            }
    
    return None

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
    
    # Import here to avoid circular imports
    from .resolution import contact_cache
    contact_cache.clear()
    
    return {
        "status": "success" if save_success else "warning",
        "message": f"Added new contact: {name} <{email}>" + 
                  ("" if save_success else " but failed to save to file"),
        "new_contact": new_contact,
        "contact_id": len(FALLBACK_CONTACTS) - 1,
        "saved_to_file": save_success
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
    
    # Import here to avoid circular imports
    from .resolution import contact_cache
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
    
    # Import here to avoid circular imports
    from .resolution import contact_cache
    contact_cache.clear()
    
    return {
        "status": "success" if save_success else "warning",
        "message": f"Deleted contact ID {contact_id}" + 
                  ("" if save_success else " but failed to save to file"),
        "deleted_contact": deleted_contact,
        "saved_to_file": save_success
    }

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
