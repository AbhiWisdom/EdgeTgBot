"""
Broadcast handler - allows owner to send messages to all users
"""
import asyncio
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..user_manager import get_all_users, is_owner, get_user_count
from ..config import OWNER_ID

logger = logging.getLogger(__name__)
router = Router()

# Track if a broadcast is currently running
_broadcast_running = False


class BroadcastState(StatesGroup):
    """States for broadcast flow"""
    waiting_for_message = State()


@router.message(Command("broadcast"), F.from_user.id == OWNER_ID)
async def cmd_broadcast(message: types.Message, state: FSMContext):
    """Start broadcast process (owner only)."""
    global _broadcast_running
    
    # Check if a broadcast is already running
    if _broadcast_running:
        await message.answer(
            "⚠️ **Broadcast Already Running**\n\n"
            "Please wait for the current broadcast to complete.\n"
            "Use /stopbroadcast to cancel it.",
            parse_mode='Markdown'
        )
        return
    
    user_count = get_user_count()
    await state.set_state(BroadcastState.waiting_for_message)
    await message.answer(
        f"📢 **Broadcast Mode**\n\n"
        f"👥 Total Users: **{user_count:,}**\n\n"
        f"📝 Send me the message you want to broadcast to all users.\n"
        f"💡 You can send text, photo, video, or any media.\n\n"
        f"❌ Send /cancel to abort.",
        parse_mode='Markdown'
    )


@router.message(Command("cancel"), BroadcastState.waiting_for_message, F.from_user.id == OWNER_ID)
async def cancel_broadcast(message: types.Message, state: FSMContext):
    """Cancel broadcast operation."""
    await state.clear()
    await message.answer("❌ Broadcast cancelled.")


@router.message(Command("stopbroadcast"), F.from_user.id == OWNER_ID)
async def stop_broadcast(message: types.Message, state: FSMContext):
    """Stop any running broadcast."""
    global _broadcast_running
    
    if _broadcast_running:
        _broadcast_running = False
        await state.clear()
        await message.answer("🛑 Broadcast stopped. It may take a few seconds to fully stop.")
    else:
        await message.answer("ℹ️ No broadcast is currently running.")


@router.message(BroadcastState.waiting_for_message, F.from_user.id == OWNER_ID)
async def process_broadcast(message: types.Message, state: FSMContext):
    """Process and send broadcast message to all users."""
    global _broadcast_running
    
    if _broadcast_running:
        await message.answer("⚠️ A broadcast is already running. Please wait for it to complete.")
        return
    
    await _execute_broadcast(message, state)


async def _execute_broadcast(message: types.Message, state: FSMContext):
    """Execute broadcast to all users."""
    global _broadcast_running
    
    _broadcast_running = True
    
    try:
        users = get_all_users()
        total_users = len(users)
        
        if total_users == 0:
            await message.answer("❌ No users in database to broadcast to.")
            await state.clear()
            return
        
        # Show progress message
        progress_msg = await message.answer(
            f"📤 **Broadcasting...**\n\n"
            f"👥 Sending to {total_users:,} users...\n"
            f"⏱️ Estimated time: ~{int(total_users * 0.05 / 60)} minutes",
            parse_mode='Markdown'
        )
        
        # Broadcast statistics
        success_count = 0
        failed_count = 0
        blocked_count = 0
        
        # Send to all users
        for idx, user_id in enumerate(users, 1):
            # Check if broadcast was stopped
            if not _broadcast_running:
                await progress_msg.edit_text(
                    f"🛑 **Broadcast Stopped**\n\n"
                    f"📊 Sent to {success_count}/{idx} users before stopping.",
                    parse_mode='Markdown'
                )
                await state.clear()
                return
            
            try:
                # Don't send to owner
                if user_id == OWNER_ID:
                    continue
                    
                # Copy message to user
                await message.copy_to(user_id)
                success_count += 1
                
                # Update progress every 50 users
                if idx % 50 == 0:
                    try:
                        await progress_msg.edit_text(
                            f"📤 **Broadcasting...**\n\n"
                            f"📊 Progress: {idx:,}/{total_users:,}\n"
                            f"✅ Sent: {success_count:,}\n"
                            f"❌ Failed: {failed_count + blocked_count:,}\n"
                            f"⏱️ Remaining: ~{int((total_users - idx) * 0.05 / 60)} min",
                            parse_mode='Markdown'
                        )
                    except Exception:
                        pass  # Ignore edit errors
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.05)
                
            except Exception as e:
                error_msg = str(e).lower()
                if 'blocked' in error_msg or 'bot was blocked' in error_msg:
                    blocked_count += 1
                    logger.warning(f"User {user_id} blocked the bot")
                else:
                    failed_count += 1
                    logger.error(f"Failed to send to user {user_id}: {e}")
        
        # Final report
        await state.clear()
        
        report = (
            f"✅ **Broadcast Complete!**\n\n"
            f"📊 **Statistics:**\n"
            f"👥 Total Users: {total_users:,}\n"
            f"✅ Successfully Sent: {success_count:,}\n"
            f"🚫 Blocked Bot: {blocked_count:,}\n"
            f"❌ Failed: {failed_count:,}\n\n"
            f"📈 Success Rate: {(success_count/max(total_users,1)*100):.1f}%"
        )
        
        await progress_msg.edit_text(report, parse_mode='Markdown')
        logger.info(f"Broadcast completed: {success_count}/{total_users} successful")
        
    finally:
        _broadcast_running = False


@router.message(Command("stats"), F.from_user.id == OWNER_ID)
async def cmd_stats(message: types.Message):
    """Show bot statistics (owner only)."""
    
    total_users = get_user_count()
    
    stats_message = (
        f"📊 **Bot Statistics**\n\n"
        f"👥 Total Registered Users: **{total_users:,}**\n"
        f"🤖 Bot Status: **Active**\n\n"
        f"💡 Commands:\n"
        f"• /broadcast - Message all users\n"
        f"• /getuserlist - Download user database\n"
        f"• /stopbroadcast - Stop current broadcast"
    )
    
    await message.answer(stats_message, parse_mode='Markdown')


@router.message(Command("getuserlist"), F.from_user.id == OWNER_ID)
async def cmd_get_userlist(message: types.Message):
    """Send userid.json to owner."""
    
    try:
        from pathlib import Path
        from aiogram.types import FSInputFile
        
        user_file_path = Path('userid.json')
        if user_file_path.exists():
            user_file = FSInputFile(str(user_file_path))
            user_count = get_user_count()
            await message.answer_document(
                user_file,
                caption=f"📋 User Database\n👥 Total Users: **{user_count:,}**",
                parse_mode='Markdown'
            )
        else:
            await message.answer("❌ User database file not found.")
    except Exception as e:
        logger.error(f"Error sending user list: {e}")
        await message.answer("❌ Error retrieving user list.")
