"""
Navigation handlers (back buttons)
"""
import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from ..states import VoiceSelection
from ..utils import load_voice_list, get_countries, get_languages
from ..keyboards import create_country_keyboard, create_language_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'back_to_countries')
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


@router.callback_query(F.data == 'back_to_languages')
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

