import streamlit as st
from models import create_db_and_tables, Message, engine
from auth import auth_widget, cookies
from sqlmodel import Session
from datetime import datetime
from edenai import edenai

edenai_client = edenai.Client(api_key='API_KEY')

create_db_and_tables()
cookies()

if "username" not in cookies:
    auth_widget()
    st.stop()

username = cookies["username"]

def save_message(user_id, message):
    with Session(engine) as session:
        msg = Message(user_id=user_id, message=message, timestamp=datetime.utcnow())
        session.add(msg)
        session.commit()

def get_user_id(username):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        return user.id if user else None

st.title("ChatBot")

message = st.text_input("Your message")
if st.button("Send"):
    user_id = get_user_id(username)
    if user_id and message:
        save_message(user_id, message)
        response = edenai_client.chat.send_message(text=message, provider='openai')
        bot_message = response.get('text', 'Error: No response')
        st.write(f"Bot: {bot_message}")
        save_message(user_id, bot_message)

# Display chat history
st.header("Chat History")
with Session(engine) as session:
    user_id = get_user_id(username)
    messages = session.exec(select(Message).where(Message.user_id == user_id)).all()
    for msg in messages:
        st.write(f"[{msg.timestamp}] {msg.message}")
