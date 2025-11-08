"""
User management utilities - tracking and broadcasting
"""
import json
import logging
import os
from pathlib import Path
from typing import List, Set
from aiogram.types import FSInputFile

from .config import OWNER_ID

logger = logging.getLogger(__name__)

# Use /tmp for Heroku (ephemeral) or local for development
if os.environ.get('DYNO'):  # Heroku detection
    USER_DB_PATH = Path('/tmp/userid.json')
else:
    USER_DB_PATH = Path('userid.json')


def load_users() -> Set[int]:
    """Load user IDs from JSON file."""
    try:
        if USER_DB_PATH.exists():
            with open(USER_DB_PATH, 'r') as f:
                users = json.load(f)
                return set(users)
        else:
            logger.warning(f"{USER_DB_PATH} not found, creating new file")
            return set()
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        return set()


def save_users(users: Set[int]) -> bool:
    """Save user IDs to JSON file."""
    try:
        users_list = sorted(list(users))
        with open(USER_DB_PATH, 'w') as f:
            json.dump(users_list, f, indent=4)
        logger.info(f"Saved {len(users_list)} users to {USER_DB_PATH}")
        return True
    except Exception as e:
        logger.error(f"Error saving users: {e}")
        return False


async def register_user(user_id: int, bot) -> bool:
    """
    Register a new user and notify owner if new.
    Returns True if user is new, False if already exists.
    """
    users = load_users()
    
    if user_id in users:
        return False  # User already exists
    
    # Add new user
    users.add(user_id)
    save_users(users)
    
    # Notify owner about new user
    try:
        message = (
            f"🎉 **New User Alert!**\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"📊 Total Users: **{len(users)}**\n\n"
            f"📎 Updated user database attached below."
        )
        await bot.send_message(OWNER_ID, message, parse_mode='Markdown')
        
        # Send updated userid.json to owner
        if USER_DB_PATH.exists():
            user_file = FSInputFile(str(USER_DB_PATH))
            await bot.send_document(
                OWNER_ID,
                user_file,
                caption=f"📋 Updated user database ({len(users)} users)"
            )
        
        logger.info(f"New user {user_id} registered. Total users: {len(users)}")
        return True
        
    except Exception as e:
        logger.error(f"Error notifying owner about new user {user_id}: {e}")
        return True  # User was still added


def get_all_users() -> List[int]:
    """Get list of all registered users."""
    users = load_users()
    return sorted(list(users))


def get_user_count() -> int:
    """Get total number of registered users."""
    users = load_users()
    return len(users)


def is_owner(user_id: int) -> bool:
    """Check if user is the bot owner."""
    return user_id == OWNER_ID

