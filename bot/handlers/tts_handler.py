"""
Text-to-Speech handler
"""
import logging
import uuid
from pathlib import Path
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
import edge_tts

from ..config import BASE_AUDIO_DIR, OWNER_ID, MAX_TEXT_LENGTH
from ..states import VoiceSelection
from ..utils import cleanup_audio_files

logger = logging.getLogger(__name__)
router = Router()


@router.message(VoiceSelection.ready_for_text, F.text)
async def handle_text(message: types.Message, state: FSMContext):
    """Handle text messages for TTS."""
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Input validation
    if not text:
        await message.reply('🛑 *Error:* Text input is empty.', parse_mode='Markdown')
        return
    
    if len(text) > MAX_TEXT_LENGTH:
        await message.reply(
            f'🛑 *Error:* Text exceeds the maximum allowed length of {MAX_TEXT_LENGTH} characters.',
            parse_mode='Markdown'
        )
        return
    
    # Get selected voice from state
    data = await state.get_data()
    voice = data.get('selected_voice')
    
    if not voice:
        await message.reply(
            '🛑 *Error:* Please select a voice using the /start command.',
            parse_mode='Markdown'
        )
        return
    
    # Create user-specific audio directory
    user_audio_dir = BASE_AUDIO_DIR / str(user_id)
    user_audio_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate a unique filename
    filename = f"{uuid.uuid4()}.mp3"
    output_path = user_audio_dir / filename
    
    try:
        # Forward message to owner
        await message.bot.forward_message(OWNER_ID, message.chat.id, message.message_id)
        
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
            await message.reply(
                '⚠️ *Warning:* The generated audio file is empty. Please try again.',
                parse_mode='Markdown'
            )
        
        # Cleanup old audio files
        cleanup_audio_files(user_id)
    except Exception as e:
        logger.error(f"Unexpected Error during TTS generation for user {user_id}: {e}")
        await message.reply(
            '❌ *Error:* An unexpected error occurred. Please try again later.',
            parse_mode='Markdown'
        )


@router.message(F.text)
async def handle_other_text(message: types.Message, state: FSMContext):
    """Handle text messages when not in ready_for_text state."""
    await message.reply(
        '🛑 *Error:* Please select a voice using the /start command first.',
        parse_mode='Markdown'
    )

