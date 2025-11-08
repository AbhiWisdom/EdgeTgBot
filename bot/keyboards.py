"""
Keyboard builders for the Telegram TTS Bot
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .config import COUNTRIES_PER_PAGE, VOICES_PER_PAGE
from .utils import sanitize_callback_data


def create_country_keyboard(countries, page=0):
    """Create an inline keyboard for country selection with pagination."""
    keyboard = []
    total_pages = (len(countries) + COUNTRIES_PER_PAGE - 1) // COUNTRIES_PER_PAGE

    start = page * COUNTRIES_PER_PAGE
    end = start + COUNTRIES_PER_PAGE
    page_countries = countries[start:end]

    # Add country buttons (3 per row)
    for i in range(0, len(page_countries), 3):
        row = []
        for country in page_countries[i:i+3]:
            row.append(InlineKeyboardButton(
                text=country,
                callback_data=f'country:{sanitize_callback_data(country)}'
            ))
        keyboard.append(row)

    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Previous",
            callback_data=f'country_page:{page - 1}'
        ))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(
            text="Next ➡️",
            callback_data=f'country_page:{page + 1}'
        ))
    
    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_language_keyboard(languages):
    """Create an inline keyboard for language selection."""
    keyboard = []
    for language in languages:
        keyboard.append([InlineKeyboardButton(
            text=language,
            callback_data=f'language:{sanitize_callback_data(language)}'
        )])
    keyboard.append([InlineKeyboardButton(
        text="⬅️ Back",
        callback_data='back_to_countries'
    )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_voice_keyboard(voices, page=0):
    """Create an inline keyboard for voice selection with pagination."""
    keyboard = []
    total_pages = (len(voices) + VOICES_PER_PAGE - 1) // VOICES_PER_PAGE

    start = page * VOICES_PER_PAGE
    end = start + VOICES_PER_PAGE
    page_voices = voices[start:end]

    for voice in page_voices:
        button_text = f"{voice['ShortName']} ({voice['Gender']})"
        sanitized_voice_name = sanitize_callback_data(voice['ShortName'])
        keyboard.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f'voice:{sanitized_voice_name}'
        )])

    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Previous",
            callback_data=f'voice_page:{page - 1}'
        ))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(
            text="Next ➡️",
            callback_data=f'voice_page:{page + 1}'
        ))
    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton(
        text="⬅️ Back",
        callback_data='back_to_languages'
    )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_join_keyboard():
    """Create keyboard with join channel button."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Join @abhibots",
            url="https://t.me/abhibots"
        )
    ]])
    return keyboard

