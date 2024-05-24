import streamlit as st
from models import User,Message
from sqlmodel import Field,Session,SQLModel,create_engine,select,Relationship

@st.cache_resource
def connect_to_db():
    engine= create_engine("sqlite:///dbchat.db")
    SQLModel.metadata.create_all(engine)
    return engine

engine= connect_to_db()

def ai(user_text_message):
    return user_text_message*2

def process(user_text_message):
    ai_text=ai(user_text_message)
    
    user_message= Message(text=user_text_message, type="user",user_id=1)
    ai_message= Message(text=user_text_message, type="ai",user_id=1)
    
    ##BackEnd
    with Session(engine) as session:
        session.add(user_message)
        session.add(ai_message)
        session.commit()
        
    
    
    
    ##FrontEnd
    st.session_state.messages.append({'type':"user", "text":user_text_message})
    st.session_state.messages.append({'type':"ai", "text":ai_text})
    return ai_text
    




if "messages" not in st.session_state:
    st.session_state.messages=[]
    
for message in st.session_state.messages:
    with st.chat_message(message['type']):
        st.write(message['text'])

if user_text_message:=st.chat_input("Say something ...!"):
    
    ai_text=process(user_text_message)
    
    with st.chat_message("user"):
        st.write(user_text_message)
        
    with st.chat_message("ai"):
        st.write(ai_text)   
    
