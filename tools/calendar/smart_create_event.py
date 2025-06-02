from adapter.contacts.resolution import resolve_name_to_email
from adapter.calendar.events import send_create_event_request

async def smart_create_event(title: str, start_time: str, end_time: str, 
                           description: str = "", location: str = None, 
                           attendee_names: list = None) -> dict:
    """
    Create a new calendar event with smart attendee name resolution.
    
    Args:
        title: Event title/summary
        start_time: Start time in ISO format
        end_time: End time in ISO format
        description: Event description (optional)
        location: Event location (optional)
        attendee_names: List of attendee names to resolve to emails (optional)
        
    Returns:
        Dictionary with created event details and any unresolved attendees
    """
    resolved_attendees = []
    unresolved_attendees = []
    
    # Try to resolve attendee names to email addresses
    if attendee_names and isinstance(attendee_names, list):
        for name in attendee_names:
            email = await resolve_name_to_email(name)
            if email:
                resolved_attendees.append(email)
            else:
                unresolved_attendees.append(name)
    
    # Create the event with the resolved attendees
    event = await send_create_event_request(
        title, 
        start_time, 
        end_time, 
        description, 
        location, 
        resolved_attendees if resolved_attendees else None
    )
    
    # Prepare the response
    response = {
        "message": f"Event '{event['summary']}' created.",
        "start": event["start"],
        "end": event["end"],
        "event_id": event["event_id"]
    }
    
    # Add location if it exists
    if "location" in event:
        response["location"] = event["location"]
        
    # Add attendees information
    if resolved_attendees:
        response["resolved_attendees"] = resolved_attendees
    
    if unresolved_attendees:
        response["unresolved_attendees"] = unresolved_attendees
        response["message"] += f" Note: {len(unresolved_attendees)} attendee(s) could not be automatically resolved."
    
    return response
