# 🔗 Webhook Configuration

## Your Heroku App

**App URL:** `https://ttsbot-a572faff13b4.herokuapp.com/`

**Webhook URL:** `https://ttsbot-a572faff13b4.herokuapp.com/webhook`

---

## 📋 Setup Commands

### 1. Set Environment Variables on Heroku

```bash
heroku config:set WEBHOOK_URL="https://ttsbot-a572faff13b4.herokuapp.com/webhook"
```

### 2. Set Webhook Using Script

```bash
heroku run python setup_webhook.py
```

### 3. Or Set Webhook Manually

Visit in browser or use curl:
```
https://ttsbot-a572faff13b4.herokuapp.com/setwebhook?url=https://ttsbot-a572faff13b4.herokuapp.com/webhook
```

### 4. Check Webhook Status

```bash
# Using Heroku CLI
heroku run python -c "
import os
import asyncio
from aiogram import Bot

async def check():
    bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
    info = await bot.get_webhook_info()
    print(f'Webhook URL: {info.url}')
    print(f'Pending Updates: {info.pending_update_count}')
    print(f'Last Error: {info.last_error_message or \"None\"}')

asyncio.run(check())
"

# Or visit:
# https://ttsbot-a572faff13b4.herokuapp.com/webhookinfo
```

---

## ✅ Verification

After setting webhook, test your bot:
1. Send `/start` to your bot
2. Check Heroku logs: `heroku logs --tail`
3. Verify webhook info endpoint

---

## 🔧 Troubleshooting

If webhook doesn't work:
1. Check app is running: `heroku ps`
2. Check logs: `heroku logs --tail`
3. Verify WEBHOOK_URL config: `heroku config`
4. Test health endpoint: `curl https://ttsbot-a572faff13b4.herokuapp.com/health`

