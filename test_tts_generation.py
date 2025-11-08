#!/usr/bin/env python3
"""
Test TTS generation with retry logic
"""
import sys
import os
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

def test_tts_generation():
    """Test TTS generation with a sample text."""
    print("=" * 60)
    print("TTS GENERATION TEST")
    print("=" * 60)
    print()
    
    # Test parameters
    test_text = "Hello, this is a test of the text to speech system."
    test_voice = "en-US-AriaNeural"  # Common English voice
    
    # Create output directory
    test_dir = BASE_AUDIO_DIR / 'test'
    test_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = test_dir / "test_output.mp3"
    
    print(f"📝 Test Text: {test_text}")
    print(f"🎤 Voice: {test_voice}")
    print(f"💾 Output: {output_path}")
    print()
    
    print("🔄 Generating TTS with retry logic...")
    print()
    
    # Test TTS generation
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
        print("✅ TTS GENERATION SUCCESSFUL!")
        print(f"   File size: {file_size} bytes")
        print(f"   File path: {output_path}")
        print()
        print("🎉 Test passed! The retry logic is working correctly.")
    else:
        print("❌ TTS GENERATION FAILED")
        print()
        print("⚠️  This could be due to:")
        print("   - Rate limiting from Edge TTS service")
        print("   - Network connectivity issues")
        print("   - Invalid voice selection")
        print()
        print("💡 Try again in a few moments.")
    
    print("=" * 60)
    
    # Cleanup
    if output_path.exists():
        try:
            output_path.unlink()
            print(f"\n🧹 Cleaned up test file: {output_path}")
        except Exception as e:
            print(f"\n⚠️  Could not delete test file: {e}")

if __name__ == "__main__":
    try:
        test_tts_generation()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

