"""
Contact resolution and caching functionality.
"""

import os
import json
import re

# In-memory cache for contacts and aliases
contact_cache = {}

# Path to name aliases file
NAME_ALIASES_PATH = os.path.join(os.path.dirname(__file__), "../../secrets/name-aliases.json")

# Global variable to store name aliases
name_aliases = {}

# Load name aliases from file if it exists
try:
    if os.path.exists(NAME_ALIASES_PATH):
        with open(NAME_ALIASES_PATH, 'r') as f:
            loaded_aliases = json.load(f)
            if isinstance(loaded_aliases, dict):
                name_aliases = loaded_aliases
                print(f"Loaded {len(name_aliases)} name aliases from {NAME_ALIASES_PATH}")
            else:
                print(f"Invalid format in {NAME_ALIASES_PATH}, using empty aliases")
    else:
        print(f"No name aliases file found at {NAME_ALIASES_PATH}, using empty aliases")
        # Create an empty aliases file
        os.makedirs(os.path.dirname(NAME_ALIASES_PATH), exist_ok=True)
        with open(NAME_ALIASES_PATH, 'w') as f:
            json.dump({}, f, indent=2)
        print(f"Created empty name aliases file at {NAME_ALIASES_PATH}")
except Exception as e:
    print(f"Error loading name aliases from {NAME_ALIASES_PATH}: {e}")

