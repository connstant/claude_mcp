from adapter.google_apis import send_create_event_request
import datetime
import re

def format_datetime_for_google(dt):
    """Format a datetime object for Google Calendar API."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

def get_current_time():
    """Get the current time."""
    return datetime.datetime.now()

def parse_time_string(time_str):
    """Parse a time string into a datetime object."""
    # If the time string is 'now', return the current time
    if time_str.lower() == 'now':
        return get_current_time()
    
    # Try to parse the time string
    try:
        # Check if it's already in ISO format
        if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', time_str):
            return datetime.datetime.fromisoformat(time_str)
        
        # Otherwise, assume it's a date/time string
        return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # If parsing fails, return the current time
        print(f"Could not parse time string '{time_str}', using current time instead")
        return get_current_time()

async def create_event(title: str, start_time: str, end_time: str, description: str = "") -> dict:
    """Create a calendar event with proper time handling."""
    # Parse the start and end times
    start_dt = parse_time_string(start_time)
    
    # If end_time is a duration (e.g., '1h', '30m'), calculate the end time
    duration_match = re.match(r'(\d+)([hm])', end_time)
    if duration_match:
        amount = int(duration_match.group(1))
        unit = duration_match.group(2)
        
        if unit == 'h':
            end_dt = start_dt + datetime.timedelta(hours=amount)
        else:  # unit == 'm'
            end_dt = start_dt + datetime.timedelta(minutes=amount)
    else:
        end_dt = parse_time_string(end_time)
    
    # Format the times for Google Calendar API
    formatted_start = format_datetime_for_google(start_dt)
    formatted_end = format_datetime_for_google(end_dt)
    
    print(f"Creating event from {formatted_start} to {formatted_end}")
    
    # Send the request to Google Calendar API
    event = await send_create_event_request(title, formatted_start, formatted_end, description)
    
    return {
        "message": f"Event '{event['summary']}' created.",
        "start": event["start"],
        "end": event["end"],
        "event_id": event["event_id"]
    }
