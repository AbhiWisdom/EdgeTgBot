"""
Country selection handlers
"""
import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from ..states import VoiceSelection
from ..utils import load_voice_list, get_languages
from ..keyboards import create_country_keyboard, create_language_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('country_page:'))
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


@router.callback_query(F.data.startswith('country:'))
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

