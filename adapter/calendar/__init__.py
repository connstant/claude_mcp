"""
Calendar adapter package for Google Calendar integration.
"""

# Export all calendar-related functions
from adapter.calendar.auth import get_calendar_service
from adapter.calendar.events import (
    send_create_event_request,
    send_delete_event_request,
    send_update_event_request
)
from adapter.calendar.queries import list_calendar_events
