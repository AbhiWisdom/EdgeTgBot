#!/usr/bin/env python3
"""
Test web HTML interface and audio generation
"""
import requests
import json
import time

def test_web_interface():
    """Test the web HTML interface and TTS API."""
    base_url = 'http://localhost:5001'
    
    print("=" * 60)
    print("TESTING WEB HTML INTERFACE & AUDIO GENERATION")
    print("=" * 60)
    print()
    
    # Test 1: Check if web interface loads
    print("1️⃣ Testing web interface (/)...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Web interface loaded successfully")
            print(f"   Content length: {len(response.text):,} bytes")
            if 'text-to-speech' in response.text.lower() or 'voice' in response.text.lower():
                print(f"   ✅ HTML content looks correct")
            else:
                print(f"   ⚠️  HTML content may be incomplete")
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error: Server not running")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print()
    
    # Test 2: Test TTS API endpoint
    print("2️⃣ Testing TTS API endpoint (/tts)...")
    test_data = {
        'text': 'Hello! This is a test of the web interface audio generation.',
        'voice': 'en-US-AriaNeural'
    }
    
    try:
        print(f"   Sending request with text: '{test_data['text'][:40]}...'")
        print(f"   Voice: {test_data['voice']}")
        
        response = requests.post(
            f"{base_url}/tts",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'audio_url' in result:
                audio_url = result['audio_url']
                print(f"   ✅ SUCCESS! Audio generated")
                print(f"   Audio URL: {audio_url}")
                
                # Test 3: Verify audio file is accessible
                print()
                print("3️⃣ Testing audio file access...")
                audio_full_url = f"{base_url}{audio_url}"
                audio_response = requests.get(audio_full_url, timeout=10)
                
                if audio_response.status_code == 200:
                    audio_size = len(audio_response.content)
                    print(f"   ✅ Audio file accessible")
                    print(f"   File size: {audio_size:,} bytes ({audio_size / 1024:.2f} KB)")
                    print(f"   Content-Type: {audio_response.headers.get('Content-Type', 'unknown')}")
                else:
                    print(f"   ⚠️  Audio file not accessible: {audio_response.status_code}")
            else:
                print(f"   ⚠️  Response: {json.dumps(result, indent=2)}")
        else:
            try:
                error = response.json()
                print(f"   ❌ Error: {json.dumps(error, indent=2)}")
            except:
                print(f"   ❌ Error: {response.text[:200]}")
                
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout: Request took too long (>60s)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print()
    print(f"🌐 Web Interface: http://localhost:5001/")
    print(f"📡 API Endpoint: http://localhost:5001/tts")
    print()

if __name__ == "__main__":
    test_web_interface()

