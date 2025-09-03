import streamlit as st
import os
import uuid
import pygame
import time
import random
from datetime import datetime  # Import datetime to handle timestamps
import json
import urllib,io,json
from langchain.llms import OpenAI
from io import StringIO
from dotenv import load_dotenv
from openai import OpenAI
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import MongoDBChatMessageHistory
client = OpenAI()
import openai
from pymongo import MongoClient
# Load environment variables from .env file
load_dotenv()

# OpenAI API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Load exercise data from a JSON file
@st.cache_data(show_spinner=False)
def load_exercise_data():
    try:
        json_data = """
        [
    {
        "name": "",
        "favorite_exercise": "N/A",
        "instructions": [
            "Hi there! I'm Amos, your virtual assistant. Today, we’ll focus on Improving Mobility and Flexibility. What activities do you enjoy that keep you moving?",
            "May I ask where you tend to feel the most stiffness or restriction in your movement? Your feedback will allow us to target those areas more effectively.",
            "What specific improvements in mobility or flexibility would have the most positive impact on your daily life? Our goal is to help enhance those aspects for you.",
            "Have you had the opportunity to work on improving your flexibility or mobility in the past? If so, could you share the methods or exercises you’ve tried and how they worked for you?",
            "How would you describe your current range of motion? Are there any limitations you’ve noticed in your daily activities that you find concerning?",
            "Do you have any concerns about increasing your mobility or flexibility, such as potential injury? Please feel free to share, and we’ll work together to address them."
        ]
    }
    
]
        """
        buffer = StringIO(json_data)
        return json.load(buffer)
    except json.JSONDecodeError:
        st.error("Error: The in-memory JSON data is not valid.")
        return []

# Get exercise details by exercise name
@st.cache_data(show_spinner=False)
def get_exercise_by_name(exercise_name):
    exercises = load_exercise_data()
    exercise = next((item for item in exercises if item["name"].lower() == exercise_name.lower()), None)
    return exercise

# Generate the next step using GPT-3 Instruct model
@st.cache_data(show_spinner=False)
def enhance_instruction_with_gpt3(exercise_name, current_step_instruction):
    #Return the original instruction without enhancement
    return current_step_instruction

# Generate a goodbye message using GPT-3
@st.cache_data(show_spinner=False)
def generate_goodbye_message():
    # Static polite and friendly goodbye message
    goodbye_message = "Thank you for using the physical health session. If you have any more questions in the future, feel free to ask. Take care and have a great day!"
    return goodbye_message

def interpret_user_input(user_input):
    positive_responses = ["next question"]
    negative_responses = ["still working"]
    previous_step_responses = ["previous question"]
    quit_responses = ["exit"]
    
    user_input_lower = user_input.lower()
    if any(phrase in user_input_lower for phrase in positive_responses):
        result = "completed"
    elif any(phrase in user_input_lower for phrase in negative_responses):
        result = "not_completed"
    elif any(phrase in user_input_lower for phrase in previous_step_responses):
        result = "previous"
    elif any(phrase in user_input_lower for phrase in quit_responses):
        result = "quit"
    else:
        result = "help"  
    return result, user_input  
    
survey_link = "https://qualtricsxmqnmjvr9mb.qualtrics.com/jfe/form/SV_8uznC2DYCYJdACW"
KB1 = "https://www.hse.ie/"
KB2 = "https://iapt.ie/"
KB3 = "https://www.iscp.ie/" 
KB4 = "https://www.who.int/health-topics/physical-activity#tab=tab_1"
# Get assistance from GPT-3 for user-shared problems
#@st.cache_data(show_spinner=False)
@st.cache_data(show_spinner=False)
def ask_gpt3_for_help(user_problem, chat_history):
    """
    Function to generate a response from the language model based on user query, chat history.
    """
    # Prepare the chat history and user problem for the OpenAI API
    messages = [{"role": "system", "content": "You are Amos a passive, non-empathetic physical health support chatbot expert In Improving Mobility and Flexibility. Your goal is to guide users with their physical health-related problems. Provide factual, concise responses without empathy, emotion, or unnecessary embellishments (ideally 30 words or fewer). Deliver direct answers to queries and avoid elaboration unless explicitly requested If the topic is outside physical health, redirect the conversation to your area of expertise. If the user expresses gratitude or indicates they want to end the conversation with phrases like 'ok thanks,' 'thank you,' 'got it,' 'sounds good,' or 'that's all,' respond with a brief, such as 'Thank you for chatting with me' and kindly ask them to fill out a survey. Include the following survey link in your response: " + survey_link + "."}] + chat_history + [
        {"role": "user", "content": user_problem}
    ]


    
    # Call the OpenAI chat API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
        stop=["user:", "assistant:"],
        temperature=0.3
        
    )
    
    response_text = response.choices[0].message.content
    return response_text

    
