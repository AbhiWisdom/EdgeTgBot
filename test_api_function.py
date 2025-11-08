#!/usr/bin/env python3
"""
Test TTS API function directly
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import generate_tts_with_retry
from bot.config import BASE_AUDIO_DIR
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_tts_api_function():
    """Test TTS generation function directly."""
    print("=" * 60)
    print("TESTING TTS API FUNCTION")
    print("=" * 60)
    print()
    
    test_cases = [
        {
            "name": "Simple text",
            "text": "Hello, this is a test of the TTS API.",
            "voice": "en-US-AriaNeural"
        },
        {
            "name": "Longer text",
            "text": "This is a longer test message to verify the TTS API is working correctly with multiple sentences and more content.",
            "voice": "en-US-AriaNeural"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"  Text: {test_case['text'][:60]}...")
        print(f"  Voice: {test_case['voice']}")
        print()
        
        # Create output directory
        output_dir = BASE_AUDIO_DIR / 'api_test'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"test_{i}.mp3"
        
        print("  🔄 Generating audio...")
        
        # Test with fast_mode=False (normal mode for API)
        success = generate_tts_with_retry(
            text=test_case['text'],
            voice=test_case['voice'],
            output_path=output_path,
            max_retries=5,
            fast_mode=False
        )
        
        if success:
            file_size = output_path.stat().st_size
            print(f"  ✅ SUCCESS!")
            print(f"  File: {output_path}")
            print(f"  Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        else:
            print(f"  ❌ FAILED")
            print(f"  TTS generation failed after retries")
        
        print()
    
    print("=" * 60)
    print("✅ API Function Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_tts_api_function()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

