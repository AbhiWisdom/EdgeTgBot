#!/usr/bin/env python3
"""
Quick webhook setup script for Heroku
"""
import os
import sys
import requests

try:
    from bot.config import API_TOKEN, WEBHOOK_URL
except ImportError:
    API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://ttsbot-a572faff13b4.herokuapp.com/webhook')

def main():
    if not API_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set")
        print("Set it with: heroku config:set TELEGRAM_BOT_TOKEN='your_token'")
        sys.exit(1)
    
    print("=" * 60)
    print("Setting Telegram Webhook")
    print("=" * 60)
    print(f"Bot Token: {API_TOKEN[:10]}...")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print()
    
    # Set webhook
    url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook"
    payload = {'url': WEBHOOK_URL}
    
    try:
        print("📤 Setting webhook...")
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook set successfully!")
            print()
            
            # Get webhook info
            info_url = f"https://api.telegram.org/bot{API_TOKEN}/getWebhookInfo"
            info_response = requests.get(info_url, timeout=10)
            info = info_response.json()
            
            if info.get('ok'):
                webhook_info = info.get('result', {})
                print("📊 Webhook Status:")
                print(f"   URL: {webhook_info.get('url', 'Not set')}")
                print(f"   Pending Updates: {webhook_info.get('pending_update_count', 0)}")
                
                if webhook_info.get('last_error_message'):
                    print(f"   ⚠️  Last Error: {webhook_info.get('last_error_message')}")
                else:
                    print("   ✅ No errors")
                
                print()
                print("🎉 Bot is ready! Send /start to your bot to test.")
        else:
            print(f"❌ Failed to set webhook: {result.get('description', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
