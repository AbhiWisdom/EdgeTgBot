#!/usr/bin/env python3
"""Test TTS API on Heroku"""
import requests
import json

url = 'https://ttsbot-a572faff13b4.herokuapp.com/tts'
data = {
    'text': 'Hello, this is a test of the TTS API on Heroku.',
    'voice': 'en-US-AriaNeural'
}

print("=" * 60)
print("TESTING TTS API ON HEROKU")
print("=" * 60)
print()
print(f"URL: {url}")
print(f"Text: {data['text']}")
print(f"Voice: {data['voice']}")
print()

try:
    print("🔄 Sending request...")
    response = requests.post(url, json=data, timeout=60)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS!")
        print(f"Response: {json.dumps(result, indent=2)}")
        if 'audio_url' in result:
            print(f"\n🎉 Audio URL: https://ttsbot-a572faff13b4.herokuapp.com{result['audio_url']}")
    else:
        try:
            error = response.json()
            print(f"❌ Error: {json.dumps(error, indent=2)}")
        except:
            print(f"❌ Error: {response.text}")
            
except requests.exceptions.Timeout:
    print("❌ Timeout: Request took too long (>60s)")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 60)
