"""
Configuration and constants for the Telegram TTS Bot
"""
import os
from pathlib import Path

# ==============================
# Bot Configuration
# ==============================

# Get API token from environment variable (Heroku) or use default
API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '7813366733:AAHjgmubIbQPXEoxCkipp1BLbD1th96-rWw')

# Webhook URL - Set this to your Heroku app URL + /webhook
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://ttsbot-a572faff13b4.herokuapp.com/webhook')

# ==============================
# Paths
# ==============================

# Use /tmp for Heroku (ephemeral filesystem) or local static for development
if os.environ.get('DYNO'):  # Heroku detection
    BASE_AUDIO_DIR = Path('/tmp/static') / 'audio'
else:
    BASE_AUDIO_DIR = Path('static') / 'audio'

VOICE_JSON_PATH = Path('voice.json')

# ==============================
# Bot Settings
# ==============================

# Time in seconds after which audio files are deleted
AUDIO_EXPIRY_TIME = 3600  # 1 hour

# Maximum text length for TTS
MAX_TEXT_LENGTH = 5000

# Pagination settings
COUNTRIES_PER_PAGE = 15
VOICES_PER_PAGE = 5

# ==============================
# Channel & Owner Settings
# ==============================

# Owner user ID to forward media to (from env or default)
OWNER_ID = int(os.environ.get('OWNER_ID', '890382857'))

# Channel for membership check
ABHIBOTS_CHAT_ID = os.environ.get('ABHIBOTS_CHAT_ID', '@abhibots')
ABHIBOTS_CHANNEL_ID = int(os.environ.get('ABHIBOTS_CHANNEL_ID', '-1001857446616'))

# ==============================
# Initialization
# ==============================

# Create directories if they don't exist
BASE_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

