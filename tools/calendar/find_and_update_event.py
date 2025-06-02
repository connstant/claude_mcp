from adapter.calendar.queries import list_calendar_events
from adapter.calendar.events import send_update_event_request

async def find_and_update_event(title: str = None, description: str = None, start_date: str = None, 
                              new_title: str = None, new_start_time: str = None, new_end_time: str = None, 
                              new_description: str = None, new_location: str = None, 
                              add_attendees: list = None, remove_attendees: list = None) -> dict:
    """
    Find and update an event based on search criteria.
    
    Args:
        title: Event title to search for
        description: Event description to search for
        start_date: Start date of the event (YYYY-MM-DD)
        new_title: New title for the event
        new_start_time: New start time for the event
        new_end_time: New end time for the event
        new_description: New description for the event
        new_location: New location for the event
        add_attendees: List of email addresses to add as attendees
        remove_attendees: List of email addresses to remove from attendees
        
    Returns:
        Dictionary with result of the operation
    """
    # Build search query from title and/or description
    search_terms = []
    if title:
        search_terms.append(title)
    if description:
        search_terms.append(description)
    
    search_query = " ".join(search_terms) if search_terms else None
    
    # Set time range if start_date is provided
    time_min = None
    time_max = None
    if start_date:
        # Convert date to datetime range for that day
        time_min = f"{start_date}T00:00:00Z"
        time_max = f"{start_date}T23:59:59Z"
    
    # List events matching the criteria
    result = await list_calendar_events(
        max_results=10,
        search_query=search_query,
        time_min=time_min,
        time_max=time_max
    )
    
    if not result['success']:
        return {
            "success": False,
            "message": f"Failed to find events: {result.get('message', 'Unknown error')}"
        }
    
    if result['count'] == 0:
        return {
            "success": False,
            "message": "No events found matching the criteria."
        }
    
    if result['count'] > 1:
        # Return the list of events found so the user can choose
        return {
            "success": False,
            "message": f"Found {result['count']} events matching the criteria. Please be more specific or provide an event ID.",
            "events": result['events']
        }
    
    # If exactly one event is found, update it
    event = result['events'][0]
    update_result = await update_event(
        event_id=event['id'],
        title=new_title,
        start_time=new_start_time,
        end_time=new_end_time,
        description=new_description,
        location=new_location,
        add_attendees=add_attendees,
        remove_attendees=remove_attendees
    )
    
    if update_result['success']:
        return {
            "success": True,
            "message": f"Successfully updated event '{event['summary']}'",
            "old_event": event,
            "updated_event": {
                "summary": update_result['summary'],
                "start": update_result['start'],
                "end": update_result['end'],
                "event_id": update_result['event_id']
            }
        }
    else:
        return {
            "success": False,
            "message": f"Found event '{event['summary']}' but failed to update it: {update_result.get('message', 'Unknown error')}"
        }