def save_name_aliases():
    """
    Save the current name aliases to the JSON file in secrets directory.
    Creates the file if it doesn't exist.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(NAME_ALIASES_PATH), exist_ok=True)
        with open(NAME_ALIASES_PATH, 'w') as f:
            json.dump(name_aliases, f, indent=2)
        print(f"Saved {len(name_aliases)} name aliases to {NAME_ALIASES_PATH}")
        return True
    except Exception as e:
        print(f"Error saving name aliases to {NAME_ALIASES_PATH}: {e}")
        return False

def add_contact_to_cache(name, email):
    """
    Add a contact to the in-memory cache for faster lookups.
    
    Args:
        name: The name of the contact
        email: The email of the contact
    """
    if not name or not email:
        return
    
    # Normalize the name for case-insensitive lookups
    name_lower = name.lower()
    
    # Add to cache with both name and email as keys
    contact_cache[name_lower] = email
    contact_cache[email.lower()] = email

async def resolve_contact(query):
    """
    Resolve a contact query to an email address.
    Tries multiple methods in this order:
    1. Check if it's already an email
    2. Look in the cache
    3. Check name aliases
    4. Look in the directory
    5. Look in fallback contacts
    
    Args:
        query: The contact query (name, alias, or email)
        
    Returns:
        Dictionary with the resolved contact information or None if not found
    """
    if not query:
        return None
    
    # Normalize the query
    query = query.strip()
    query_lower = query.lower()
    
    # Check if it's already an email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, query):
        return {
            "name": query,  # Use email as name since we don't know the actual name
            "email": query,
            "source": "direct_email"
        }
    
    # Check the cache
    if query_lower in contact_cache:
        email = contact_cache[query_lower]
        return {
            "name": query,  # Use the query as name since that's what the user used
            "email": email,
            "source": "cache"
        }
    
    # Check name aliases
    if query_lower in name_aliases:
        email = name_aliases[query_lower]
        add_contact_to_cache(query, email)  # Add to cache for future lookups
        return {
            "name": query,  # Use the alias as name since that's what the user used
            "email": email,
            "source": "alias"
        }
    
    # Import here to avoid circular imports
    from .directory_api import lookup_contact_in_directory
    
    # Look in the directory
    directory_contact = await lookup_contact_in_directory(query)
    if directory_contact:
        add_contact_to_cache(directory_contact["name"], directory_contact["email"])
        return directory_contact
    
    # Import here to avoid circular imports
    from .fallback import lookup_fallback_contact
    
    # Look in fallback contacts
    fallback_contact = await lookup_fallback_contact(query)
    if fallback_contact:
        add_contact_to_cache(fallback_contact["name"], fallback_contact["email"])
        return fallback_contact
    
    # Not found
    return None

async def add_name_alias(alias, email):
    """
    Add a new name alias.
    
    Args:
        alias: The alias to add
        email: The email to associate with the alias
        
    Returns:
        Dictionary with status and the new alias information
    """
    global name_aliases
    
    # Normalize the alias
    alias_lower = alias.lower()
    
    # Check if the alias already exists
    if alias_lower in name_aliases:
        old_email = name_aliases[alias_lower]
        if old_email == email:
            return {
                "status": "info",
                "message": f"Alias '{alias}' already exists for email {email}",
                "alias": alias,
                "email": email
            }
        else:
            # Update the existing alias
            name_aliases[alias_lower] = email
            save_success = save_name_aliases()
            
            # Clear the contact cache since we've updated an alias
            contact_cache.clear()
            
            return {
                "status": "success" if save_success else "warning",
                "message": f"Updated alias '{alias}' from {old_email} to {email}" + 
                          ("" if save_success else " but failed to save to file"),
                "alias": alias,
                "old_email": old_email,
                "new_email": email,
                "saved_to_file": save_success
            }
    
    # Add the new alias
    name_aliases[alias_lower] = email
    save_success = save_name_aliases()
    
    # Clear the contact cache since we've added an alias
    contact_cache.clear()
    
    return {
        "status": "success" if save_success else "warning",
        "message": f"Added new alias: '{alias}' -> {email}" + 
                  ("" if save_success else " but failed to save to file"),
        "alias": alias,
        "email": email,
        "saved_to_file": save_success
    }

async def delete_name_alias(alias):
    """
    Delete a name alias.
    
    Args:
        alias: The alias to delete
        
    Returns:
        Dictionary with status and the deleted alias information
    """
    global name_aliases
    
    # Normalize the alias
    alias_lower = alias.lower()
    
    # Check if the alias exists
    if alias_lower not in name_aliases:
        return {
            "status": "error",
            "message": f"Alias '{alias}' not found"
        }
    
    # Get the email associated with the alias
    email = name_aliases[alias_lower]
    
    # Remove the alias
    del name_aliases[alias_lower]
    save_success = save_name_aliases()
    
    # Clear the contact cache since we've deleted an alias
    contact_cache.clear()
    
    return {
        "status": "success" if save_success else "warning",
        "message": f"Deleted alias: '{alias}' -> {email}" + 
                  ("" if save_success else " but failed to save to file"),
        "alias": alias,
        "email": email,
        "saved_to_file": save_success
    }

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
    # Get contacts from directory
    from adapter.contacts.directory_api import list_directory_contacts
    
    directory_contacts = []
    try:
        directory_result = await list_directory_contacts()
        if directory_result and "contacts" in directory_result:
            directory_contacts = directory_result["contacts"]
    except Exception as e:
        print(f"Error fetching directory contacts: {e}")
    
    # Get contacts from fallback
    from adapter.contacts.fallback import get_all_fallback_contacts
    
    fallback_contacts = []
    try:
        fallback_contacts = get_all_fallback_contacts()
    except Exception as e:
        print(f"Error fetching fallback contacts: {e}")
    
    # Combine results
    return {
        "directory": directory_contacts,
        "fallback": fallback_contacts,
        "total": len(directory_contacts) + len(fallback_contacts)
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
    # First try to resolve the contact using the full resolution process
    contact = await resolve_contact(name)
    if contact and "email" in contact:
        return contact["email"]
    
    # Check if this is a known alias
    for alias, email in name_aliases.items():
        if alias.lower() == name.lower():
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
    from adapter.contacts.fallback import get_all_fallback_contacts, fuzzy_match_contacts
    
    fallback_contacts = get_all_fallback_contacts()
    matches = fuzzy_match_contacts(name, fallback_contacts)
    if matches and matches[0]["score"] >= 90:
        return matches[0]["email"]
    
    # No direct resolution possible
    return None
