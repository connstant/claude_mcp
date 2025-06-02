from adapter.calendar.queries import list_calendar_events

async def list_events(max_results: int = 10, search_query: str = None, time_min: str = None, time_max: str = None) -> dict:
    """
    List calendar events with optional filtering.
    """
    return await list_calendar_events(max_results, search_query, time_min, time_max)
