"""
Event management utilities for Google Calendar API.
Handles creating, updating, and deleting calendar events.
"""

import datetime
from adapter.calendar.auth import get_calendar_service

async def send_create_event_request(title: str, start_time: str, end_time: str, 
                                  description: str = "", location: str = None, 
                                  attendees: list = None):
    """
    Sends a request to Google Calendar to create a new event.
    
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
    service = get_calendar_service()
    
    # Format the event data
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/Los_Angeles',
        },
    }
    
    # Add optional fields if provided
    if location:
        event['location'] = location
    
    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]
    
    # Call the Calendar API to create the event
    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        # Format the response
        response = {
            'status': 'success',
            'message': f"Event created: {title}",
            'event_id': created_event.get('id'),
            'html_link': created_event.get('htmlLink'),
            'created': True
        }
        
        return response
    except Exception as e:
        print(f"Error creating event: {e}")
        return {
            'status': 'error',
            'message': f"Failed to create event: {str(e)}",
            'created': False
        }

async def send_delete_event_request(event_id: str):
    """
    Sends a request to Google Calendar to delete an event.
    
    Args:
        event_id: ID of the event to delete
        
    Returns:
        Dictionary with status of the deletion
    """
    service = get_calendar_service()
    
    try:
        # Call the Calendar API to delete the event
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        
        return {
            'status': 'success',
            'message': f"Event deleted successfully",
            'event_id': event_id,
            'deleted': True
        }
    except Exception as e:
        print(f"Error deleting event: {e}")
        return {
            'status': 'error',
            'message': f"Failed to delete event: {str(e)}",
            'event_id': event_id,
            'deleted': False
        }

async def send_update_event_request(event_id: str, title: str = None, 
                                  start_time: str = None, end_time: str = None, 
                                  description: str = None, location: str = None, 
                                  add_attendees: list = None, remove_attendees: list = None):
    """
    Sends a request to Google Calendar to update an existing event.
    
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
        Dictionary with updated event details
    """
    service = get_calendar_service()
    
    try:
        # First, get the existing event
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Update fields if provided
        if title:
            event['summary'] = title
        
        if description:
            event['description'] = description
        
        if location:
            event['location'] = location
        
        if start_time:
            event['start']['dateTime'] = start_time
        
        if end_time:
            event['end']['dateTime'] = end_time
        
        # Handle attendees
        current_attendees = event.get('attendees', [])
        
        # Remove attendees if specified
        if remove_attendees:
            current_attendees = [
                attendee for attendee in current_attendees 
                if attendee.get('email') not in remove_attendees
            ]
        
        # Add new attendees if specified
        if add_attendees:
            # Get current email addresses
            current_emails = [attendee.get('email') for attendee in current_attendees]
            
            # Add new attendees that aren't already in the list
            for email in add_attendees:
                if email not in current_emails:
                    current_attendees.append({'email': email})
        
        # Update the attendees list if it was modified
        if add_attendees or remove_attendees:
            event['attendees'] = current_attendees
        
        # Call the Calendar API to update the event
        updated_event = service.events().update(
            calendarId='primary', 
            eventId=event_id, 
            body=event
        ).execute()
        
        # Format the response
        response = {
            'status': 'success',
            'message': f"Event updated successfully",
            'event_id': updated_event.get('id'),
            'html_link': updated_event.get('htmlLink'),
            'updated': True
        }
        
        return response
    except Exception as e:
        print(f"Error updating event: {e}")
        return {
            'status': 'error',
            'message': f"Failed to update event: {str(e)}",
            'event_id': event_id,
            'updated': False
        }
