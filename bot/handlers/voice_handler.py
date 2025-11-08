"""
Voice selection handlers
"""
import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from ..states import VoiceSelection
from ..utils import load_voice_list, get_voices
from ..keyboards import create_voice_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('voice_page:'))
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


@router.callback_query(F.data.startswith('voice:'))
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

