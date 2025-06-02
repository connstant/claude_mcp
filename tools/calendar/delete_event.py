from adapter.google_apis import send_delete_event_request

async def delete_event(event_id: str) -> dict:
    """
    Delete a calendar event by its ID.
    """
    result = await send_delete_event_request(event_id)
    return result