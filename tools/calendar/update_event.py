from adapter.calendar.events import send_update_event_request

async def update_event(event_id: str, title: str = None, start_time: str = None, end_time: str = None, description: str = None, location: str = None, add_attendees: list = None, remove_attendees: list = None) -> dict:
    """
    Update an existing calendar event.
    
    Args:
        event_id: ID of the event to update
        title: New title for the event (optional)
        start_time: New start time for the event (optional)
        end_time: New end time for the event (optional)
        description: New description for the event (optional)
        location: New location for the event (optional)
        add_attendees: List of email addresses to add as attendees (optional)
        remove_attendees: List of email addresses to remove from attendees (optional)
        
    Returns:
        Dictionary with result of the update operation
    """
    return await send_update_event_request(event_id, title, start_time, end_time, description, location, add_attendees, remove_attendees)
