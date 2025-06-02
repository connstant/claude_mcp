"""
Tool to list all available contacts from both directory and fallback sources.
"""

from adapter.contacts.resolution import list_all_contacts as get_all_contacts

async def list_contacts():
    """
    List all available contacts from both directory and fallback sources.
    
    Returns:
        Dictionary with contacts grouped by source (directory and fallback)
    """
    return await get_all_contacts()
