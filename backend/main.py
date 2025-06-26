from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agent.langgraph_agent import handle_user_message, confirm_booking
from backend.google_calendar import confirm_booking_with_details  # ✅ new
from dateutil import parser as dateutil_parser
from agent.langgraph_agent import CALENDAR_ID


app = FastAPI(
    title="TailorTalk Calendar Agent",
    description="Conversational AI to book appointments on Google Calendar",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session (production: use Redis or DB)
user_sessions = {}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_message = body.get("message", "").strip()
    session_id = "default"

    if not user_message:
        return {"response": "Please enter a valid message."}

    # Basic yes/confirm case
    if user_message.lower() in {"yes", "yeah", "confirm", "book it", "ok", "okay", "yep"}:
        last_slot = user_sessions.get(session_id)
        if not last_slot:
            return {"response": "⚠️ I don't remember which time slot to book. Please specify again."}
        # Prompt frontend to collect user details
        return {
            "response": "✍️ Please enter: Name | Work | Place/Link",
            "slot": last_slot  # Send slot info to frontend
        }

    # Handle regular input
    response, suggested_slot = handle_user_message(user_message)

    if suggested_slot:
        user_sessions[session_id] = suggested_slot

    return {"response": response}


@app.post("/confirm")
async def confirm_with_user_info(request: Request):
    body = await request.json()
    slot = body.get("slot")
    user_info = body.get("user_info")

    if not slot or not user_info:
        return {"response": "❌ Missing slot or user details."}

    try:
        # ✅ Convert time strings back to datetime
        slot["start_time"] = dateutil_parser.isoparse(slot["start_time"])
        slot["end_time"] = dateutil_parser.isoparse(slot["end_time"])
    except Exception as e:
        return {"response": f"❌ Invalid datetime format: {e}"}

    response = confirm_booking_with_details(CALENDAR_ID, slot, user_info)
    return {"response": response}




