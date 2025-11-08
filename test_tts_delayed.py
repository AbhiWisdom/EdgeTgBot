#!/usr/bin/env python3
"""
Test TTS generation with longer delays
"""
import sys
import os
import time
from pathlib import Path

# Add parent directory to path to import app functions
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

def test_with_delay():
    """Test TTS with initial delay to avoid rate limiting."""
    print("=" * 60)
    print("TTS GENERATION TEST (WITH INITIAL DELAY)")
    print("=" * 60)
    print()
    
    print("⏳ Waiting 5 seconds before test to avoid rate limiting...")
    time.sleep(5)
    print()
    
    # Test parameters
    test_text = "Testing text to speech generation."
    test_voice = "en-US-AriaNeural"
    
    # Create output directory
    test_dir = BASE_AUDIO_DIR / 'test'
    test_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = test_dir / "test_delayed.mp3"
    
    print(f"📝 Test Text: {test_text}")
    print(f"🎤 Voice: {test_voice}")
    print()
    
    print("🔄 Generating TTS...")
    print()
    
    success = generate_tts_with_retry(
        text=test_text,
        voice=test_voice,
        output_path=output_path,
        max_retries=3
    )
    
    print()
    print("=" * 60)
    
    if success:
        file_size = output_path.stat().st_size if output_path.exists() else 0
        print("✅ SUCCESS!")
        print(f"   File size: {file_size} bytes")
        print(f"   File path: {output_path}")
    else:
        print("❌ FAILED")
        print("   All retry attempts failed with 403 errors")
        print("   This indicates Edge TTS is blocking requests")
    
    print("=" * 60)
    
    # Cleanup
    if output_path.exists():
        try:
            output_path.unlink()
            print(f"\n🧹 Cleaned up test file")
        except:
            pass

if __name__ == "__main__":
    try:
        test_with_delay()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")

