# Edge TTS Library Implementation

## ✅ Current Implementation

The bot now uses the `edge_tts` library with proper async/await patterns and retry logic.

### Key Features

1. **Proper Async Handling**
   - Uses `async def` for TTS generation
   - Properly awaits `edge_tts.Communicate().save()`
   - Uses `asyncio.run()` to bridge sync/async code

2. **Input Validation**
   - Validates text is not empty
   - Validates voice is specified
   - Ensures output directory exists

3. **Retry Logic**
   - Exponential backoff (2s, 4s delays)
   - Maximum 3 retry attempts
   - Specific handling for 403 errors

4. **Error Handling**
   - Catches `WSServerHandshakeError` for 403 errors
   - Logs warnings and errors appropriately
   - Returns clear success/failure status

## 📝 Code Structure

```python
# Internal async function
async def _generate_tts_async(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    return True if file exists and has content else False

# Public function with retry logic
def generate_tts_with_retry(text, voice, output_path, max_retries=3):
    # Validates inputs
    # Retries with exponential backoff
    # Returns True/False
```

## 🔧 Usage

### In Web Interface (`/tts` endpoint)
```python
success = generate_tts_with_retry(text, voice_shortname, output_path)
```

### In Telegram Bot (`handle_text_message`)
```python
success = generate_tts_with_retry(text, voice, output_path)
```

## ⚠️ Known Issues

**403 Errors**: Edge TTS may return 403 errors due to:
- Rate limiting from Microsoft's service
- IP-based blocking (server IPs may be restricted)
- Service restrictions for automated use

**Solution**: The retry logic handles transient 403 errors. Persistent 403s indicate service restrictions, not code issues.

## 📊 Library Information

- **Library**: `edge-tts==6.1.12`
- **Total Voices**: 322 available voices
- **Format**: MP3 audio files
- **Method**: WebSocket connection to Microsoft Edge TTS service

## ✅ Implementation Status

- ✅ Proper async/await usage
- ✅ Input validation
- ✅ Retry logic with exponential backoff
- ✅ Error handling for 403 errors
- ✅ File verification
- ✅ Logging and debugging

The `edge_tts` library is now properly integrated and ready for production use!

