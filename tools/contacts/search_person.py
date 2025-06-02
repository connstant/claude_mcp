from adapter.contacts.directory_api import lookup_contact_in_directory
from adapter.contacts.fallback import lookup_fallback_contact
from adapter.contacts.resolution import add_contact_to_cache, resolve_contact

async def search_person(name: str) -> dict:
    """
    Search for a person by name and return matching contacts.
    
    Args:
        name: The name or partial name to search for
        
    Returns:
        Dictionary with matching contacts and metadata
    """
    if not name or len(name.strip()) == 0:
        return {
            "success": False,
            "message": "Please provide a name to search for.",
            "contacts": []
        }
    
    # Try to resolve the contact directly first
    resolved_contact = await resolve_contact(name)
    if resolved_contact:
        contacts = [resolved_contact]
    else:
        # If not resolved directly, try to find matches in directory and fallback
        directory_contact = await lookup_contact_in_directory(name)
        fallback_contact = await lookup_fallback_contact(name)
        
        contacts = []
        if directory_contact:
            contacts.append(directory_contact)
        if fallback_contact:
            contacts.append(fallback_contact)
    
    if not contacts:
        return {
            "success": False,
            "message": f"No contacts found matching '{name}'.",
            "contacts": []
        }
    
    # Format the response
    formatted_contacts = []
    for i, contact in enumerate(contacts):
        # Add to cache for future lookups
        if "name" in contact and "email" in contact:
            add_contact_to_cache(contact["name"], contact["email"])
            
        formatted_contacts.append({
            "id": i + 1,
            "name": contact.get("name", ""),
            "email": contact.get("email", ""),
            "source": contact.get("source", "unknown")
        })
    
    return {
        "success": True,
        "message": f"Found {len(contacts)} contacts matching '{name}'.",
        "contacts": formatted_contacts
    }

def select_contact(contact_id: int, search_results: dict) -> dict:
    """
    Select a contact from previous search results by ID.
    
    Args:
        contact_id: The ID of the contact to select (1-based index)
        search_results: The previous search results dictionary
        
    Returns:
        Dictionary with the selected contact or error message
    """
    if not search_results or not search_results.get("success", False):
        return {
            "success": False,
            "message": "No valid search results to select from.",
            "contact": None
        }
    
    contacts = search_results.get("contacts", [])
    
    if not contacts:
        return {
            "success": False,
            "message": "No contacts available to select from.",
            "contact": None
        }
    
    try:
        contact_id = int(contact_id)
        if contact_id < 1 or contact_id > len(contacts):
            return {
                "success": False,
                "message": f"Invalid contact ID. Please select a number between 1 and {len(contacts)}.",
                "contact": None
            }
    except ValueError:
        return {
            "success": False,
            "message": "Invalid contact ID. Please provide a number.",
            "contact": None
        }
    
    selected_contact = contacts[contact_id - 1]
    
    # Add to cache for future quick lookups
    add_contact_to_cache(selected_contact["name"], selected_contact["email"])
    
    return {
        "success": True,
        "message": f"Selected contact: {selected_contact['name']} ({selected_contact['email']})",
        "contact": selected_contact
    }
