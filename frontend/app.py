import streamlit as st
import requests

st.set_page_config(page_title="TailorTalk", page_icon="🗓️", layout="centered")

st.title("🧵 TailorTalk: Calendar Booking Assistant")
st.markdown("Chat with the assistant to book appointments on your calendar.")

# States
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "waiting_for_user_info" not in st.session_state:
    st.session_state.waiting_for_user_info = False

if "last_slot" not in st.session_state:
    st.session_state.last_slot = None

# Constants
BACKEND_URL = "http://localhost:8000"
# BACKEND_URL = "https://calender-booking-agent-backend.onrender.com"

# Input
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))

    if st.session_state.waiting_for_user_info:
        # Expecting "Name | Work | Place"
        parts = user_input.split("|")
        if len(parts) >= 3:
            user_info = {
                "name": parts[0].strip(),
                "work": parts[1].strip(),
                "place": parts[2].strip()
            }
            try:
                response = requests.post(
                    f"{BACKEND_URL}/confirm",
                    json={
                        "slot": st.session_state.last_slot,
                        "user_info": user_info
                    },
                    timeout=10
                )

                print("[DEBUG] /confirm response status:", response.status_code)
                print("[DEBUG] /confirm response text:", response.text)

                if "application/json" in response.headers.get("content-type", ""):
                    bot_reply = response.json().get("response", "❌ Could not book.")
                else:
                    bot_reply = f"❌ Server error: {response.text}"

            except Exception as e:
                bot_reply = f"❌ Error contacting backend: {e}"

        else:
            bot_reply = "⚠️ Please enter details in this format:\n**Name | Work | Place/Link**"

    else:
        try:
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={"message": user_input},
                timeout=10
            )
            data = response.json()
            bot_reply = data.get("response", "❌ Error from backend")
            if "slot" in data:
                st.session_state.waiting_for_user_info = True
                st.session_state.last_slot = data["slot"]
        except Exception as e:
            bot_reply = f"❌ Error contacting backend: {e}"

    # ✅ Reset state if booking was successful
    if "✅" in bot_reply:
        st.session_state.waiting_for_user_info = False
        st.session_state.last_slot = None

    st.session_state.chat_history.append(("bot", bot_reply))

# Display Chat
for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(message)
