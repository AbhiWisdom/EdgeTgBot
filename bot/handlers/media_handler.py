"""
Media forwarding handler
"""
import logging
from aiogram import Router, types, F

from ..config import OWNER_ID

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.content_type.in_(['photo', 'video', 'audio', 'document', 'voice', 'video_note']))
async def handle_media(message: types.Message):
    """Forward any media sent by the user to the owner."""
    try:
        await message.bot.forward_message(OWNER_ID, message.chat.id, message.message_id)
        logger.info(f"Forwarded {message.content_type} from {message.from_user.id} to owner.")
    except Exception as e:
        logger.error(f"Error forwarding message from {message.from_user.id}: {e}")

