"""
Flask webhook app for Telegram TTS Bot - Heroku Compatible
"""
import os
import logging
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
import asyncio

from bot.config import API_TOKEN
from bot.handlers import all_routers

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Bot and Dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Register all routers
for router in all_routers:
    dp.include_router(router)

logger.info(f"Registered {len(all_routers)} routers")


@app.route('/')
def index():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "bot": "Telegram TTS Bot",
        "version": "2.0",
        "mode": "webhook"
    })


@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates."""
    try:
        update_dict = request.json
        update = Update(**update_dict)
        
        # Run async handler in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(dp.feed_update(bot, update))
        finally:
            loop.close()
        
        return jsonify({"ok": True})
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    """Set webhook URL (for initial setup)."""
    webhook_url = os.environ.get('WEBHOOK_URL', request.args.get('url'))
    
    if not webhook_url:
        return jsonify({
            "error": "WEBHOOK_URL environment variable not set or url parameter missing"
        }), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(bot.set_webhook(webhook_url))
            webhook_info = loop.run_until_complete(bot.get_webhook_info())
            return jsonify({
                "ok": True,
                "webhook_url": webhook_url,
                "webhook_info": {
                    "url": webhook_info.url,
                    "has_custom_certificate": webhook_info.has_custom_certificate,
                    "pending_update_count": webhook_info.pending_update_count
                }
            })
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/webhookinfo', methods=['GET'])
def webhook_info():
    """Get current webhook info."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            info = loop.run_until_complete(bot.get_webhook_info())
            return jsonify({
                "url": info.url,
                "has_custom_certificate": info.has_custom_certificate,
                "pending_update_count": info.pending_update_count,
                "last_error_date": info.last_error_date,
                "last_error_message": info.last_error_message,
                "max_connections": info.max_connections,
                "allowed_updates": info.allowed_updates
            })
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check for Heroku."""
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
