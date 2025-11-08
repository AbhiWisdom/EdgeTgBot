# 🤖 Telegram TTS Bot - Modular Structure

## 📁 Project Structure

```
EdgeTTS-main/
├── main.py                 # Entry point - starts the bot
├── bot/                    # Main bot package
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration & constants
│   ├── states.py          # FSM state definitions
│   ├── utils.py           # Helper functions (voice loading, cleanup, etc.)
│   ├── keyboards.py       # Keyboard builders
│   └── handlers/          # Handler modules
│       ├── __init__.py            # Exports all routers
│       ├── start_handler.py       # /start command
│       ├── country_handler.py     # Country selection
│       ├── language_handler.py    # Language selection
│       ├── voice_handler.py       # Voice selection
│       ├── navigation_handler.py  # Back buttons
│       ├── tts_handler.py         # Text-to-speech processing
│       └── media_handler.py       # Media forwarding
├── voice.json             # Voice database
├── static/audio/          # Generated audio files
└── venv/                  # Virtual environment
```

## 🎯 Module Responsibilities

### `main.py`
- Bot initialization
- Router registration
- Polling management
- Error handling

### `bot/config.py`
- API tokens
- File paths
- Configuration constants
- Owner/channel settings

### `bot/states.py`
- FSM (Finite State Machine) states
- User flow management

### `bot/utils.py`
- Voice list loading
- Country/language/voice filtering
- Audio file cleanup
- Data sanitization

### `bot/keyboards.py`
- Inline keyboard builders
- Pagination logic
- Button creation

### `bot/handlers/`
Each handler file focuses on a specific feature:
- **start_handler**: Entry point, membership check
- **country_handler**: Country selection & pagination
- **language_handler**: Language selection
- **voice_handler**: Voice selection & pagination
- **navigation_handler**: Back button navigation
- **tts_handler**: Text-to-speech generation
- **media_handler**: Media forwarding to owner

## 🚀 How to Run

### Start the Bot
```bash
cd /Users/abhiraj/Downloads/EdgeTTS-main
source venv/bin/activate
python main.py
```

### Stop the Bot
```bash
pkill -f "python.*main"
```

## ➕ Adding New Features

### 1. Adding a New Command Handler

Create a new file: `bot/handlers/new_feature_handler.py`

```python
"""
New Feature Handler
"""
import logging
from aiogram import Router, types, F
from aiogram.filters import Command

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("newcommand"))
async def handle_new_command(message: types.Message):
    """Handle /newcommand"""
    await message.answer("New feature!")
```

Then add it to `bot/handlers/__init__.py`:

```python
from .new_feature_handler import router as new_feature_router

all_routers = [
    start_router,
    country_router,
    # ... existing routers ...
    new_feature_router,  # Add here
]
```

### 2. Adding New Configuration

Add to `bot/config.py`:

```python
# New feature settings
NEW_FEATURE_ENABLED = True
NEW_FEATURE_LIMIT = 100
```

Use in handlers:

```python
from ..config import NEW_FEATURE_ENABLED, NEW_FEATURE_LIMIT
```

### 3. Adding New States

Add to `bot/states.py`:

```python
class NewFeatureStates(StatesGroup):
    step_one = State()
    step_two = State()
```

### 4. Adding New Utility Functions

Add to `bot/utils.py`:

```python
def new_helper_function(param):
    """Description of what it does"""
    # Implementation
    return result
```

### 5. Adding New Keyboards

Add to `bot/keyboards.py`:

```python
def create_new_keyboard(items):
    """Create keyboard for new feature"""
    keyboard = []
    for item in items:
        keyboard.append([InlineKeyboardButton(
            text=item['name'],
            callback_data=f'new:{item["id"]}'
        )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
```

## 🔧 Common Tasks

### Adding Middleware
Create `bot/middlewares/` directory:

```python
# bot/middlewares/logging_middleware.py
from aiogram import BaseMiddleware

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Pre-processing
        result = await handler(event, data)
        # Post-processing
        return result
```

Register in `main.py`:

```python
from bot.middlewares.logging_middleware import LoggingMiddleware

dp.message.middleware(LoggingMiddleware())
```

### Adding Database Support
1. Create `bot/database.py`
2. Add database models
3. Import in handlers that need it

```python
# bot/database.py
import aiosqlite

async def init_db():
    # Database initialization
    pass
```

### Adding API Integrations
Create `bot/api/` directory for external APIs:

```python
# bot/api/translation_api.py
import aiohttp

async def translate_text(text, target_lang):
    async with aiohttp.ClientSession() as session:
        # API call
        pass
```

## 📊 Benefits of This Structure

### ✅ Modularity
- Each feature in its own file
- Easy to locate and modify code
- Clear separation of concerns

### ✅ Scalability
- Add new handlers without touching existing code
- Easy to enable/disable features
- Support for team development

### ✅ Maintainability
- Changes are isolated to specific modules
- Easier debugging
- Clear code organization

### ✅ Testing
- Each module can be tested independently
- Mock dependencies easily
- Better code coverage

### ✅ Performance
- Only import what you need
- Lazy loading possible
- Better memory management

## 🎨 Best Practices

1. **One responsibility per file** - Each handler handles one feature
2. **Use routers** - Group related handlers in Router objects
3. **Centralize config** - All settings in config.py
4. **Type hints** - Use type annotations for better IDE support
5. **Logging** - Log important events in each handler
6. **Error handling** - Catch and handle exceptions gracefully
7. **Documentation** - Add docstrings to functions
8. **Async/await** - Use async functions throughout

## 🔍 Debugging Tips

### Check which handlers are registered:
```python
logger.info(f"Registered {len(all_routers)} routers")
```

### Enable debug logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Test individual modules:
```python
from bot.utils import load_voice_list
voices = load_voice_list()
print(len(voices))
```

## 📝 TODO Ideas for Future Features

- [ ] Add admin panel handler
- [ ] Implement user statistics
- [ ] Add voice preview functionality
- [ ] Support for batch TTS generation
- [ ] Add custom voice speed/pitch controls
- [ ] Implement user favorites system
- [ ] Add multilingual bot interface
- [ ] Create backup/restore handlers
- [ ] Add usage analytics
- [ ] Implement rate limiting middleware

---

**Happy coding! 🚀**

