#!/usr/bin/env python3
"""
Test webhook endpoint
"""
import requests
import json
import os

# Get webhook URL from config or env
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://ttsbot-a572faff13b4.herokuapp.com/webhook')
APP_URL = 'https://ttsbot-a572faff13b4.herokuapp.com'

print("=" * 60)
print("WEBHOOK TEST")
print("=" * 60)
print()

# Test 1: Check webhook info
print("1️⃣ Checking webhook status...")
try:
    response = requests.get(f"{APP_URL}/webhookinfo", timeout=10)
    info = response.json()
    
    if info.get('ok'):
        webhook_url = info.get('webhook_url', 'Not set')
        pending = info.get('pending_update_count', 0)
        print(f"   ✅ Webhook URL: {webhook_url}")
        print(f"   📊 Pending Updates: {pending}")
        
        if info.get('last_error_message'):
            print(f"   ⚠️  Last Error: {info.get('last_error_message')}")
        else:
            print("   ✅ No errors")
    else:
        print(f"   ❌ Error: {info.get('error', 'Unknown')}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

print()

# Test 2: Test webhook endpoint with mock update
print("2️⃣ Testing webhook endpoint with mock update...")
test_update = {
    "update_id": 999999999,
    "message": {
        "message_id": 1,
        "from": {
            "id": 123456789,
            "is_bot": False,
            "first_name": "Test"
        },
        "chat": {
            "id": 123456789,
            "type": "private"
        },
        "date": 1234567890,
        "text": "/start"
    }
}

try:
    response = requests.post(
        f"{APP_URL}/webhook",
        json=test_update,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    result = response.json()
    if result.get('ok'):
        print("   ✅ Webhook endpoint responded successfully")
        print(f"   Response: {result}")
    else:
        print(f"   ⚠️  Response: {result}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

print()

# Test 3: Health check
print("3️⃣ Testing health endpoint...")
try:
    response = requests.get(f"{APP_URL}/health", timeout=10)
    health = response.json()
    print(f"   ✅ Health: {health.get('status')}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

print()

# Test 4: Test endpoint
print("4️⃣ Testing /test endpoint...")
try:
    response = requests.get(f"{APP_URL}/test", timeout=10)
    test_info = response.json()
    print(f"   ✅ Status: {test_info.get('status')}")
    print(f"   ✅ API Token Configured: {test_info.get('api_token_configured')}")
    print(f"   ✅ Webhook URL: {test_info.get('webhook_url')}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print()
print("📱 To test with real Telegram bot:")
print("   1. Make sure webhook is set: /setwebhook/auto")
print("   2. Send /start to your bot on Telegram")
print("   3. Check logs: heroku logs --tail")

