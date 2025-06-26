from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List
from dateutil import parser as dateutil_parser
from dateutil import tz
import os
import json

# Path to your service account credentials
SERVICE_ACCOUNT_FILE = "credentials/calendar-bot-credentials.json"

# Define the required scopes
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    """
    Initializes and returns the Google Calendar API service client.
    Loads credentials from a file locally or from env variable on Render.
    """
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
    else:
        google_creds = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        if not google_creds:
            raise RuntimeError("Missing Google credentials in both file and environment.")
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(google_creds), scopes=SCOPES
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
    # Ensure timezone-aware
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=tz.gettz("Asia/Kolkata"))
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=tz.gettz("Asia/Kolkata"))

    # Convert to UTC
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

def confirm_booking_with_details(calendar_id: str, slot: dict, user_info: dict) -> str:
    """
    Confirms the booking and includes user name, work, and location/link in the event.
    """
    if not is_time_slot_available(calendar_id, slot["start_time"], slot["end_time"]):
        return "❌ Sorry, that time slot is no longer available."

    name = user_info.get("name", "Unknown")
    work = user_info.get("work", "No purpose given")
    place = user_info.get("place", "No location provided")

    summary = f"Meeting with {name}"
    description = f"Purpose: {work}\nLocation/Link: {place}\nDetails: {slot['description']}"

    try:
        create_event(
            calendar_id,
            summary,
            description,
            slot["start_time"],
            slot["end_time"]
        )
        st = slot["start_time"].strftime("%I:%M %p")
        et = slot["end_time"].strftime("%I:%M %p")
        return f"✅ Meeting booked from {st} to {et} with {name}!"
    except Exception as e:
        return f"⚠️ Booking failed: {str(e)}"
