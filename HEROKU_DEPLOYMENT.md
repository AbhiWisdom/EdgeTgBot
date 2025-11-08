# 🚀 Heroku Deployment Guide - Telegram TTS Bot

## 📋 Prerequisites

1. **Heroku Account** - Sign up at [heroku.com](https://www.heroku.com)
2. **Heroku CLI** - Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git** - For version control
4. **Telegram Bot Token** - From [@BotFather](https://t.me/BotFather)

---

## 🔧 Step-by-Step Deployment

### 1. **Prepare Your Project**

Make sure you have these files:
- ✅ `app.py` - Flask webhook app
- ✅ `Procfile` - Heroku process file
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version
- ✅ `bot/` - Bot package directory
- ✅ `voice.json` - Voice database
- ✅ `userid.json` - User database (optional, will be created)

### 2. **Login to Heroku**

```bash
heroku login
```

### 3. **Create Heroku App**

```bash
# Create app (replace 'your-bot-name' with your desired name)
heroku create your-bot-name

# Or let Heroku generate a name
heroku create
```

### 4. **Set Environment Variables**

```bash
# Set your Telegram bot token
heroku config:set TELEGRAM_BOT_TOKEN="your_bot_token_here"

# Set webhook URL (replace with your app URL)
heroku config:set WEBHOOK_URL="https://your-bot-name.herokuapp.com/webhook"

# Set owner ID (your Telegram user ID)
heroku config:set OWNER_ID="890382857"

# Set channel ID (optional, if different)
heroku config:set ABHIBOTS_CHANNEL_ID="-1001857446616"

# Set channel username (optional)
heroku config:set ABHIBOTS_CHAT_ID="@abhibots"
```

**To find your Telegram User ID:**
- Message [@userinfobot](https://t.me/userinfobot) on Telegram

### 5. **Deploy to Heroku**

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial deployment"

# Deploy to Heroku
git push heroku main

# Or if using master branch
git push heroku master
```

### 6. **Set Webhook**

After deployment, set the webhook:

```bash
# Method 1: Using Heroku CLI
heroku run python -c "
import os
import asyncio
from aiogram import Bot

async def set_webhook():
    bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
    await bot.set_webhook(os.environ['WEBHOOK_URL'])
    info = await bot.get_webhook_info()
    print(f'Webhook set: {info.url}')
    print(f'Pending updates: {info.pending_update_count}')

asyncio.run(set_webhook())
"
```

**Or visit in browser:**
```
https://your-bot-name.herokuapp.com/setwebhook?url=https://your-bot-name.herokuapp.com/webhook
```

### 7. **Verify Deployment**

```bash
# Check logs
heroku logs --tail

# Check webhook status
curl https://your-bot-name.herokuapp.com/webhookinfo

# Health check
curl https://your-bot-name.herokuapp.com/health
```

---

## 🔍 Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | ✅ Yes | Your bot token from BotFather | `123456:ABC-DEF...` |
| `WEBHOOK_URL` | ✅ Yes | Your Heroku app webhook URL | `https://app.herokuapp.com/webhook` |
| `OWNER_ID` | ✅ Yes | Your Telegram user ID | `890382857` |
| `ABHIBOTS_CHANNEL_ID` | ⚠️ Optional | Channel ID for membership check | `-1001857446616` |
| `ABHIBOTS_CHAT_ID` | ⚠️ Optional | Channel username | `@abhibots` |
| `PORT` | ❌ No | Auto-set by Heroku | `5000` |

---

## 📊 Monitoring & Management

### View Logs

```bash
# Real-time logs
heroku logs --tail

# Last 100 lines
heroku logs -n 100

# Filter errors
heroku logs --tail | grep ERROR
```

### Check App Status

```bash
# App info
heroku info

# Check dynos
heroku ps

# Restart app
heroku restart
```

### Update Environment Variables

```bash
# Update token
heroku config:set TELEGRAM_BOT_TOKEN="new_token"

# View all config
heroku config

# Remove config
heroku config:unset VARIABLE_NAME
```

### Update Code

```bash
# Make changes locally, then:
git add .
git commit -m "Update description"
git push heroku main
```

---

## 🗄️ Database Management (Heroku Ephemeral Filesystem)

**Important:** Heroku uses an ephemeral filesystem. Files in `/tmp` are lost on restart.

### For `userid.json`:

The bot automatically uses `/tmp/userid.json` on Heroku. To persist data:

**Option 1: Use Heroku Postgres (Recommended)**
```bash
heroku addons:create heroku-postgresql:mini
```

**Option 2: Use External Storage**
- Google Drive API
- AWS S3
- MongoDB Atlas
- Redis

**Option 3: Backup Regularly**
```bash
# Download userid.json
heroku run cat /tmp/userid.json > userid_backup.json
```

---

## 🐛 Troubleshooting

### Bot Not Responding

1. **Check webhook:**
   ```bash
   curl https://your-app.herokuapp.com/webhookinfo
   ```

2. **Check logs:**
   ```bash
   heroku logs --tail
   ```

3. **Restart app:**
   ```bash
   heroku restart
   ```

### Webhook Errors

1. **Reset webhook:**
   ```bash
   # Clear webhook
   curl https://api.telegram.org/bot<TOKEN>/deleteWebhook
   
   # Set again
   curl https://your-app.herokuapp.com/setwebhook?url=https://your-app.herokuapp.com/webhook
   ```

### Memory Issues

If you see memory errors:
```bash
# Upgrade dyno type
heroku ps:scale web=1:standard-1x

# Or use more workers
# Edit Procfile: --workers 1
```

### Timeout Errors

Increase timeout in `Procfile`:
```
web: gunicorn app:app --timeout 300
```

---

## 📈 Scaling

### Upgrade Dyno Type

```bash
# View current plan
heroku ps

# Upgrade to standard-1x (paid)
heroku ps:resize web=standard-1x

# Or scale horizontally
heroku ps:scale web=2
```

### Performance Tips

1. **Use webhooks** (already configured) ✅
2. **Optimize workers** in Procfile
3. **Use Redis** for FSM storage (instead of MemoryStorage)
4. **Monitor** with Heroku metrics

---

## 🔐 Security Best Practices

1. **Never commit secrets:**
   - Use `.gitignore` for sensitive files
   - Store tokens in Heroku config vars

2. **Use environment variables:**
   - All sensitive data in `heroku config:set`

3. **Enable SSL:**
   - Heroku provides SSL automatically ✅

4. **Rate limiting:**
   - Already implemented in broadcast handler ✅

---

## 📝 File Structure for Heroku

```
your-bot/
├── app.py                 # Flask webhook app
├── Procfile              # Heroku process file
├── requirements.txt      # Dependencies
├── runtime.txt           # Python version
├── .gitignore            # Git ignore rules
├── bot/                  # Bot package
│   ├── __init__.py
│   ├── config.py
│   ├── handlers/
│   └── ...
├── voice.json            # Voice database
└── userid.json          # User database (created automatically)
```

---

## ✅ Post-Deployment Checklist

- [ ] App deployed successfully
- [ ] Environment variables set
- [ ] Webhook configured
- [ ] Bot responds to `/start`
- [ ] Owner commands work (`/broadcast`, `/stats`)
- [ ] Logs show no errors
- [ ] Health check returns 200

---

## 🆘 Support

### Common Issues:

**"Application Error"**
- Check logs: `heroku logs --tail`
- Verify all environment variables are set
- Check Procfile syntax

**"Webhook not working"**
- Verify WEBHOOK_URL is correct
- Check webhook info endpoint
- Ensure HTTPS (not HTTP)

**"Bot not responding"**
- Check bot token is correct
- Verify webhook is set
- Check logs for errors

---

## 🎉 Success!

Once deployed, your bot will:
- ✅ Run 24/7 on Heroku
- ✅ Handle webhooks automatically
- ✅ Scale with traffic
- ✅ Auto-restart on crashes
- ✅ Provide health monitoring

**Your bot is now live! 🚀**

---

## 📚 Additional Resources

- [Heroku Python Support](https://devcenter.heroku.com/articles/python-support)
- [Heroku Config Vars](https://devcenter.heroku.com/articles/config-vars)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Aiogram Documentation](https://docs.aiogram.dev/)

