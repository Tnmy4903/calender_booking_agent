from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List
from dateutil import parser as dateutil_parser
from dateutil import tz

# Path to your service account credentials
SERVICE_ACCOUNT_FILE = "credentials/calendar-bot-credentials.json"

# Define the required scopes
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    """
    Initializes and returns the Google Calendar API service client.
    """
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=credentials)

def list_events(calendar_id: str, time_min: str, time_max: str) -> List[dict]:
    """
    Fetches all events between `time_min` and `time_max`.
    """
    service = get_calendar_service()
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    return events_result.get("items", [])

def is_time_slot_available(calendar_id: str, start_time: datetime, end_time: datetime) -> bool:
    """
    Returns True if no existing event overlaps with the given time slot.
    Handles timezone-aware datetime comparisons.
    """
    # Ensure start and end are timezone-aware (Asia/Kolkata assumed)
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=tz.gettz("Asia/Kolkata"))
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=tz.gettz("Asia/Kolkata"))

    # Convert to UTC for querying
    time_min = start_time.astimezone(tz.UTC).isoformat()
    time_max = end_time.astimezone(tz.UTC).isoformat()

    events = list_events(calendar_id, time_min, time_max)

    for event in events:
        event_start_str = event["start"].get("dateTime")
        event_end_str = event["end"].get("dateTime")

        if not event_start_str or not event_end_str:
            continue

        event_start = dateutil_parser.isoparse(event_start_str)
        event_end = dateutil_parser.isoparse(event_end_str)

        # Ensure event datetimes are also timezone-aware
        if start_time < event_end and end_time > event_start:
            print(f"[DEBUG] ❌ Overlap with existing event: {event_start} - {event_end}")
            return False

    return True

def create_event(calendar_id: str, summary: str, description: str, start_time: datetime, end_time: datetime) -> dict:
    """
    Creates a calendar event.
    """
    service = get_calendar_service()

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        }
    }

    return service.events().insert(calendarId=calendar_id, body=event).execute()
