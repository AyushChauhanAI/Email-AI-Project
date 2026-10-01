import os
from dotenv import load_dotenv

# .env file se variables load karein
load_dotenv()

# Credentials fetch karein
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# Check karein ki sabhi variables properly load hue ya nahi
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable nahi mili! Kripya .env file check karein.")

if not GMAIL_USER or not GMAIL_APP_PASSWORD:
    raise ValueError("Gmail credentials (GMAIL_USER ya GMAIL_APP_PASSWORD) nahi mile! Kripya .env file check karein.")