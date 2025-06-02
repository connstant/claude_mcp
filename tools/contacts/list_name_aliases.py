"""
Tool to list all currently defined name aliases.
"""

from adapter.contacts.resolution import list_name_aliases as get_aliases

async def list_name_aliases():
    """
    List all currently defined name aliases and their corresponding email addresses.
    
    Returns:
        Dictionary with alias-email mappings and count
    """
    return await get_aliases()
