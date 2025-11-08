# 🤖 Telegram TTS Bot - Heroku Ready

A fast, modular Telegram bot for text-to-speech conversion using Microsoft Edge TTS.

## ✨ Features

- 🎤 **Text-to-Speech** - Convert text to speech with 400+ voices
- 📢 **Broadcast System** - Send messages to all users (owner only)
- 👥 **User Tracking** - Automatic user registration and database
- 🌍 **Multi-language** - Support for 100+ languages
- ⚡ **Fast & Async** - Built with aiogram 3.x for maximum performance
- 🏗️ **Modular** - Clean architecture for easy feature addition
- ☁️ **Heroku Ready** - Deploy to Heroku with one command

## 🚀 Quick Deploy to Heroku

```bash
# 1. Clone and setup
git clone <your-repo>
cd EdgeTTS-main

# 2. Login to Heroku
heroku login

# 3. Create app
heroku create your-bot-name

# 4. Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN="your_bot_token"
heroku config:set WEBHOOK_URL="https://your-bot-name.herokuapp.com/webhook"
heroku config:set OWNER_ID="your_telegram_user_id"

# 5. Deploy
git push heroku main

# 6. Set webhook
heroku run python setup_webhook.py
```

**See `HEROKU_DEPLOYMENT.md` for detailed instructions!**

## 📁 Project Structure

```
bot/
├── config.py              # Configuration (env vars)
├── handlers/              # Feature handlers
│   ├── start_handler.py
│   ├── broadcast_handler.py
│   └── ...
├── keyboards.py           # UI keyboards
├── states.py              # FSM states
├── utils.py               # Helper functions
└── user_manager.py        # User tracking

app.py                     # Flask webhook app
main.py                    # Local polling (dev)
Procfile                   # Heroku process
requirements.txt           # Dependencies
```

## 🎮 Commands

### User Commands
- `/start` - Start bot and select voice

### Owner Commands
- `/broadcast` - Send message to all users
- `/stats` - View bot statistics
- `/getuserlist` - Download user database
- `/stopbroadcast` - Stop running broadcast

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (polling mode)
python main.py

# Or run Flask app
python app.py
```

## 📚 Documentation

- **`HEROKU_DEPLOYMENT.md`** - Complete Heroku deployment guide
- **`BOT_STRUCTURE.md`** - Architecture and development guide
- **`BROADCAST_GUIDE.md`** - Broadcast feature documentation
- **`QUICK_START.md`** - Quick reference guide

## 🛠️ Tech Stack

- **Python 3.12** - Programming language
- **Flask** - Web framework (Heroku)
- **Aiogram 3.x** - Telegram bot framework
- **Edge TTS** - Text-to-speech engine
- **Gunicorn** - WSGI server (Heroku)

## 📝 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Bot token from BotFather |
| `WEBHOOK_URL` | ✅ | Heroku app webhook URL |
| `OWNER_ID` | ✅ | Your Telegram user ID |
| `ABHIBOTS_CHANNEL_ID` | ⚠️ | Channel ID (optional) |

## 🐛 Troubleshooting

See `HEROKU_DEPLOYMENT.md` for troubleshooting guide.

## 📄 License

MIT License

## 🙏 Credits

- Microsoft Edge TTS
- Aiogram Framework
- Heroku Platform

---

**Made with ❤️ for the Telegram community**

