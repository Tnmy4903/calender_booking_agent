from datetime import datetime, timedelta
from backend.google_calendar import (
    is_time_slot_available,
    create_event,
    confirm_booking_with_details
)
import re
from dateutil import parser as dateutil_parser

CALENDAR_ID = "tnmy4903@gmail.com"


def find_available_slots(base_date: datetime, count: int = 3) -> list:
    """
    Finds `count` available 1-hour slots between 9 AM to 10 PM.
    """
    available = []
    for hour in range(9, 22):  # 9 AM to 10 PM
        start = base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        if is_time_slot_available(CALENDAR_ID, start, end):
            available.append({"start_time": start, "end_time": end})
        if len(available) == count:
            break
    return available


def parse_user_message(message: str) -> dict:
    """
    Parses user message for time, or returns None if no time given.
    """
    print(f"[DEBUG] User Message: {message}")

    # Time range pattern
    time_range = re.search(
        r"(\d{1,2})(:\d{2})?\s?(am|pm)?\s?[-–]\s?(\d{1,2})(:\d{2})?\s?(am|pm)?", message.lower()
    )

    if time_range:
        g = time_range.groups()
        start_str = f"{g[0]}{g[1] or ':00'} {g[2] or ''}".strip()
        end_str = f"{g[3]}{g[4] or ':00'} {g[5] or g[2] or ''}".strip()
    else:
        # Single time like 5pm
        single = re.search(r"\b(\d{1,2})(:\d{2})?\s?(am|pm)\b", message.lower())
        if single:
            start_str = single.group()
            end_str = None
        else:
            return None  # no time found

    now = datetime.now()
    if "tomorrow" in message.lower():
        base_date = now + timedelta(days=1)
    elif "today" in message.lower():
        base_date = now
    elif "next week" in message.lower():
        base_date = now + timedelta(days=7)
    else:
        base_date = now + timedelta(days=1)

    date = base_date.strftime("%Y-%m-%d")
    start_dt_str = f"{date} {start_str}"
    end_dt_str = f"{date} {end_str}" if end_str else None

    try:
        start_time = dateutil_parser.parse(start_dt_str)
        end_time = dateutil_parser.parse(end_dt_str) if end_dt_str else start_time + timedelta(hours=1)
        return {
            "summary": "Meeting with user",
            "description": f"Booked via TailorTalk: \"{message}\"",
            "start_time": start_time,
            "end_time": end_time
        }
    except Exception as e:
        print(f"[DEBUG] Parse error: {e}")
        return None


def handle_user_message(user_input: str) -> tuple[str, dict | None]:
    """
    Handles user request and returns (response_message, slot_to_confirm_if_any).
    """
    parsed = parse_user_message(user_input)

    if parsed:
        available = is_time_slot_available(CALENDAR_ID, parsed["start_time"], parsed["end_time"])
        if available:
            st = parsed["start_time"].strftime("%I:%M %p")
            et = parsed["end_time"].strftime("%I:%M %p")
            msg = f"🕒 Should I book {st} to {et}?"
            return msg, parsed
        else:
            base_date = parsed["start_time"].replace(hour=9, minute=0)
            alternatives = find_available_slots(base_date)
            if not alternatives:
                return "❌ That slot is busy and no other free times found.", None
            alt_msg = "❌ That slot is busy. Available options:\n"
            for slot in alternatives:
                st = slot["start_time"].strftime("%I:%M %p")
                et = slot["end_time"].strftime("%I:%M %p")
                alt_msg += f"- {st} to {et}\n"
            return alt_msg.strip(), None
    else:
        base_date = datetime.now() + timedelta(days=1)
        options = find_available_slots(base_date)
        if not options:
            return "❌ I couldn't find any free time slots for tomorrow.", None
        st = options[0]["start_time"].strftime("%I:%M %p")
        et = options[0]["end_time"].strftime("%I:%M %p")
        msg = f"🕒 Should I book {st} to {et} tomorrow?"
        return msg, {
            "summary": "Meeting with user",
            "description": f"Booked via TailorTalk: \"{user_input}\"",
            "start_time": options[0]["start_time"],
            "end_time": options[0]["end_time"]
        }


def confirm_booking(slot: dict, user_info: dict) -> str:
    """
    Confirms a booking with user metadata (name, work, place).
    """
    return confirm_booking_with_details(CALENDAR_ID, slot, user_info)