# MongoDB connection
mongo_client = MongoClient("mongodb+srv://ghlogic88:88ZXoTyCx@cluster0.kuweh.mongodb.net/?retryWrites=true&w=majority")
db = mongo_client['survey']
chat_collection = db['rag']

# Initialize session state attributes
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "current_step_index" not in st.session_state:
    st.session_state["current_step_index"] = 0
if "current_exercise" not in st.session_state:
    st.session_state["current_exercise"] = None
if "exercise_history" not in st.session_state:
    st.session_state["exercise_history"] = []
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = str(uuid.uuid4())  # Generate a unique ID
if "session_start_time" not in st.session_state:
    st.session_state["session_start_time"] = time.time()  # Record session start time
if "agreed" not in st.session_state:
    st.session_state["agreed"] = False  # Track whether user has started interaction
if "page" not in st.session_state:
    st.session_state["page"] = "instructions"  # Default to instructions page

@st.cache_data(show_spinner=False)
# Function to automatically save conversation to MongoDB
def auto_save_conversation(messages):
    """Automatically saves the conversation to MongoDB."""
    conversation_id = st.session_state.get("conversation_id")
    session_duration = time.time() - st.session_state["session_start_time"]
    # Prepare the data to save
    chat_data = {
        'conversation_id': conversation_id,
        'messages': [{'role': msg['role'], 'content': msg['content']} for msg in messages],
        'session_duration': session_duration # Add session duration to the saved data
    }

    try:
        chat_collection.update_one(
            {'conversation_id': conversation_id}, 
            {'$set': chat_data}, 
            upsert=True
        )
    except Exception as e:
        print(f"Error saving conversation: {e}")

# Function to show survey page after interaction
def show_survey_page():
    st.markdown("<h1 style='text-align: center;'>Thank You for Using Amos!</h1>", unsafe_allow_html=True)
    st.markdown("### We Value Your Feedback")
    st.markdown("Please take a moment to fill out our survey. Your feedback helps us improve our services.")
    st.markdown("[Click here to fill the survey form](https://qualtricsxmqnmjvr9mb.qualtrics.com/jfe/form/SV_8uznC2DYCYJdACW)")


# Function to start interaction
def continue_click():
    st.session_state["agreed"] = True
    st.session_state["page"] = "main"  # Change to main chat UI

### **🔹 Show Instructions Page (Only Before Clicking Continue)**
if st.session_state["page"] == "instructions":
    st.markdown("""
    Thank you for participating in the Amos study. Below, we will give you some instructions on how to interact with the Amos. After you have finished interacting with Amos, you will be forwarded to a questionnaire where we will ask you a small number of questions.
    """)
    
    st.markdown("### Instructions")
    st.markdown("""
    Please read the instructions below carefully before using this app. The instructions will also be available when you are interacting with Amos.
    
    1. **Launch the App**: Open the virtual assistant by clicking the "Continue to interaction" button below.
    2. **Start Chatting**: Chat with Amos. Amos will probably have a number of questions for you.
    3. **Finish**: Amos will ask questions and end the conversation at the end of those questions. If you want to finish before the natural end of the conversation, type "exit" to quit anytime.
    4. **Feedback**: Fill out the survey form after your session.
    """)

    # Button to start interaction
    st.button("Continue to interaction", on_click=continue_click)
    st.stop()  # **Prevents further execution until button is clicked**

### **🔹 Show Chat UI After Clicking Continue**
st.markdown("<h1 style='text-align: center;'>I'm Amos </h1>", unsafe_allow_html=True)
st.markdown("""
""", unsafe_allow_html=True)

# Sidebar Instructions (Always Visible)

st.sidebar.image('amos.png', use_container_width=True) 
st.sidebar.title("Instructions")
st.sidebar.markdown("""
1) **Start Chatting:** Chat with Amos.  
2) **Finish:** Type `"exit"` to quit anytime.  
3) **Feedback:** [Fill out the survey form](https://qualtricsxmqnmjvr9mb.qualtrics.com/jfe/form/SV_8uznC2DYCYJdACW) after your session.   
""")

        # Initialize pygame mixer for playing sound
#pygame.mixer.init()

# Load the typing sound (ensure you are using a .wav file here)
#typing_sound = pygame.mixer.Sound('Python/Projects/RAG/AL_Bot/typing.wav')  # Replace with the correct path to your typing sound file

# Typing simulation function
def simulate_typing(text, char_pace=0.03, space_lag=0.1, container=None):
    if container is None:
        return  # If no container is provided, exit the function (safety check)
    
    display_text = ""
    
    for i, char in enumerate(text):
        display_text += char
        cursor = "|" if i % 2 == 0 else ""  # Simple cursor blink illusion
        container.markdown(display_text + cursor)

        # Custom pause logic
        if char in [".", "!", "?"]:
            time.sleep(0.5 + random.uniform(0, 0.3))  # Longer pause for punctuation
        elif char == ",":
            time.sleep(0.3 + random.uniform(0, 0.2))
        elif char == " ":
            time.sleep(space_lag + random.uniform(0, 0.05))
        else:
            time.sleep(char_pace + random.uniform(0, 0.01))

    container.markdown(display_text)  # Final render without the blinking cursor
# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "current_step_index" not in st.session_state:
    st.session_state["current_step_index"] = 0
if "current_exercise" not in st.session_state:
    st.session_state["current_exercise"] = None
if "exercise_history" not in st.session_state:
    st.session_state["exercise_history"] = []

# Load exercise data
exercises = load_exercise_data()

for exercise in exercises:
    st.write(f"**{exercise['name']}**")

# Start exercise
if st.session_state["current_exercise"] is None and len(exercises) > 0:
    st.session_state["current_exercise"] = exercises[0]

if st.session_state.get("current_exercise"):
    exercise = st.session_state["current_exercise"]

    # Get current step instruction
    if st.session_state["current_step_index"] < len(exercise["instructions"]):
        current_step_instruction = exercise["instructions"][st.session_state["current_step_index"]]
        enhanced_instruction = enhance_instruction_with_gpt3(exercise["name"], current_step_instruction)
        st.session_state["current_step_instruction"] = enhanced_instruction
        if not any(msg['content'] == enhanced_instruction for msg in st.session_state["messages"]):
            st.session_state.messages.append({"role": "assistant", "content": enhanced_instruction})
    else:
        st.session_state.messages.append({"role": "assistant", "content": "Congratulations! You've completed the exercise."})
        st.session_state["current_exercise"] = None
        st.session_state["current_step_index"] = 0
        st.balloons()

# Chat input
if user_input := st.chat_input("Type Here...."):
    action, user_problem = interpret_user_input(user_input)
    auto_save_conversation(st.session_state["messages"])
    st.session_state.messages.append({"role": "user", "content": user_input})

    if action == "completed":
        st.session_state["exercise_history"].append(st.session_state["current_step_instruction"])
        st.session_state["current_step_index"] += 1
        save_chat_history_to_mongodb()
        if st.session_state["current_step_index"] < len(exercise["instructions"]):
            next_instruction = exercise["instructions"][st.session_state["current_step_index"]]
            enhanced_next_instruction = enhance_instruction_with_gpt3(exercise["name"], next_instruction)
            st.session_state["current_step_instruction"] = enhanced_next_instruction
            if not any(msg['content'] == enhanced_next_instruction for msg in st.session_state["messages"]):
                st.session_state.messages.append({"role": "assistant", "content": enhanced_next_instruction})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Well done! You've successfully concluded the session, and I sincerely hope you found it enjoyable."})
            st.session_state["current_exercise"] = None
            st.session_state["current_step_index"] = 0
            st.balloons()

    elif action == "not_completed":
        st.session_state.messages.append({"role": "assistant", "content": "Not a problem at all! Please feel free to take your time, and whenever you're ready to proceed, just let me know. I'm here to assist you whenever you need."})
        save_chat_history_to_mongo(user_input, st.session_state["current_step_instruction"])

    elif action == "previous":
        if st.session_state["current_step_index"] > 0:
            st.session_state["current_step_index"] -= 1
            previous_instruction = exercise["instructions"][st.session_state["current_step_index"]]
            enhanced_previous_instruction = enhance_instruction_with_gpt3(exercise["name"], previous_instruction)
            st.session_state["current_step_instruction"] = enhanced_previous_instruction
            if not any(msg['content'] == f"Previous Step: {enhanced_previous_instruction}" for msg in st.session_state["messages"]):
                st.session_state.messages.append({"role": "assistant", "content": f"Previous Step: {enhanced_previous_instruction}"})

    elif action == "help":
        help_response = ask_gpt3_for_help(user_problem, st.session_state["messages"])
        st.session_state.messages.append({"role": "assistant", "content": help_response})

    elif action == "i am done" or user_input.lower() in ["i am done", "exit", "goodbye"]:
        goodbye_message = generate_goodbye_message()  # No spinner, directly generate the message
        st.session_state.messages.append({"role": "assistant", "content": goodbye_message})
        st.session_state["current_exercise"] = None
        st.session_state["current_step_index"] = 0
        st.session_state["exercise_history"] = []
        show_survey_page()
        st.stop()
    else:
        st.session_state.messages.append({"role": "assistant", "content": "Certainly! Please feel free to take as much time as you need, and kindly inform me when you're prepared to move forward."})

# Display chat with typing effect for assistant messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        # Only simulate typing for the last assistant message
        if message["role"] == "assistant" and idx == len(st.session_state.messages) - 1:
            container = st.empty()  # Create a container to handle the typing effect
            simulate_typing(message["content"], container=container)  # Pass the container to simulate typing
        else:
            st.markdown(message["content"])  # Display previous messages instantly

       





