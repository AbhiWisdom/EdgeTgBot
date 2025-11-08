#!/usr/bin/env python3
"""
Generate a single TTS audio file
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

def generate_audio():
    """Generate a test audio file."""
    print("=" * 60)
    print("GENERATING TTS AUDIO")
    print("=" * 60)
    print()
    
    # Test parameters
    text = "Hello! This is a test of the text to speech system. The audio generation is working correctly."
    voice = "en-US-AriaNeural"  # Popular English voice
    
    # Create output directory
    output_dir = BASE_AUDIO_DIR / 'generated'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "test_audio.mp3"
    
    print(f"📝 Text: {text}")
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
        max_retries=3
    )
    
    print()
    print("=" * 60)
    
    if success:
        file_size = output_path.stat().st_size
        print("✅ AUDIO GENERATED SUCCESSFULLY!")
        print(f"   📁 File: {output_path}")
        print(f"   📊 Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        print()
        print(f"🎉 Audio file is ready at: {output_path.absolute()}")
    else:
        print("❌ AUDIO GENERATION FAILED")
        print("   All retry attempts failed with 403 errors")
        print("   This may be due to Edge TTS service restrictions")
        print()
        print("💡 Try again later or check network connectivity")
    
    print("=" * 60)
    
    return success, output_path

if __name__ == "__main__":
    try:
        success, output_path = generate_audio()
        if success:
            print(f"\n✅ Success! Audio saved to: {output_path}")
        else:
            print(f"\n⚠️  Generation failed. Check logs above for details.")
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

