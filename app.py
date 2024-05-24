import json
import requests
import streamlit as st
from models import User, Message
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from streamlit_cookies_manager import EncryptedCookieManager
from sqlalchemy.exc import NoResultFound
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()
api=os.getenv("API_KEY")
@st.cache_resource
def connect_to_db():
    # Get MySQL connection details from environment variables
    # DB_USERNAME = os.getenv("DB_USERNAME")
    # DB_PASSWORD = os.getenv("DB_PASSWORD")
    # DB_HOST = os.getenv("DB_HOST")
    # DB_PORT = os.getenv("DB_PORT")
    # DB_NAME = os.getenv("DB_NAME")

    # # Create the MySQL engine
    # DATABASE_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    # engine = create_engine(DATABASE_URL)
    
    
    engine = create_engine("sqlite:///dbchat.db")
    return engine

engine = connect_to_db()

def get_user_by_email(session, email):
    try:
        return session.exec(select(User).where(User.email == email)).one()
    except NoResultFound:
        return None

def authenticate_user(email: str, password: str) -> Optional[User]:
    with Session(engine) as session:
        user = get_user_by_email(session, email)
        if user and user.password == password:
            return user
    return None

def get_user_messages(user_id):
    with Session(engine) as session:
        return session.exec(select(Message).where(Message.user_id == user_id)).all()

def ai(user_text_message):
    
    responce_txt="!"
    try:
        headers = {"Authorization": f"Bearer {api}"}

        url = "https://api.edenai.run/v2/text/chat"
        payload = {
            "providers": "openai",
            "text": user_text_message,
            "chatbot_global_action": "Act as an assistant",
            "previous_history": [],
            "temperature": 0.0,
            "max_tokens": 150,
            "fallback_providers": ""
        }

        response = requests.post(url, json=payload, headers=headers)
        result = json.loads(response.text)
        print(result['openai']['generated_text'])
        responce_txt=response.text
    except:
        responce_txt="API not working"

    # return user_text_message * 2
    return responce_txt

def register_user(name, email, password):
    with Session(engine) as session:
        if get_user_by_email(session, email):
            return None  # User already exists
        
        user = User(name=name, email=email, password=password)
        session.add(user)
        session.commit()  # Commit before refreshing
        session.refresh(user)  # Refresh the user object
        return user

def process(user_text_message, user_id):
    ai_text = ai(user_text_message)
    
    user_message = Message(text=user_text_message, type="user", user_id=user_id)
    ai_message = Message(text=ai_text, type="ai", user_id=user_id)
    
    with Session(engine) as session:
        session.add(user_message)
        session.add(ai_message)
        session.commit()
    
    st.session_state.messages.append({'type': "user", "text": user_text_message})
    st.session_state.messages.append({'type': "ai", "text": ai_text})
    return ai_text

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.get('authenticated', False):
    st.title("Login or Register")
    
    choice = st.selectbox("Select Action", ["Login", "Register"])
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if choice == "Register":
        name = st.text_input("Name")
        if st.button("Register"):
            user = register_user(name, email, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.messages = []  # Initialize messages list
                st.write(f"Welcome, {st.session_state.user.name}")
                st.rerun()
            else:
                st.error("Registration failed")
    elif choice == "Login":
        if st.button("Login"):
            user = authenticate_user(email, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.messages = []  # Initialize messages list
                st.write(f"Welcome, {st.session_state.user.name}")
                st.rerun()
            else:
                st.error("Login failed")

if st.session_state.user:
    user_id = st.session_state.user.id
    
    messages = get_user_messages(user_id)
        
    st.title("Chat Application")
    
    for message in messages:
        with st.chat_message(message.type):
            st.write(message.text)
    
    if user_text_message := st.chat_input("Say something ...!"):
        ai_text = process(user_text_message, user_id)
        
        with st.chat_message("user"):
            st.write(user_text_message)
        
        with st.chat_message("ai"):
            st.write(ai_text)