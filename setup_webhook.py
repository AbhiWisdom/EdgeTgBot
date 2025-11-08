#!/usr/bin/env python3
"""
Quick script to set webhook for Heroku deployment
"""
import os
import asyncio
import sys
from aiogram import Bot

async def set_webhook():
    """Set webhook URL."""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    webhook_url = os.environ.get('WEBHOOK_URL')
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set")
        sys.exit(1)
    
    if not webhook_url:
        print("❌ Error: WEBHOOK_URL environment variable not set")
        print("💡 Set it with: heroku config:set WEBHOOK_URL='https://your-app.herokuapp.com/webhook'")
        sys.exit(1)
    
    bot = Bot(token=token)
    
    try:
        # Delete existing webhook first
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Cleared existing webhook")
        
        # Set new webhook
        await bot.set_webhook(webhook_url)
        print(f"✅ Webhook set to: {webhook_url}")
        
        # Get webhook info
        info = await bot.get_webhook_info()
        print(f"\n📊 Webhook Info:")
        print(f"   URL: {info.url}")
        print(f"   Pending Updates: {info.pending_update_count}")
        print(f"   Last Error: {info.last_error_message or 'None'}")
        
        if info.pending_update_count > 0:
            print(f"\n⚠️  Warning: {info.pending_update_count} pending updates will be processed")
        
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        sys.exit(1)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(set_webhook())

