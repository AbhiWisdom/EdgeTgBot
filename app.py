"""
Pure Flask Telegram TTS Bot - No Aiogram
Uses Telegram Bot API directly via requests
"""
import os
import json
import logging
import requests
import uuid
import asyncio
import time
import random
from pathlib import Path
from flask import Flask, request, jsonify, session, render_template, send_from_directory
from flask_session import Session
from flask_cors import CORS
import edge_tts
from aiohttp.client_exceptions import WSServerHandshakeError

from bot.config import API_TOKEN, OWNER_ID, ABHIBOTS_CHANNEL_ID, BASE_AUDIO_DIR, MAX_TEXT_LENGTH, WEBHOOK_URL
from bot.utils import load_voice_list, get_countries, get_languages, get_voices, cleanup_audio_files, sanitize_callback_data
from bot.keyboards import create_country_keyboard, create_language_keyboard, create_voice_keyboard, create_join_keyboard
from bot.user_manager import register_user, get_all_users, get_user_count, is_owner, load_users

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup info
logger.info("=" * 50)
logger.info("Telegram TTS Bot Starting...")
logger.info(f"API Token configured: {bool(API_TOKEN)}")
logger.info(f"Webhook URL: {WEBHOOK_URL}")
logger.info(f"Owner ID: {OWNER_ID}")
logger.info("=" * 50)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app)  # Enable CORS for all routes
Session(app)

# Telegram Bot API base URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{API_TOKEN}"

# User states storage (in-memory, use Redis for production)
user_states = {}
user_data = {}


def send_message(chat_id, text, reply_markup=None, parse_mode='Markdown'):
    """Send message via Telegram Bot API."""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None


def send_audio(chat_id, audio_path, caption=None):
    """Send audio file via Telegram Bot API."""
    url = f"{TELEGRAM_API_URL}/sendAudio"
    
    try:
        with open(audio_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            data = {'chat_id': chat_id}
            if caption:
                data['caption'] = caption
            
            response = requests.post(url, files=files, data=data, timeout=30)
            return response.json()
    except Exception as e:
        logger.error(f"Error sending audio: {e}")
        return None


def edit_message_reply_markup(chat_id, message_id, reply_markup=None):
    """Edit message reply markup."""
    url = f"{TELEGRAM_API_URL}/editMessageReplyMarkup"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        return None


def answer_callback_query(callback_query_id, text=None):
    """Answer callback query."""
    url = f"{TELEGRAM_API_URL}/answerCallbackQuery"
    payload = {'callback_query_id': callback_query_id}
    if text:
        payload['text'] = text
    
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"Error answering callback: {e}")


