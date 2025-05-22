from adapter.google_apis import send_create_event_request

async def create_event(title: str, start_time: str, end_time: str, description: str = "") -> dict:
    event = await send_create_event_request(title, start_time, end_time, description)
    return {
        "message": f"Event '{event['summary']}' created.",
        "start": event["start"],
        "end": event["end"],
        "event_id": event["event_id"]
    }
