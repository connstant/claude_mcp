from adapter.contacts.resolution import add_name_alias as add_alias

def add_name_alias(alias: str, email: str) -> dict:
    """
    Add or update a name alias mapping.
    
    Args:
        alias: The alias to use (e.g., "my manager")
        email: The email address to map to
        
    Returns:
        Dictionary with result of the operation
    """
    if not alias or len(alias.strip()) == 0:
        return {
            "success": False,
            "message": "Please provide a valid alias name."
        }
    
    if not email or len(email.strip()) == 0 or '@' not in email:
        return {
            "success": False,
            "message": "Please provide a valid email address."
        }
    
    return add_alias(alias.strip(), email.strip())
