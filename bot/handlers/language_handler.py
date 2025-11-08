"""
Language selection handlers
"""
import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from ..states import VoiceSelection
from ..utils import load_voice_list, get_voices
from ..keyboards import create_voice_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('language:'))
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

