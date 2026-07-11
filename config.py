# config.py
# Configuration loader and settings manager for the AI Meeting Assistant.
# Loads environment variables from the .env file.

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys and Endpoint Configurations
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# LLM & Voice Settings
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

# Path Configurations
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
ASSETS_DIR = os.getenv("ASSETS_DIR", "assets")
