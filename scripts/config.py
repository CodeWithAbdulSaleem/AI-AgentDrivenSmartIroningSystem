import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
TB_URL = os.getenv("TB_URL", "https://demo.thingsboard.io")
USERNAME = os.getenv("TB_USERNAME")
PASSWORD = os.getenv("TB_PASSWORD")
DEVICE_ID = os.getenv("DEVICE_ID")

if not all([USERNAME, PASSWORD, DEVICE_ID]):
    print("WARNING: Missing credentials in .env file. Please copy .env.example to .env and fill in your details.")
