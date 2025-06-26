from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agent.langgraph_agent import handle_user_message, confirm_booking

app = FastAPI(
    title="TailorTalk Calendar Agent",
    description="Conversational AI to book appointments on Google Calendar",
    version="1.1.0"
)

# Allow CORS for local frontend (Streamlit)
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
    session_id = "default"  # Replace with user_id/email/IP for real sessions

    if not user_message:
        return {"response": "Please enter a valid message."}

    # If user replies with yes/confirm → proceed to book
    if user_message.lower() in {"yes", "yeah", "confirm", "book it", "ok", "okay", "yep"}:
        last_slot = user_sessions.get(session_id)
        if not last_slot:
            return {"response": "⚠️ I don't remember which time slot to book. Please specify again."}
        response = confirm_booking(last_slot)
        user_sessions.pop(session_id, None)  # clear after booking
        print(f"User message: {user_message}")
        print(f"Response: {response}")
        return {"response": response}

    # Else, handle as normal user message
    response, suggested_slot = handle_user_message(user_message)

    # If a slot was suggested for confirmation, store it
    if suggested_slot:
        user_sessions[session_id] = suggested_slot

    return {"response": response}


