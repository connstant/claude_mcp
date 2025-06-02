"""
Tool to delete a fallback contact.
"""

from adapter.contacts.fallback import delete_fallback_contact

async def delete_contact(contact_id: int):
    """
    Delete a fallback contact by ID.
    
    Args:
        contact_id: The ID of the contact to delete
        
    Returns:
        Dictionary with status and the deleted contact information
    """
    return await delete_fallback_contact(contact_id)
