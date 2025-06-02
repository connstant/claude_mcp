"""
Tool to edit an existing fallback contact.
"""

from adapter.contacts.fallback import edit_fallback_contact

async def edit_contact(contact_id: int, new_name: str = None, new_email: str = None):
    """
    Edit a fallback contact by ID.
    
    Args:
        contact_id: The ID of the contact to edit
        new_name: Optional new name for the contact
        new_email: Optional new email for the contact
        
    Returns:
        Dictionary with status and the updated contact information
    """
    return await edit_fallback_contact(contact_id, new_name, new_email)
