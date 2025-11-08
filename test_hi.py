#!/usr/bin/env python3
"""
Quick test: Convert "hi" to audio
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

def test_hi():
    """Test converting 'hi' to audio."""
    print("=" * 60)
    print("TEST: Converting 'hi' to Audio")
    print("=" * 60)
    print()
    
    # Test parameters
    text = "hi"
    voice = "en-US-AriaNeural"  # Popular English voice
    
    # Create output directory
    output_dir = BASE_AUDIO_DIR / 'test'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "hi_test.mp3"
    
    print(f"📝 Text: '{text}'")
    print(f"🎤 Voice: {voice}")
    print(f"💾 Output: {output_path}")
    print()
    
    print("🔄 Generating audio...")
    print()
    
    # Generate audio
    success = generate_tts_with_retry(
        text=text,
        voice=voice,
        output_path=output_path,
        max_retries=5  # Using improved retry logic with 5 attempts
    )
    
    print()
    print("=" * 60)
    
    if success:
        file_size = output_path.stat().st_size
        print("✅ SUCCESS!")
        print(f"   📁 File: {output_path}")
        print(f"   📊 Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        print()
        print(f"🎉 Audio file created: {output_path.absolute()}")
        print()
        print("💡 You can play it with:")
        print(f"   open {output_path}")
    else:
        print("❌ FAILED")
        print("   All retry attempts failed with 403 errors")
        print("   This indicates Edge TTS service restrictions")
        print()
        print("💡 Note: This may work on Heroku with different IP")
    
    print("=" * 60)
    
    return success, output_path

if __name__ == "__main__":
    try:
        success, output_path = test_hi()
        if success:
            print(f"\n✅ Test passed! Audio saved to: {output_path}")
        else:
            print(f"\n⚠️  Test failed. Check logs above.")
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

