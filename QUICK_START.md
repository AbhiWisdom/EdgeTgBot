# 🚀 Quick Start Guide

## ✅ Bot is Now Modular!

Your bot has been successfully refactored into a clean, modular structure for easy feature addition.

## 📂 New Structure

```
EdgeTTS-main/
├── main.py                          # ⭐ Main entry point
├── bot/
│   ├── config.py                   # ⚙️ All settings
│   ├── states.py                   # 📊 FSM states
│   ├── utils.py                    # 🛠️ Helper functions
│   ├── keyboards.py                # ⌨️ UI keyboards
│   ├── user_manager.py             # 👥 User tracking
│   └── handlers/                   # 🎯 Feature handlers
│       ├── start_handler.py        # /start command
│       ├── country_handler.py      # Country selection
│       ├── language_handler.py     # Language selection
│       ├── voice_handler.py        # Voice selection
│       ├── navigation_handler.py   # Navigation (back buttons)
│       ├── tts_handler.py          # Text-to-speech
│       ├── media_handler.py        # Media forwarding
│       └── broadcast_handler.py    # 📢 Broadcast system (NEW!)
```

## 🎮 Commands

### Start the bot:
```bash
cd /Users/abhiraj/Downloads/EdgeTTS-main
source venv/bin/activate
python main.py
```

### Stop the bot:
```bash
pkill -f "python.*main"
```

### Check if running:
```bash
ps aux | grep "python.*main"
```

## ➕ Adding New Features (Example)

### 1️⃣ Add a New Command

Create `bot/handlers/stats_handler.py`:
```python
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    await message.answer("📊 User statistics coming soon!")
```

### 2️⃣ Register the Handler

Edit `bot/handlers/__init__.py`:
```python
from .stats_handler import router as stats_router

all_routers = [
    start_router,
    country_router,
    # ... existing ...
    stats_router,  # ← Add here
]
```

### 3️⃣ Restart the bot
```bash
pkill -f "python.*main" && python main.py
```

That's it! ✨

## 🎯 Common Modifications

### Change bot token:
Edit `bot/config.py` → `API_TOKEN`

### Change owner ID:
Edit `bot/config.py` → `OWNER_ID`

### Change channel requirement:
Edit `bot/config.py` → `ABHIBOTS_CHANNEL_ID`

### Adjust pagination:
Edit `bot/config.py` → `COUNTRIES_PER_PAGE` or `VOICES_PER_PAGE`

### Add logging:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Your log message")
```

## 🆕 Latest Features (Just Added!)

### 📊 **Automatic User Tracking**
- Every new user is automatically saved to `userid.json`
- Owner receives instant notification when a new user joins
- Updated user database sent to owner automatically

### 📢 **Broadcast System**
- `/broadcast` - Send messages to all users
- `/stats` - View bot statistics  
- `/getuserlist` - Download user database
- Real-time progress tracking
- Detailed delivery statistics

**See `BROADCAST_GUIDE.md` for complete broadcast documentation!**

## 🏗️ Architecture Benefits

✅ **Modular** - Each feature is isolated  
✅ **Scalable** - Easy to add new features  
✅ **Maintainable** - Changes don't affect other modules  
✅ **Fast** - Fully async with aiogram  
✅ **Clean** - Clear separation of concerns  

## 📚 Documentation

See `BOT_STRUCTURE.md` for detailed documentation on:
- Architecture overview
- How each module works
- Step-by-step feature addition
- Best practices
- Debugging tips

## 🎉 What Changed?

### Before:
- ❌ One massive 649-line file
- ❌ Hard to find specific features
- ❌ Difficult to add new features
- ❌ Changes risked breaking everything

### After:
- ✅ 10 clean, focused modules
- ✅ Each feature in its own file
- ✅ Add features without touching existing code
- ✅ Changes are isolated and safe
- ✅ Team-friendly structure

---

**Happy coding! 🚀**

Need help? Check `BOT_STRUCTURE.md` for comprehensive guides!

