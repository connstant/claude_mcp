from .search_person import select_contact as select_from_results

def select_contact(contact_id: int, search_results: dict) -> dict:
    """
    Select a contact from previous search results by ID.
    
    Args:
        contact_id: The ID of the contact to select (1-based index)
        search_results: The previous search results dictionary
        
    Returns:
        Dictionary with the selected contact or error message
    """
    return select_from_results(contact_id, search_results)
