#!/usr/bin/env python3
"""
Test TTS API endpoint
"""
import requests
import json
import time
import sys

def test_tts_api(base_url='http://localhost:5000'):
    """Test the /tts API endpoint."""
    print("=" * 60)
    print("TESTING TTS API ENDPOINT")
    print("=" * 60)
    print()
    
    url = f"{base_url}/tts"
    
    # Test data
    test_cases = [
        {
            "name": "Simple text",
            "data": {
                "text": "Hello, this is a test.",
                "voice": "en-US-AriaNeural"
            }
        },
        {
            "name": "Longer text",
            "data": {
                "text": "This is a longer test message to verify the TTS API is working correctly with multiple sentences.",
                "voice": "en-US-AriaNeural"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"  Text: {test_case['data']['text'][:50]}...")
        print(f"  Voice: {test_case['data']['voice']}")
        print()
        
        try:
            response = requests.post(
                url,
                json=test_case['data'],
                timeout=60,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'audio_url' in result:
                    print(f"  ✅ SUCCESS!")
                    print(f"  Audio URL: {result['audio_url']}")
                    print(f"  Full URL: {base_url}{result['audio_url']}")
                else:
                    print(f"  ⚠️  Response: {json.dumps(result, indent=2)}")
            else:
                try:
                    error = response.json()
                    print(f"  ❌ Error: {json.dumps(error, indent=2)}")
                except:
                    print(f"  ❌ Error: {response.text}")
            
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection Error: Server not running at {base_url}")
            print(f"  💡 Start server with: python app.py")
            return False
        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout: Request took too long")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()
        time.sleep(1)  # Small delay between tests
    
    print("=" * 60)
    return True

if __name__ == "__main__":
    # Try localhost first
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5000'
    
    print(f"Testing API at: {base_url}")
    print()
    
    success = test_tts_api(base_url)
    
    if not success:
        print("\n💡 To start the server:")
        print("   python app.py")
        print("\n   Then run this test again.")

