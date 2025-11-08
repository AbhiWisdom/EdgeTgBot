"""
Main entry point for the Telegram TTS Bot
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import API_TOKEN
from bot.handlers import all_routers


# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot."""
    logger.info("Starting Telegram TTS Bot...")
    
    # Initialize Bot and Dispatcher
    bot = Bot(token=API_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register all routers
    for router in all_routers:
        dp.include_router(router)
    
    logger.info(f"Registered {len(all_routers)} routers")
    logger.info("Bot is now running. Press Ctrl+C to stop.")
    
    # Start polling
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")

