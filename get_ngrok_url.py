#!/usr/bin/env python3
"""Get ngrok URL and set webhook"""
import requests
import time
import sys
from bot.config import API_TOKEN

print("Getting ngrok URL...")
for i in range(10):
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            https_tunnels = [t for t in tunnels if t.get('proto') == 'https']
            if https_tunnels:
                url = https_tunnels[0]['public_url']
                print(f"✅ Found ngrok URL: {url}")
                webhook_url = f"{url}/webhook"
                
                # Set webhook
                print(f"Setting webhook to: {webhook_url}")
                set_url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook"
                payload = {'url': webhook_url}
                response = requests.post(set_url, json=payload, timeout=10)
                result = response.json()
                
                if result.get('ok'):
                    print(f"✅ Webhook set successfully!")
                    print(f"   URL: {webhook_url}")
                    sys.exit(0)
                else:
                    print(f"❌ Failed: {result.get('description')}")
                    sys.exit(1)
        else:
            print(f"⏳ Waiting for ngrok... ({i+1}/10)")
    except Exception as e:
        if i < 9:
            print(f"⏳ Waiting for ngrok... ({i+1}/10)")
        else:
            print(f"❌ Error: {e}")
    time.sleep(2)

print("❌ Could not get ngrok URL")
print("💡 Please check ngrok manually at http://localhost:4040")
sys.exit(1)
