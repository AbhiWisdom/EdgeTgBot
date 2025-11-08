# 🔧 Heroku Bot Troubleshooting Guide

## 🚨 Bot Not Responding on Heroku

### Step 1: Check if App is Running

```bash
heroku ps
```

Should show:
```
web.1: up 2024-XX-XX XX:XX:XX
```

If not running:
```bash
heroku restart
```

---

### Step 2: Check Logs

```bash
heroku logs --tail
```

Look for:
- ✅ "Registered routers" or "Bot is running"
- ❌ Error messages
- ❌ Import errors
- ❌ Missing environment variables

---

### Step 3: Verify Webhook is Set

**Check webhook status:**
```bash
curl https://ttsbot-a572faff13b4.herokuapp.com/webhookinfo
```

Or visit:
```
https://ttsbot-a572faff13b4.herokuapp.com/webhookinfo
```

**Set webhook if not set:**
```bash
# Method 1: Auto-set
curl https://ttsbot-a572faff13b4.herokuapp.com/setwebhook/auto

# Method 2: Using script
heroku run python setup_webhook.py

# Method 3: Manual
curl "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://ttsbot-a572faff13b4.herokuapp.com/webhook"
```

---

### Step 4: Check Environment Variables

```bash
heroku config
```

Required variables:
- ✅ `TELEGRAM_BOT_TOKEN` - Your bot token
- ✅ `WEBHOOK_URL` - Webhook URL (optional, has default)
- ✅ `OWNER_ID` - Your Telegram user ID

Set missing ones:
```bash
heroku config:set TELEGRAM_BOT_TOKEN="your_token"
heroku config:set OWNER_ID="890382857"
```

---

### Step 5: Test Endpoints

**Health check:**
```bash
curl https://ttsbot-a572faff13b4.herokuapp.com/health
```

**Test endpoint:**
```bash
curl https://ttsbot-a572faff13b4.herokuapp.com/test
```

Should return JSON with bot status.

---

### Step 6: Check Webhook Endpoint

**Test webhook manually:**
```bash
curl -X POST https://ttsbot-a572faff13b4.herokuapp.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"update_id": 123, "message": {"message_id": 1, "from": {"id": 123}, "chat": {"id": 123, "type": "private"}, "text": "/start"}}'
```

Should return: `{"ok": true}`

---

### Step 7: Common Issues

#### Issue: "Application Error"
- **Cause**: App crashed on startup
- **Fix**: Check logs, fix import errors

#### Issue: "Webhook not set"
- **Cause**: Webhook URL not configured
- **Fix**: Run `/setwebhook/auto` endpoint

#### Issue: "Bot token invalid"
- **Cause**: Wrong or missing TELEGRAM_BOT_TOKEN
- **Fix**: Set correct token: `heroku config:set TELEGRAM_BOT_TOKEN="..."`

#### Issue: "No response from bot"
- **Cause**: Webhook receiving but not processing
- **Fix**: Check logs for errors in handle_message()

---

### Step 8: Debug Checklist

- [ ] App is running (`heroku ps`)
- [ ] No errors in logs (`heroku logs --tail`)
- [ ] Webhook is set (`/webhookinfo`)
- [ ] Environment variables set (`heroku config`)
- [ ] Health endpoint works (`/health`)
- [ ] Webhook endpoint accessible (`/webhook`)

---

### Step 9: Quick Fixes

**Restart app:**
```bash
heroku restart
```

**Clear webhook and reset:**
```bash
# Delete webhook
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"

# Set again
curl https://ttsbot-a572faff13b4.herokuapp.com/setwebhook/auto
```

**Redeploy:**
```bash
git push heroku main
```

---

### Step 10: Enable Debug Logging

Add to `app.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

Then check logs:
```bash
heroku logs --tail
```

---

## 📞 Still Not Working?

1. Check Heroku logs: `heroku logs --tail`
2. Test webhook endpoint: `/test`
3. Verify webhook is set: `/webhookinfo`
4. Check environment variables: `heroku config`
5. Restart app: `heroku restart`

---

**Most common fix:**
```bash
heroku restart
heroku run python setup_webhook.py
```

