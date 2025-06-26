import streamlit as st
import requests

st.set_page_config(page_title="TailorTalk", page_icon="🗓️", layout="centered")

st.title("🧵 TailorTalk: Calendar Booking Assistant")
st.markdown("Chat with the assistant to book appointments on your calendar.")

# Chat history state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input box
user_input = st.chat_input("Type your message here...")

if user_input:
    # Append user message
    st.session_state.chat_history.append(("user", user_input))

    # Send message to backend
    try:
        response = requests.post("http://localhost:8000/chat", json={"message": user_input})
        bot_reply = response.json().get("response", "Error from backend")
    except Exception as e:
        bot_reply = f"❌ Error contacting backend: {e}"

    st.session_state.chat_history.append(("bot", bot_reply))

# Display chat
for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(message)
