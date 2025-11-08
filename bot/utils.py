"""
Utility functions for the Telegram TTS Bot
"""
import logging
import time
import json
from pathlib import Path
import pycountry
from .config import BASE_AUDIO_DIR, VOICE_JSON_PATH, AUDIO_EXPIRY_TIME

logger = logging.getLogger(__name__)


def cleanup_audio_files(user_id):
    """Remove audio files older than AUDIO_EXPIRY_TIME to save disk space."""
    user_audio_dir = BASE_AUDIO_DIR / str(user_id)
    if user_audio_dir.exists():
        now = time.time()
        for file in user_audio_dir.iterdir():
            if file.is_file() and file.suffix == '.mp3':
                try:
                    if file.stat().st_mtime < now - AUDIO_EXPIRY_TIME:
                        file.unlink()
                        logger.debug(f"Deleted old audio file: {file.name}")
                except Exception as e:
                    logger.error(f"Error deleting file {file.name}: {e}")


def load_voice_list(filename=None):
    """Load voices from a JSON file and return a list of dictionaries."""
    if filename is None:
        filename = VOICE_JSON_PATH
    
    voices = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            voices = json.load(file)
            logger.info(f"Total voices loaded: {len(voices)}")
    except FileNotFoundError:
        logger.error(f"File {filename} not found. Please ensure it's in the correct directory.")
    except Exception as e:
        logger.error(f"Error loading voice list: {e}")
    return voices


def sanitize_callback_data(data):
    """Ensure callback data is within limits and properly formatted."""
    return data.replace(" ", "_")[:64]


def get_countries(voices):
    """Extract and return a sorted list of unique country names from voices."""
    countries = set()
    for voice in voices:
        locale = voice['Locale']
        parts = locale.split('-')
        if len(parts) != 2:
            logger.warning(f"Invalid locale format: {locale}")
            continue
        language_code, country_code = parts
        country = pycountry.countries.get(alpha_2=country_code.upper())
        if country:
            countries.add(country.name)
        else:
            countries.add(country_code.upper())
    return sorted(countries)


def get_languages(voices, country_name):
    """Extract and return a sorted list of unique language names for a given country."""
    languages = set()
    for voice in voices:
        locale = voice['Locale']
        parts = locale.split('-')
        if len(parts) != 2:
            continue
        language_code, country_code = parts
        country = pycountry.countries.get(alpha_2=country_code.upper())
        if country and country.name == country_name:
            language = pycountry.languages.get(alpha_2=language_code.lower())
            if language:
                languages.add(language.name)
            else:
                languages.add(language_code.upper())
    return sorted(languages)


def get_voices(voices, country_name, language_name):
    """Retrieve and return a list of voices for a given country and language."""
    selected_voices = []
    for voice in voices:
        locale = voice['Locale']
        parts = locale.split('-')
        if len(parts) != 2:
            continue
        language_code, country_code = parts
        country = pycountry.countries.get(alpha_2=country_code.upper())
        language = pycountry.languages.get(alpha_2=language_code.lower())
        if country and language:
            if country.name == country_name and language.name == language_name:
                selected_voices.append(voice)
    return selected_voices

