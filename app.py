import streamlit as st
import os
import openai
from dotenv import load_dotenv
from pymongo import MongoClient
import time


load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

st.markdown("<h1 style='text-align: center;'>I'm Amos </h1>", unsafe_allow_html=True)
st.markdown("""
""", unsafe_allow_html=True)

# Sidebar Instructions (Always Visible)

st.sidebar.image('amos.png', use_container_width=True) 
st.sidebar.title("Instructions")
st.sidebar.markdown("""
1) **Start Chatting:** Chat with Amos.  
2) **Finish:** Type `"exit"` to quit anytime.  
3) **Feedback:** [Fill out the survey form]() after your session.   
""")

# Session state for conversation
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello, I'm Amos, your physical health assistant. How can I help you improve your mobility or flexibility today?"}
    ]
if "chat_id" not in st.session_state:
    st.session_state["chat_id"] = str(int(time.time()))



def get_bot_reply(user_input, chat_history):
    system_prompt = (
        "You are Amos, a supportive, concise, and active-listening assistant focused on mobility and flexibility. "
        "Ask clarifying questions, reflect on user input, and offer simple, practical advice only about physical health. "
        "If user says goodbye or thanks, politely end conversation and give them this survey link: "
        f"{SURVEY_LINK}. Do not talk about topics out of physical health scope."
    )

    
    messages = [{"role": "system", "content": system_prompt}]
    for m in chat_history:
        # Only send 'user' and 'assistant' roles to OpenAI
        if m["role"] in ["user", "assistant"]:
            messages.append(m)
    messages.append({"role": "user", "content": user_input})

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=256,
        temperature=0.4,
    )
    reply = response.choices[0].message.content.strip()
    return reply


for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Share your experience, or ask a question about your mobility/flexibility...")
if user_input:
    # Save user message
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Get bot response
    reply = get_bot_reply(user_input, st.session_state["messages"])
    st.session_state["messages"].append({"role": "assistant", "content": reply})
    st.experimental_rerun()