def forward_message(chat_id, from_chat_id, message_id):
    """Forward message."""
    url = f"{TELEGRAM_API_URL}/forwardMessage"
    payload = {
        'chat_id': chat_id,
        'from_chat_id': from_chat_id,
        'message_id': message_id
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")
        return None


def get_chat_member(chat_id, user_id):
    """Get chat member status."""
    url = f"{TELEGRAM_API_URL}/getChatMember"
    payload = {
        'chat_id': chat_id,
        'user_id': user_id
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        if result.get('ok'):
            return result.get('result', {}).get('status')
        return None
    except Exception as e:
        logger.error(f"Error getting chat member: {e}")
        return None


async def _generate_tts_async(text, voice, output_path, timeout=30):
    """
    Internal async function to generate TTS audio.
    
    Args:
        text: Text to convert to speech
        voice: Voice shortname
        output_path: Path to save the audio file
        timeout: Connection timeout in seconds
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Use edge_tts.Communicate with increased timeouts and proper async/await
        # Increased timeouts help with connection issues
        communicate = edge_tts.Communicate(
            text, 
            voice,
            connect_timeout=timeout,
            receive_timeout=timeout * 2
        )
        await communicate.save(str(output_path))
        
        # Verify file was created and has content
        if output_path.exists() and output_path.stat().st_size > 0:
            return True
        else:
            logger.warning(f"Generated audio file is empty")
            return False
            
    except WSServerHandshakeError as e:
        # Check if it's a 403 error (rate limiting/IP blocking)
        error_str = str(e)
        if '403' in error_str or 'Invalid response status' in error_str:
            raise Exception(f"Edge TTS 403 error: {e}")
        else:
            raise Exception(f"TTS WebSocket error: {e}")
    except Exception as e:
        raise


def generate_tts_with_retry(text, voice, output_path, max_retries=5):
    """
    Generate TTS audio with retry logic for handling 403 errors.
    Uses edge_tts library with proper async handling and improved retry strategy.
    
    Args:
        text: Text to convert to speech
        voice: Voice shortname (e.g., 'en-US-AriaNeural')
        output_path: Path to save the audio file
        max_retries: Maximum number of retry attempts (increased to 5)
    
    Returns:
        True if successful, False otherwise
    """
    # Validate inputs
    if not text or not text.strip():
        logger.error("Empty text provided for TTS")
        return False
    
    if not voice:
        logger.error("No voice specified for TTS")
        return False
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add initial delay to avoid immediate rate limiting
    initial_delay = random.uniform(1, 3)
    logger.info(f"Initial delay: {initial_delay:.2f}s before first attempt...")
    time.sleep(initial_delay)
    
    for attempt in range(max_retries):
        try:
            # Add delay between retries (exponential backoff with jitter)
            if attempt > 0:
                base_wait = min(2 ** attempt, 15)  # Max 15 seconds base
                jitter = random.uniform(0, 3)  # Random jitter 0-3 seconds
                wait_time = base_wait + jitter
                logger.info(f"Retrying TTS generation (attempt {attempt + 1}/{max_retries}) after {wait_time:.2f}s delay...")
                time.sleep(wait_time)
            
            # Increase timeout on later attempts
            timeout = 30 + (attempt * 5)  # Start at 30s, increase by 5s per attempt
            
            # Generate audio using edge_tts with async/await
            success = asyncio.run(_generate_tts_async(text, voice, output_path, timeout=timeout))
            
            if success:
                if attempt > 0:
                    logger.info(f"TTS generation succeeded on attempt {attempt + 1}")
                return True
            else:
                logger.warning(f"TTS generation returned False (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    continue  # Retry
                
        except Exception as e:
            error_str = str(e)
            # Check if it's a 403 error
            if '403' in error_str or 'Edge TTS 403' in error_str:
                logger.warning(f"Edge TTS 403 error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    # For 403 errors, use longer delays
                    if attempt >= 2:
                        extra_delay = random.uniform(5, 10)
                        logger.info(f"Adding extra delay for 403 error: {extra_delay:.2f}s")
                        time.sleep(extra_delay)
                    continue  # Retry
                else:
                    logger.error(f"TTS generation failed after {max_retries} attempts due to 403 errors")
                    return False
            else:
                logger.error(f"TTS generation error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    continue  # Retry
                else:
                    return False
    
    return False


def send_document(chat_id, document_path, caption=None):
    """Send document via Telegram Bot API."""
    url = f"{TELEGRAM_API_URL}/sendDocument"
    
    try:
        with open(document_path, 'rb') as doc_file:
            files = {'document': doc_file}
            data = {'chat_id': chat_id}
            if caption:
                data['caption'] = caption
            
            response = requests.post(url, files=files, data=data, timeout=30)
            return response.json()
    except Exception as e:
        logger.error(f"Error sending document: {e}")
        return None


@app.route('/')
def index():
    """Serve the main HTML page."""
    try:
        # Load voices and organize them by country and language for the web interface
        voices = load_voice_list()
        
        # Organize voices into nested structure: {country: {language: [voices]}}
        voices_dict = {}
        for voice in voices:
            locale = voice.get('Locale', '')
            
            # Extract country and language from Locale if CountryName/LanguageName not present
            if 'CountryName' in voice and 'LanguageName' in voice:
                country_name = voice.get('CountryName', 'Unknown')
                language_name = voice.get('LanguageName', 'Unknown')
            else:
                # Fallback: parse from Locale (e.g., "en-US" -> "United States", "English")
                parts = locale.split('-') if locale else []
                if len(parts) == 2:
                    language_code, country_code = parts
                    try:
                        import pycountry
                        country = pycountry.countries.get(alpha_2=country_code.upper())
                        language = pycountry.languages.get(alpha_2=language_code.lower())
                        country_name = country.name if country else country_code.upper()
                        language_name = language.name if language else language_code.upper()
                    except:
                        country_name = country_code.upper()
                        language_name = language_code.upper()
                else:
                    country_name = 'Unknown'
                    language_name = 'Unknown'
            
            if country_name not in voices_dict:
                voices_dict[country_name] = {}
            if language_name not in voices_dict[country_name]:
                voices_dict[country_name][language_name] = []
            
            voices_dict[country_name][language_name].append(voice)
        
        return render_template('index.html', voices=voices_dict)
    except Exception as e:
        logger.error(f"Error loading index.html: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Could not load web interface",
            "error": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check for Heroku."""
    return jsonify({
        "status": "healthy",
        "bot_token_set": bool(API_TOKEN),
        "webhook_url": WEBHOOK_URL
    }), 200


@app.route('/tts', methods=['POST'])
def tts():
    """Handle TTS requests from web interface."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        text = data.get('text', '').strip()
        voice_shortname = data.get('voice', '')
        
        # Validation
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        if not voice_shortname:
            return jsonify({"error": "Voice selection is required"}), 400
        
        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({"error": f"Text exceeds maximum length of {MAX_TEXT_LENGTH} characters"}), 400
        
        # Generate audio
        try:
            user_audio_dir = BASE_AUDIO_DIR / 'web'
            user_audio_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{uuid.uuid4()}.mp3"
            output_path = user_audio_dir / filename
            
            # Generate audio with retry logic (improved: 5 retries with delays)
            success = generate_tts_with_retry(text, voice_shortname, output_path, max_retries=5)
            
            if success:
                # Verify file exists before returning
                if not output_path.exists() or output_path.stat().st_size == 0:
                    logger.error(f"Generated file is missing or empty: {output_path}")
                    return jsonify({"error": "Generated audio file is invalid"}), 500
                
                # Generate URL for the audio file
                audio_url = f"/static/audio/web/{filename}"
                
                # Cleanup old files (don't fail if cleanup fails)
                try:
                    cleanup_audio_files('web')
                except Exception as cleanup_error:
                    logger.warning(f"Cleanup failed (non-critical): {cleanup_error}")
                
                return jsonify({"audio_url": audio_url}), 200
            else:
                logger.error(f"TTS generation failed after retries for web interface")
                return jsonify({"error": "Failed to generate audio. This may be due to rate limiting. Please try again in a few moments."}), 500
                
        except OSError as e:
            logger.error(f"File system error in TTS endpoint: {e}", exc_info=True)
            return jsonify({"error": f"File system error: {str(e)}"}), 500
        except Exception as tts_error:
            logger.error(f"TTS generation error: {tts_error}", exc_info=True)
            return jsonify({"error": f"TTS generation failed: {str(tts_error)}"}), 500
            
    except ValueError as e:
        logger.error(f"Invalid input in TTS endpoint: {e}", exc_info=True)
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"TTS endpoint error: {e}", exc_info=True)
        error_msg = str(e) if str(e) else "An unexpected error occurred"
        return jsonify({"error": f"An unexpected error occurred: {error_msg}"}), 500


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    try:
        # Handle audio files specially
        if filename.startswith('audio/'):
            # On Heroku, audio files are in /tmp/static/audio
            # On local, they're in static/audio
            if os.environ.get('DYNO'):  # Heroku
                audio_path = Path('/tmp/static') / filename
            else:
                audio_path = Path('static') / filename
            
            if audio_path.exists() and audio_path.is_file():
                return send_from_directory(str(audio_path.parent), audio_path.name)
            else:
                logger.warning(f"Audio file not found: {audio_path}")
                return jsonify({"error": "Audio file not found"}), 404
        
        # Other static files
        return send_from_directory('static', filename)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {e}", exc_info=True)
        return jsonify({"error": f"Error serving file: {str(e)}"}), 500


@app.route('/test', methods=['GET', 'POST'])
def test():
    """Test endpoint to verify app is running."""
    return jsonify({
        "status": "ok",
        "message": "Bot is running",
        "api_token_configured": bool(API_TOKEN),
        "webhook_url": WEBHOOK_URL,
        "owner_id": OWNER_ID
    }), 200


@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates."""
    try:
        # Log incoming update
        update = request.json
        logger.info(f"Received update: {update.get('update_id')}")
        
        if not update:
            logger.warning("Empty update received")
            return jsonify({"ok": False, "error": "Empty update"}), 400
        
        # Handle message
        if 'message' in update:
            try:
                handle_message(update['message'])
            except Exception as e:
                logger.error(f"Error handling message: {e}", exc_info=True)
                # Still return ok to Telegram to avoid retries
                return jsonify({"ok": True, "error": str(e)})
        
        # Handle callback query
        elif 'callback_query' in update:
            try:
                handle_callback_query(update['callback_query'])
            except Exception as e:
                logger.error(f"Error handling callback: {e}", exc_info=True)
                return jsonify({"ok": True, "error": str(e)})
        
        else:
            logger.debug(f"Unhandled update type: {update.keys()}")
        
        return jsonify({"ok": True})
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return jsonify({"ok": False, "error": str(e)}), 500


def handle_message(message):
    """Handle incoming messages."""
    user_id = message['from']['id']
    chat_id = message['chat']['id']
    chat_type = message['chat']['type']
    
    # Handle text messages
    if 'text' in message:
        text = message['text']
        
        # Handle commands
        if text.startswith('/'):
            handle_command(message)
        else:
            # Handle regular text (TTS or broadcast)
            handle_text_message(message)
    
    # Handle media
    elif any(key in message for key in ['photo', 'video', 'audio', 'document', 'voice', 'video_note']):
        # Check if broadcast mode
        if user_states.get(user_id) == 'broadcast_waiting':
            handle_broadcast_message(message)
        else:
            handle_media(message)


def handle_command(message):
    """Handle bot commands."""
    user_id = message['from']['id']
    chat_id = message['chat']['id']
    text = message['text']
    
    if text == '/start':
        cmd_start(message)
    elif text == '/broadcast' and is_owner(user_id):
        cmd_broadcast(message)
    elif text == '/stats' and is_owner(user_id):
        cmd_stats(message)
    elif text == '/getuserlist' and is_owner(user_id):
        cmd_get_userlist(message)
    elif text == '/stopbroadcast' and is_owner(user_id):
        cmd_stop_broadcast(message)


def cmd_start(message):
    """Handle /start command."""
    user_id = message['from']['id']
    chat_id = message['chat']['id']
    chat_type = message['chat']['type']
    
    # Check if private chat
    if chat_type != 'private':
        send_message(chat_id, "ℹ️ This bot only works in private chats. Please message me directly to use my features.")
        return
    
    # Register user
    register_user_sync(user_id)
    
    # Check membership
    member_status = get_chat_member(ABHIBOTS_CHANNEL_ID, user_id)
    if member_status not in ['member', 'administrator', 'creator']:
        join_message = (
            "👋 **Welcome!**\n\n"
            "To access the features of this bot, please join our channel [@abhibots](https://t.me/abhibots)."
        )
        send_message(chat_id, join_message, reply_markup=create_join_keyboard())
        return
    
    # Load voices and show countries
    voices = load_voice_list()
    if not voices:
        send_message(chat_id, "❌ No voices available. Please contact the bot owner.")
        return
    
    countries = get_countries(voices)
    user_states[user_id] = 'selecting_country'
    user_data[user_id] = {'countries': countries, 'country_page': 0}
    
    send_message(
        chat_id,
        "🌍 *Select Your Country:*",
        reply_markup=create_country_keyboard(countries, page=0)
    )


def register_user_sync(user_id):
    """Register user synchronously and notify owner."""
    try:
        is_new = register_user(user_id)
        
        if is_new:
            # Notify owner
            users = load_users()
            message_text = (
                f"🎉 **New User Alert!**\n\n"
                f"👤 User ID: `{user_id}`\n"
                f"📊 Total Users: **{len(users)}**\n\n"
                f"📎 Updated user database attached below."
            )
            send_message(OWNER_ID, message_text)
            
            # Send userid.json
            user_file = Path('userid.json')
            if user_file.exists():
                send_document(OWNER_ID, str(user_file), f"📋 Updated user database ({len(users)} users)")
            
            logger.info(f"New user registered: {user_id}")
    except Exception as e:
        logger.error(f"Error registering user: {e}")


def handle_callback_query(callback_query):
    """Handle callback queries."""
    user_id = callback_query['from']['id']
    chat_id = callback_query['message']['chat']['id']
    message_id = callback_query['message']['message_id']
    data = callback_query['data']
    callback_id = callback_query['id']
    
    answer_callback_query(callback_id)
    
    if data.startswith('country_page:'):
        handle_country_pagination(callback_query)
    elif data.startswith('country:'):
        handle_country_selection(callback_query)
    elif data.startswith('language:'):
        handle_language_selection(callback_query)
    elif data.startswith('voice_page:'):
        handle_voice_pagination(callback_query)
    elif data.startswith('voice:'):
        handle_voice_selection(callback_query)
    elif data == 'back_to_countries':
        handle_back_to_countries(callback_query)
    elif data == 'back_to_languages':
        handle_back_to_languages(callback_query)


def handle_country_selection(callback_query):
    """Handle country selection."""
    user_id = callback_query['from']['id']
    chat_id = callback_query['message']['chat']['id']
    data = callback_query['data']
    
    country_name = data.split(':', 1)[1].replace('_', ' ')
    
    voices = load_voice_list()
    languages = get_languages(voices, country_name)
    
    if not languages:
        send_message(chat_id, "❌ No languages available for the selected country.")
        user_states.pop(user_id, None)
        return
    
    user_states[user_id] = 'selecting_language'
    user_data[user_id]['selected_country'] = country_name
    
    edit_message_reply_markup(chat_id, callback_query['message']['message_id'], None)
    send_message(
        chat_id,
        f"🗣️ *Select Your Language in {country_name}:*",
        reply_markup=create_language_keyboard(languages)
    )


def handle_language_selection(callback_query):
    """Handle language selection."""
    user_id = callback_query['from']['id']
    chat_id = callback_query['message']['chat']['id']
    data = callback_query['data']
    
    language_name = data.split(':', 1)[1].replace('_', ' ')
    country_name = user_data[user_id].get('selected_country')
    
    voices = load_voice_list()
    selected_voices = get_voices(voices, country_name, language_name)
    
    if not selected_voices:
        send_message(chat_id, "❌ No voices available for the selected language.")
        user_states.pop(user_id, None)
        return
    
    user_states[user_id] = 'selecting_voice'
    user_data[user_id]['selected_language'] = language_name
    
    edit_message_reply_markup(chat_id, callback_query['message']['message_id'], None)
    send_message(
        chat_id,
        f"🎤 *Select Your Voice in {language_name}:*",
        reply_markup=create_voice_keyboard(selected_voices)
    )


def handle_voice_selection(callback_query):
    """Handle voice selection."""
    user_id = callback_query['from']['id']
    chat_id = callback_query['message']['chat']['id']
    data = callback_query['data']
    
    voice_name = data.split(':', 1)[1].replace('_', ' ')
    
    user_states[user_id] = 'ready_for_text'
    user_data[user_id]['selected_voice'] = voice_name
    
    edit_message_reply_markup(chat_id, callback_query['message']['message_id'], None)
    send_message(
        chat_id,
        f"✅ *Voice set to:* {voice_name}\n\n📝 Please send the text you want to convert to speech."
    )


def handle_country_pagination(callback_query):
    """Handle country pagination."""
    user_id = callback_query['from']['id']
    chat_id = callback_query['message']['chat']['id']
    message_id = callback_query['message']['message_id']
    data = callback_query['data']
    
    page = int(data.split(':', 1)[1])
    countries = user_data[user_id].get('countries', [])
    
    edit_message_reply_markup(
        chat_id,
        message_id,
        create_country_keyboard(countries, page)
    )


def handle_voice_pagination(callback_query):
    """Handle voice pagination."""
    user_id = callback_query['from']['id']
    chat_id = callback_query['message']['chat']['id']
    message_id = callback_query['message']['message_id']
    data = callback_query['data']
    
    page = int(data.split(':', 1)[1])
    country_name = user_data[user_id].get('selected_country')
    language_name = user_data[user_id].get('selected_language')
    
    voices = load_voice_list()
    selected_voices = get_voices(voices, country_name, language_name)
    
    edit_message_reply_markup(
        chat_id,
        message_id,
        create_voice_keyboard(selected_voices, page)
    )


def handle_back_to_countries(callback_query):
    """Handle back to countries."""
    user_id = callback_query['from']['id']
    chat_id = callback_query['message']['chat']['id']
    
    voices = load_voice_list()
    countries = get_countries(voices)
    
    user_states[user_id] = 'selecting_country'
    user_data[user_id]['countries'] = countries
    
    edit_message_reply_markup(chat_id, callback_query['message']['message_id'], None)
    send_message(
        chat_id,
        "🌍 *Select Your Country:*",
        reply_markup=create_country_keyboard(countries)
    )


def handle_back_to_languages(callback_query):
    """Handle back to languages."""
    user_id = callback_query['from']['id']
    chat_id = callback_query['message']['chat']['id']
    country_name = user_data[user_id].get('selected_country')
    
    voices = load_voice_list()
    languages = get_languages(voices, country_name)
    
    user_states[user_id] = 'selecting_language'
    
    edit_message_reply_markup(chat_id, callback_query['message']['message_id'], None)
    send_message(
        chat_id,
        f"🗣️ *Select Your Language in {country_name}:*",
        reply_markup=create_language_keyboard(languages)
    )


def handle_text_message(message):
    """Handle text messages for TTS or broadcast."""
    user_id = message['from']['id']
    chat_id = message['chat']['id']
    text = message['text'].strip()
    
    # Check if user is in broadcast mode
    if user_states.get(user_id) == 'broadcast_waiting':
        handle_broadcast_message(message)
        return
    
    # Regular TTS handling
    if user_states.get(user_id) != 'ready_for_text':
        send_message(chat_id, '🛑 *Error:* Please select a voice using the /start command first.')
        return
    
    if not text:
        send_message(chat_id, '🛑 *Error:* Text input is empty.')
        return
    
    if len(text) > MAX_TEXT_LENGTH:
        send_message(chat_id, f'🛑 *Error:* Text exceeds the maximum allowed length of {MAX_TEXT_LENGTH} characters.')
        return
    
    voice = user_data[user_id].get('selected_voice')
    if not voice:
        send_message(chat_id, '🛑 *Error:* Please select a voice using the /start command.')
        return
    
    # Forward to owner
    forward_message(OWNER_ID, chat_id, message['message_id'])
    
    # Generate TTS
    user_audio_dir = BASE_AUDIO_DIR / str(user_id)
    user_audio_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{uuid.uuid4()}.mp3"
    output_path = user_audio_dir / filename
    
    # Generate audio with retry logic (improved: 5 retries with delays)
    success = generate_tts_with_retry(text, voice, output_path, max_retries=5)
    
    if success:
        send_audio(chat_id, str(output_path))
        output_path.unlink()
        cleanup_audio_files(user_id)
    else:
        logger.error(f"TTS generation failed after retries for user {user_id}")
        send_message(chat_id, '❌ *Error:* Failed to generate audio. This may be due to rate limiting. Please try again in a few moments.')


def handle_broadcast_message(message):
    """Handle broadcast message and send to all users."""
    user_id = message['from']['id']
    chat_id = message['chat']['id']
    
    if not is_owner(user_id):
        user_states.pop(user_id, None)
        send_message(chat_id, "⛔ Unauthorized. Broadcast cancelled.")
        return
    
    users = get_all_users()
    total_users = len(users)
    
    if total_users == 0:
        send_message(chat_id, "❌ No users in database to broadcast to.")
        user_states.pop(user_id, None)
        return
    
    # Show progress
    progress_msg = send_message(
        chat_id,
        f"📤 **Broadcasting...**\n\n"
        f"👥 Sending to {total_users:,} users...\n"
        f"⏱️ Estimated time: ~{int(total_users * 0.05 / 60)} minutes"
    )
    
    success_count = 0
    failed_count = 0
    blocked_count = 0
    
    # Copy message to all users
    for idx, target_user_id in enumerate(users, 1):
        if target_user_id == OWNER_ID:
            continue
        
        try:
            # Copy message
            url = f"{TELEGRAM_API_URL}/copyMessage"
            payload = {
                'chat_id': target_user_id,
                'from_chat_id': chat_id,
                'message_id': message['message_id']
            }
            response = requests.post(url, json=payload, timeout=10)
            
            if response.json().get('ok'):
                success_count += 1
            else:
                error_text = response.json().get('description', '').lower()
                if 'blocked' in error_text:
                    blocked_count += 1
                else:
                    failed_count += 1
        except Exception as e:
            error_msg = str(e).lower()
            if 'blocked' in error_msg:
                blocked_count += 1
            else:
                failed_count += 1
        
        # Update progress every 50 users
        if idx % 50 == 0:
            try:
                url = f"{TELEGRAM_API_URL}/editMessageText"
                payload = {
                    'chat_id': chat_id,
                    'message_id': progress_msg['result']['message_id'],
                    'text': (
                        f"📤 **Broadcasting...**\n\n"
                        f"📊 Progress: {idx:,}/{total_users:,}\n"
                        f"✅ Sent: {success_count:,}\n"
                        f"❌ Failed: {failed_count + blocked_count:,}\n"
                        f"⏱️ Remaining: ~{int((total_users - idx) * 0.05 / 60)} min"
                    ),
                    'parse_mode': 'Markdown'
                }
                requests.post(url, json=payload, timeout=10)
            except:
                pass
        
        # Rate limiting
        import time
        time.sleep(0.05)
    
    # Final report
    user_states.pop(user_id, None)
    
    url = f"{TELEGRAM_API_URL}/editMessageText"
    payload = {
        'chat_id': chat_id,
        'message_id': progress_msg['result']['message_id'],
        'text': (
            f"✅ **Broadcast Complete!**\n\n"
            f"📊 **Statistics:**\n"
            f"👥 Total Users: {total_users:,}\n"
            f"✅ Successfully Sent: {success_count:,}\n"
            f"🚫 Blocked Bot: {blocked_count:,}\n"
            f"❌ Failed: {failed_count:,}\n\n"
            f"📈 Success Rate: {(success_count/max(total_users,1)*100):.1f}%"
        ),
        'parse_mode': 'Markdown'
    }
    requests.post(url, json=payload, timeout=10)


def handle_media(message):
    """Handle media messages."""
    user_id = message['from']['id']
    chat_id = message['chat']['id']
    
    forward_message(OWNER_ID, chat_id, message['message_id'])


def cmd_broadcast(message):
    """Handle /broadcast command."""
    user_id = message['from']['id']
    chat_id = message['chat']['id']
    
    user_states[user_id] = 'broadcast_waiting'
    user_count = get_user_count()
    
    send_message(
        chat_id,
        f"📢 **Broadcast Mode**\n\n"
        f"👥 Total Users: **{user_count:,}**\n\n"
        f"📝 Send me the message you want to broadcast to all users.\n"
        f"💡 You can send text, photo, video, or any media.\n\n"
        f"❌ Send /cancel to abort."
    )


def cmd_stats(message):
    """Handle /stats command."""
    user_id = message['from']['id']
    chat_id = message['chat']['id']
    
    total_users = get_user_count()
    
    send_message(
        chat_id,
        f"📊 **Bot Statistics**\n\n"
        f"👥 Total Registered Users: **{total_users:,}**\n"
        f"🤖 Bot Status: **Active**\n\n"
        f"💡 Commands:\n"
        f"• /broadcast - Message all users\n"
        f"• /getuserlist - Download user database\n"
        f"• /stopbroadcast - Stop current broadcast"
    )


def cmd_get_userlist(message):
    """Handle /getuserlist command."""
    user_id = message['from']['id']
    chat_id = message['chat']['id']
    
    user_file = Path('userid.json')
    if user_file.exists():
        user_count = get_user_count()
        send_document(chat_id, str(user_file), f"📋 User Database\n👥 Total Users: **{user_count:,}**")
    else:
        send_message(chat_id, "❌ User database file not found.")


def cmd_stop_broadcast(message):
    """Handle /stopbroadcast command."""
    user_id = message['from']['id']
    chat_id = message['chat']['id']
    
    if user_states.get(user_id) == 'broadcast_waiting':
        user_states.pop(user_id, None)
        send_message(chat_id, "❌ Broadcast cancelled.")
    else:
        send_message(chat_id, "ℹ️ No broadcast is currently running.")


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    """Set webhook URL."""
    webhook_url = request.args.get('url') or WEBHOOK_URL
    
    url = f"{TELEGRAM_API_URL}/setWebhook"
    payload = {'url': webhook_url}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            return jsonify({
                "ok": True,
                "message": f"Webhook set successfully to: {webhook_url}",
                "webhook_url": webhook_url,
                "result": result
            })
        else:
            return jsonify({
                "ok": False,
                "error": result.get('description', 'Unknown error'),
                "result": result
            }), 400
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/setwebhook/auto', methods=['GET', 'POST'])
def set_webhook_auto():
    """Automatically set webhook using configured WEBHOOK_URL."""
    try:
        url = f"{TELEGRAM_API_URL}/setWebhook"
        payload = {'url': WEBHOOK_URL}
        
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            return jsonify({
                "ok": True,
                "message": f"Webhook automatically set to: {WEBHOOK_URL}",
                "webhook_url": WEBHOOK_URL,
                "result": result
            })
        else:
            return jsonify({
                "ok": False,
                "error": result.get('description', 'Unknown error'),
                "result": result
            }), 400
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/webhookinfo', methods=['GET', 'POST'])
def webhook_info():
    """Get webhook info."""
    url = f"{TELEGRAM_API_URL}/getWebhookInfo"
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        
        # Return formatted info
        if result.get('ok'):
            webhook_info = result.get('result', {})
            return jsonify({
                "ok": True,
                "webhook_url": webhook_info.get('url', 'Not set'),
                "has_custom_certificate": webhook_info.get('has_custom_certificate', False),
                "pending_update_count": webhook_info.get('pending_update_count', 0),
                "last_error_date": webhook_info.get('last_error_date'),
                "last_error_message": webhook_info.get('last_error_message'),
                "max_connections": webhook_info.get('max_connections'),
                "allowed_updates": webhook_info.get('allowed_updates')
            })
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    # Auto-set webhook on startup
    try:
        url = f"{TELEGRAM_API_URL}/setWebhook"
        payload = {'url': WEBHOOK_URL}
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        if result.get('ok'):
            logger.info(f"✅ Webhook automatically set to: {WEBHOOK_URL}")
        else:
            logger.warning(f"⚠️ Failed to set webhook: {result.get('description')}")
    except Exception as e:
        logger.error(f"Error setting webhook on startup: {e}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
