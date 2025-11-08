# 🔧 Fix Telegram Bot Not Responding

## ✅ Good News: App is Running!

Your app is now running:
- ✅ Web interface works: `GET /` returns 200
- ✅ Dyno is up: `web.1` is running
- ✅ App started successfully

## ❌ Problem: Bot Not Responding

The bot isn't responding to Telegram messages. This is usually because:

1. **Webhook not set** - Telegram doesn't know where to send updates
2. **Webhook URL incorrect** - Wrong URL configured
3. **Webhook endpoint error** - Errors in processing updates

---

## 🔧 Fix Steps

### Step 1: Set the Webhook

**Option A: Auto-set (Easiest)**
Visit in browser:
```
https://ttsbot-a572faff13b4.herokuapp.com/setwebhook/auto
```

**Option B: Using Script**
```bash
heroku run python setup_webhook.py
```

**Option C: Manual**
```bash
curl "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://ttsbot-a572faff13b4.herokuapp.com/webhook"
```

### Step 2: Verify Webhook is Set

Visit:
```
https://ttsbot-a572faff13b4.herokuapp.com/webhookinfo
```

Should show:
```json
{
  "ok": true,
  "result": {
    "url": "https://ttsbot-a572faff13b4.herokuapp.com/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

### Step 3: Check Logs for Webhook Updates

```bash
heroku logs --tail
```

Then send `/start` to your bot and watch for:
- `Received update: <update_id>`
- Any error messages

### Step 4: Test Webhook Endpoint

Send a test message to your bot, then check logs:
```bash
heroku logs --tail | grep -i "webhook\|update\|error"
```

---

## 🐛 Common Issues

### Issue 1: Webhook Not Set
**Symptom:** No updates received
**Fix:** Run `/setwebhook/auto` endpoint

### Issue 2: Webhook URL Wrong
**Symptom:** Updates going to wrong URL
**Fix:** Verify URL in webhookinfo matches your app

### Issue 3: Errors in Message Handling
**Symptom:** Updates received but bot doesn't respond
**Fix:** Check logs for errors in `handle_message()`

### Issue 4: API Token Wrong
**Symptom:** Can't set webhook
**Fix:** Check `TELEGRAM_BOT_TOKEN` in Heroku config

---

## ✅ Quick Fix Commands

```bash
# 1. Set webhook
curl https://ttsbot-a572faff13b4.herokuapp.com/setwebhook/auto

# 2. Check webhook status
curl https://ttsbot-a572faff13b4.herokuapp.com/webhookinfo

# 3. Watch logs
heroku logs --tail

# 4. Test bot
# Send /start to your bot on Telegram
```

---

## 🔍 Debugging

### Check if Webhook is Receiving Updates:

1. **Send `/start` to your bot**
2. **Check logs immediately:**
   ```bash
   heroku logs --tail
   ```
3. **Look for:**
   - `Received update: <number>` ✅ Good
   - `Error handling message:` ❌ Problem
   - No log entry ❌ Webhook not set

### Check Webhook Configuration:

```bash
# Get webhook info
heroku run python -c "
import os
import requests
token = os.environ['TELEGRAM_BOT_TOKEN']
response = requests.get(f'https://api.telegram.org/bot{token}/getWebhookInfo')
print(response.json())
"
```

---

## 📋 Checklist

- [ ] Webhook is set (`/webhookinfo` shows correct URL)
- [ ] Webhook URL matches your app URL
- [ ] `TELEGRAM_BOT_TOKEN` is set in Heroku config
- [ ] App is running (`heroku ps` shows `web.1: up`)
- [ ] Logs show updates being received
- [ ] No errors in logs when sending messages

---

## 🚀 Most Likely Fix

**Just set the webhook:**

Visit: `https://ttsbot-a572faff13b4.herokuapp.com/setwebhook/auto`

Then test by sending `/start` to your bot!

---

**After setting webhook, your bot should respond! 🎉**

