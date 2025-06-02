from adapter.google_apis import list_calendar_events
from adapter.google_apis import send_delete_event_request

async def find_and_delete_event(title: str = None, description: str = None, start_date: str = None) -> dict:
    """
    Find and delete an event based on search criteria.
    
    Args:
        title: Event title to search for
        description: Event description to search for
        start_date: Start date of the event (YYYY-MM-DD)
        
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
    
    # If exactly one event is found, delete it
    event = result['events'][0]
    delete_result = await delete_event(event['id'])
    
    if delete_result['success']:
        return {
            "success": True,
            "message": f"Successfully deleted event '{event['summary']}' scheduled for {event['start']}"
        }
    else:
        return {
            "success": False,
            "message": f"Found event '{event['summary']}' but failed to delete it: {delete_result.get('message', 'Unknown error')}"
        }
