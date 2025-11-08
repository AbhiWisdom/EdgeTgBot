#!/usr/bin/env python3
"""
Quick script to set webhook - Pure Flask version
"""
import os
import sys
import requests

# Import config
try:
    from bot.config import API_TOKEN, WEBHOOK_URL
except ImportError:
    print("❌ Error: Could not import bot.config")
    sys.exit(1)

def set_webhook():
    """Set webhook URL."""
    if not API_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)
    
    if not WEBHOOK_URL:
        print("❌ Error: WEBHOOK_URL not set")
        print("💡 Set it in bot/config.py or as environment variable")
        sys.exit(1)
    
    url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook"
    payload = {'url': WEBHOOK_URL}
    
    try:
        print(f"📤 Setting webhook to: {WEBHOOK_URL}")
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            print(f"✅ Webhook set successfully!")
            print(f"   URL: {WEBHOOK_URL}")
            
            # Get webhook info
            info_url = f"https://api.telegram.org/bot{API_TOKEN}/getWebhookInfo"
            info_response = requests.get(info_url, timeout=10)
            info = info_response.json()
            
            if info.get('ok'):
                webhook_info = info.get('result', {})
                print(f"\n📊 Webhook Info:")
                print(f"   URL: {webhook_info.get('url')}")
                print(f"   Pending Updates: {webhook_info.get('pending_update_count', 0)}")
                if webhook_info.get('last_error_message'):
                    print(f"   ⚠️ Last Error: {webhook_info.get('last_error_message')}")
        else:
            print(f"❌ Failed to set webhook: {result.get('description', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        sys.exit(1)

if __name__ == '__main__':
    set_webhook()
