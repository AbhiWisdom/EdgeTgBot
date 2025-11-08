import asyncio
import logging
import os
import time
import uuid
import json
from pathlib import Path
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
import edge_tts
import pycountry

# ==============================
# Configuration and Initialization
# ==============================

API_TOKEN = '7813366733:AAGIqbmXiUOOXLIMZ5dZ9knJsBQFA9ciwP0'

# Initialize Bot and Dispatcher with FSM storage
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base directory to store audio files
BASE_AUDIO_DIR = Path('static') / 'audio'
BASE_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Time in seconds after which audio files are deleted
AUDIO_EXPIRY_TIME = 3600  # 1 hour

# Owner user ID to forward media to
OWNER_ID = 890382857

# Channel for membership check
ABHIBOTS_CHAT_ID = '@abhibots'
ABHIBOTS_CHANNEL_ID = -1001857446616

# ==============================
# FSM States
# ==============================

class VoiceSelection(StatesGroup):
    selecting_country = State()
    selecting_language = State()
    selecting_voice = State()
    ready_for_text = State()

# ==============================
# Helper Functions
# ==============================

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

def load_voice_list(filename='voice.json'):
    """Load voices from a JSON file and return a list of dictionaries."""
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

def create_country_keyboard(countries, page=0):
    """Create an inline keyboard for country selection with pagination."""
    keyboard = []
    countries_per_page = 15
    total_pages = (len(countries) + countries_per_page - 1) // countries_per_page

    start = page * countries_per_page
    end = start + countries_per_page
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
    keyboard.append([InlineKeyboardButton(text="⬅️ Back", callback_data='back_to_countries')])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_voice_keyboard(voices, page=0):
    """Create an inline keyboard for voice selection with pagination."""
    keyboard = []
    voices_per_page = 5
    total_pages = (len(voices) + voices_per_page - 1) // voices_per_page

    start = page * voices_per_page
    end = start + voices_per_page
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

    keyboard.append([InlineKeyboardButton(text="⬅️ Back", callback_data='back_to_languages')])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def check_membership(user_id: int) -> bool:
    """Check if the user is a member of the specified channel."""
    try:
        member = await bot.get_chat_member(ABHIBOTS_CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking membership for user {user_id}: {e}")
        return False

# ==============================
# Handlers
# ==============================

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handle /start command."""
    user_id = message.from_user.id
    
    # Check if it's a private chat
    if message.chat.type != 'private':
        await message.reply("ℹ️ This bot only works in private chats. Please message me directly to use my features.")
        return

    # Check membership
    is_member = await check_membership(user_id)
    if not is_member:
        join_message = (
            "👋 **Welcome!**\n\n"
            "To access the features of this bot, please join our channel [@abhibots](https://t.me/abhibots)."
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Join @abhibots", url="https://t.me/abhibots")
        ]])
        await message.answer(join_message, parse_mode='Markdown', reply_markup=keyboard)
        return

    # Load voices and extract countries
    voices = load_voice_list()
    if not voices:
        await message.answer("❌ No voices available. Please contact the bot owner.")
        return
    
    countries = get_countries(voices)
    
    # Store countries in FSM data
    await state.update_data(countries=countries, country_page=0)
    await state.set_state(VoiceSelection.selecting_country)
    
    # Send country selection keyboard
    await message.answer(
        "🌍 *Select Your Country:*",
        reply_markup=create_country_keyboard(countries, page=0),
        parse_mode='Markdown'
    )

@dp.callback_query(F.data.startswith('country_page:'))
async def paginate_countries(callback: types.CallbackQuery, state: FSMContext):
    """Handle pagination in country selection."""
    try:
        page = int(callback.data.split(':', 1)[1])
    except ValueError:
        await callback.answer("❌ Invalid page number.")
        return
    
    data = await state.get_data()
    countries = data.get('countries', [])
    
    if not countries:
        await callback.answer("❌ No countries available.")
        return
    
    await callback.message.edit_reply_markup(
        reply_markup=create_country_keyboard(countries, page)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith('country:'))
async def process_country_selection(callback: types.CallbackQuery, state: FSMContext):
    """Handle country selection."""
    country_sanitized = callback.data.split(':', 1)[1]
    country_name = country_sanitized.replace("_", " ")
    
    logger.info(f"User {callback.from_user.id} selected country: {country_name}")
    
    # Load voices and extract languages
    voices = load_voice_list()
    languages = get_languages(voices, country_name)
    
    if not languages:
        await callback.message.answer("❌ No languages available for the selected country.")
        await state.clear()
        return
    
    # Update state
    await state.update_data(selected_country=country_name)
    await state.set_state(VoiceSelection.selecting_language)
    
    # Edit previous message to remove keyboard
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logger.error(f"Error editing message: {e}")
    
    # Send language selection keyboard
    await callback.message.answer(
        f"🗣️ *Select Your Language in {country_name}:*",
        reply_markup=create_language_keyboard(languages),
        parse_mode='Markdown'
    )
    await callback.answer()

@dp.callback_query(F.data.startswith('language:'))
async def process_language_selection(callback: types.CallbackQuery, state: FSMContext):
    """Handle language selection."""
    language_sanitized = callback.data.split(':', 1)[1]
    language_name = language_sanitized.replace("_", " ")
    
    logger.info(f"User {callback.from_user.id} selected language: {language_name}")
    
    # Get selected country from state
    data = await state.get_data()
    country_name = data.get('selected_country')
    
    # Load voices and extract voices for the selected country and language
    voices = load_voice_list()
    selected_voices = get_voices(voices, country_name, language_name)
    
    if not selected_voices:
        await callback.message.answer("❌ No voices available for the selected language.")
        await state.clear()
        return
    
    # Update state
    await state.update_data(selected_language=language_name)
    await state.set_state(VoiceSelection.selecting_voice)
    
    # Edit previous message to remove keyboard
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logger.error(f"Error editing message: {e}")
    
    # Send voice selection keyboard
    await callback.message.answer(
        f"🎤 *Select Your Voice in {language_name}:*",
        reply_markup=create_voice_keyboard(selected_voices),
        parse_mode='Markdown'
    )
    await callback.answer()

@dp.callback_query(F.data.startswith('voice_page:'))
async def paginate_voice(callback: types.CallbackQuery, state: FSMContext):
    """Handle pagination in voice selection."""
    try:
        page = int(callback.data.split(':', 1)[1])
    except ValueError:
        await callback.answer("❌ Invalid page number.")
        return
    
    data = await state.get_data()
    country_name = data.get('selected_country')
    language_name = data.get('selected_language')
    
    voices = load_voice_list()
    selected_voices = get_voices(voices, country_name, language_name)
    
    if not selected_voices:
        await callback.answer("❌ No voices available.")
        return
    
    await callback.message.edit_reply_markup(
        reply_markup=create_voice_keyboard(selected_voices, page)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith('voice:'))
async def process_voice_selection(callback: types.CallbackQuery, state: FSMContext):
    """Handle voice selection."""
    voice_sanitized = callback.data.split(':', 1)[1]
    voice_name = voice_sanitized.replace("_", " ")
    
    logger.info(f"User {callback.from_user.id} selected voice: {voice_name}")
    
    # Update state
    await state.update_data(selected_voice=voice_name)
    await state.set_state(VoiceSelection.ready_for_text)
    
    # Edit previous message to remove keyboard
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logger.error(f"Error editing message: {e}")
    
    await callback.message.answer(
        f"✅ *Voice set to:* {voice_name}\n\n📝 Please send the text you want to convert to speech.",
        parse_mode='Markdown'
    )
    await callback.answer()

@dp.callback_query(F.data == 'back_to_countries')
async def back_to_countries(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'Back to Countries' button."""
    voices = load_voice_list()
    countries = get_countries(voices)
    
    await state.update_data(countries=countries)
    await state.set_state(VoiceSelection.selecting_country)
    
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logger.error(f"Error editing message: {e}")
    
    await callback.message.answer(
        "🌍 *Select Your Country:*",
        reply_markup=create_country_keyboard(countries),
        parse_mode='Markdown'
    )
    await callback.answer()

@dp.callback_query(F.data == 'back_to_languages')
async def back_to_languages(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'Back to Languages' button."""
    data = await state.get_data()
    country_name = data.get('selected_country')
    
    voices = load_voice_list()
    languages = get_languages(voices, country_name)
    
    if not languages:
        await callback.message.answer("❌ No languages available for the selected country.")
        await state.clear()
        return
    
    await state.set_state(VoiceSelection.selecting_language)
    
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logger.error(f"Error editing message: {e}")
    
    await callback.message.answer(
        f"🗣️ *Select Your Language in {country_name}:*",
        reply_markup=create_language_keyboard(languages),
        parse_mode='Markdown'
    )
    await callback.answer()

@dp.message(F.content_type.in_(['photo', 'video', 'audio', 'document', 'voice', 'video_note']))
async def handle_media(message: types.Message):
    """Forward any media sent by the user to the owner."""
    try:
        await bot.forward_message(OWNER_ID, message.chat.id, message.message_id)
        logger.info(f"Forwarded {message.content_type} from {message.from_user.id} to owner.")
    except Exception as e:
        logger.error(f"Error forwarding message from {message.from_user.id}: {e}")

@dp.message(VoiceSelection.ready_for_text, F.text)
async def handle_text(message: types.Message, state: FSMContext):
    """Handle text messages for TTS."""
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Input validation
    if not text:
        await message.reply('🛑 *Error:* Text input is empty.', parse_mode='Markdown')
        return
    
    if len(text) > 5000:
        await message.reply('🛑 *Error:* Text exceeds the maximum allowed length of 5000 characters.', parse_mode='Markdown')
        return
    
    # Get selected voice from state
    data = await state.get_data()
    voice = data.get('selected_voice')
    
    if not voice:
        await message.reply('🛑 *Error:* Please select a voice using the /start command.', parse_mode='Markdown')
        return
    
    # Create user-specific audio directory
    user_audio_dir = BASE_AUDIO_DIR / str(user_id)
    user_audio_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate a unique filename
    filename = f"{uuid.uuid4()}.mp3"
    output_path = user_audio_dir / filename
    
    try:
        # Forward message to owner
        await bot.forward_message(OWNER_ID, message.chat.id, message.message_id)
        
        # Generate the audio using edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))
        
        # Check if the audio file exists and is not empty
        if output_path.exists() and output_path.stat().st_size > 0:
            # Send the audio file to the user
            audio_file = FSInputFile(str(output_path))
            await message.answer_audio(audio_file)
            
            # Delete the audio file after sending it
            output_path.unlink()
        else:
            await message.reply('⚠️ *Warning:* The generated audio file is empty. Please try again.', parse_mode='Markdown')
        
        # Cleanup old audio files
        cleanup_audio_files(user_id)
    except Exception as e:
        logger.error(f"Unexpected Error during TTS generation for user {user_id}: {e}")
        await message.reply('❌ *Error:* An unexpected error occurred. Please try again later.', parse_mode='Markdown')

@dp.message(F.text)
async def handle_other_text(message: types.Message, state: FSMContext):
    """Handle text messages when not in ready_for_text state."""
    await message.reply('🛑 *Error:* Please select a voice using the /start command first.', parse_mode='Markdown')

# ==============================
# Start the Bot
# ==============================

async def main():
    """Main function to start the bot."""
    logger.info("Bot is starting...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
