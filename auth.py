import streamlit as st
from sqlmodel import Session
from models import User, engine
from hashlib import sha256
from streamlit_cookies_manager import EncryptedCookieManager

cookies = EncryptedCookieManager(prefix="myapp")

if not cookies.ready():
    st.stop()

def get_hashed_password(password):
    return sha256(password.encode()).hexdigest()

def login(username, password):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if user and user.password == get_hashed_password(password):
            return user
    return None

def signup(username, password):
    with Session(engine) as session:
        hashed_password = get_hashed_password(password)
        user = User(username=username, password=hashed_password)
        session.add(user)
        session.commit()
        return user

def auth_widget():
    st.sidebar.title("Authentication")
    action = st.sidebar.radio("Choose Action", ["Login", "Sign Up"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if action == "Login" and st.sidebar.button("Login"):
        user = login(username, password)
        if user:
            cookies["username"] = user.username
            st.experimental_rerun()
        else:
            st.sidebar.error("Invalid username or password")

    if action == "Sign Up" and st.sidebar.button("Sign Up"):
        user = signup(username, password)
        if user:
            st.sidebar.success("User created successfully")
        else:
            st.sidebar.error("User creation failed")
