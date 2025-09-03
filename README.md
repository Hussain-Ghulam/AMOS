Amos – Your Physical Health Chat Assistant
Welcome to Amos, a conversational assistant designed to help users improve their mobility and flexibility. Powered by OpenAI's GPT-4 and built with Streamlit, Amos offers simple, actionable advice and supports active listening for all your physical health-related questions.


Features:
Conversational Interface: Engage in a helpful, supportive chat focused exclusively on physical health, mobility, and flexibility.
Session Persistence: Maintains chat state throughout the user’s session.
Active Listening: Amos clarifies, reflects, and adapts advice based on your unique needs.
Feedback Ready: Prompts users for feedback after their chat session.
Easy Deployment: Standalone, environment-variable-powered Python application.

Getting Started:
Prerequisites
Python 3.8+
(Recommended) A virtual environment
Installation
Clone the repository:

git clone (https://github.com/Hussain-Ghulam/AMOS).git
cd amos-health-assistant

Install dependencies:
pip install -r requirements.txt

Set up environment variables:
Create a .env file in the root directory and include your OpenAI API key:

OPENAI_API_KEY=your_openai_api_key

(Optional) MongoDB:
If you want to add chat logging, configure MongoDB connection settings in the code.

Running the App:
streamlit run app.py
Open your browser to the provided local URL to start chatting with Amos.

Usage
Amos is designed to discuss mobility and flexibility only.
All other health or non-health topics are gently filtered out.
To end your session, type exit.
On finishing, the bot provides a survey link for feedback.


File Structure:


├── app.py            # Main Streamlit application

├── amos.png          # Image for sidebar branding

├── requirements.txt  # Python dependencies

└── README.md         # You're reading it!

Customization
Survey Link: Update the [Fill out the survey form]() link in both code and sidebar instructions with your actual survey URL.
Branding: Swap in your own logo by replacing amos.png.

Environment Variables:
OPENAI_API_KEY : (Required) Your OpenAI API key.
(Optional) MongoDB credentials for persistent logging.

Contributing:
Pull requests are welcome! Please fork the repository and open an issue to discuss any major changes.

License:
MIT License
