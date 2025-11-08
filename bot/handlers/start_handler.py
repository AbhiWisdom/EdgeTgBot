"""
Start command handler
"""
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ..config import ABHIBOTS_CHANNEL_ID
from ..states import VoiceSelection
from ..utils import load_voice_list, get_countries
from ..keyboards import create_country_keyboard, create_join_keyboard
from ..user_manager import register_user

logger = logging.getLogger(__name__)
router = Router()


async def check_membership(bot, user_id: int) -> bool:
    """Check if the user is a member of the specified channel."""
    try:
        member = await bot.get_chat_member(ABHIBOTS_CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking membership for user {user_id}: {e}")
        return False


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handle /start command."""
    user_id = message.from_user.id
    
    # Clear any existing state (important for broadcast/other states)
    await state.clear()
    
    # Check if it's a private chat
    if message.chat.type != 'private':
        await message.reply(
            "ℹ️ This bot only works in private chats. Please message me directly to use my features."
        )
        return

    # Register user (will notify owner if new)
    is_new_user = await register_user(user_id, message.bot)
    if is_new_user:
        logger.info(f"New user registered: {user_id}")
    
    # Check membership
    is_member = await check_membership(message.bot, user_id)
    if not is_member:
        join_message = (
            "👋 **Welcome!**\n\n"
            "To access the features of this bot, please join our channel [@abhibots](https://t.me/abhibots)."
        )
        await message.answer(
            join_message,
            parse_mode='Markdown',
            reply_markup=create_join_keyboard()
        )
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

