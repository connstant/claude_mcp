"""
Tool to add a new fallback contact.
"""

from adapter.contacts.fallback import add_fallback_contact

async def add_contact(name: str, email: str):
    """
    Add a new fallback contact.
    
    Args:
        name: The name of the new contact
        email: The email of the new contact
        
    Returns:
        Dictionary with status and the new contact information
    """
    return await add_fallback_contact(name, email)
