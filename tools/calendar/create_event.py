from adapter.google_apis import send_create_event_request

async def create_event(title: str, start_time: str, end_time: str, description: str = "", location: str = None, attendees: list = None) -> dict:
    """
    Create a new calendar event.
    
    Args:
        title: Event title/summary
        start_time: Start time in ISO format
        end_time: End time in ISO format
        description: Event description (optional)
        location: Event location (optional)
        attendees: List of email addresses for attendees (optional)
        
    Returns:
        Dictionary with created event details
    """
    event = await send_create_event_request(title, start_time, end_time, description, location, attendees)
    
    # Prepare the basic response
    response = {
        "message": f"Event '{event['summary']}' created.",
        "start": event["start"],
        "end": event["end"],
        "event_id": event["event_id"]
    }
    
    # Add location if it exists
    if "location" in event:
        response["location"] = event["location"]
        
    # Add attendees if they exist
    if "attendees" in event:
        response["attendees"] = event["attendees"]
        
    return response
