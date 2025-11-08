# ✅ Webhook URL Added to Code

## 📍 Webhook URL Configuration

The webhook URL is now configured directly in the code!

### Location: `bot/config.py`

```python
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://ttsbot-a572faff13b4.herokuapp.com/webhook')
```

### Current Webhook URL:
```
https://ttsbot-a572faff13b4.herokuapp.com/webhook
```

---

## 🚀 How to Set Webhook

### Option 1: Automatic (Using Config)
Visit this URL in your browser:
```
https://ttsbot-a572faff13b4.herokuapp.com/setwebhook/auto
```

### Option 2: Manual (With Custom URL)
Visit:
```
https://ttsbot-a572faff13b4.herokuapp.com/setwebhook?url=https://ttsbot-a572faff13b4.herokuapp.com/webhook
```

### Option 3: Using Script
```bash
python setup_webhook.py
```

### Option 4: Heroku CLI
```bash
heroku run python setup_webhook.py
```

---

## 🔧 Change Webhook URL

### Method 1: Edit Config File
Edit `bot/config.py`:
```python
WEBHOOK_URL = 'https://your-new-app.herokuapp.com/webhook'
```

### Method 2: Environment Variable (Heroku)
```bash
heroku config:set WEBHOOK_URL="https://your-new-app.herokuapp.com/webhook"
```

---

## ✅ Features Added

1. **Webhook URL in Config** - `bot/config.py`
2. **Auto-set Endpoint** - `/setwebhook/auto`
3. **Manual Set Endpoint** - `/setwebhook?url=...`
4. **Updated Script** - `setup_webhook.py` uses config
5. **Optional Auto-set** - Uncomment in `app.py` to auto-set on startup

---

## 📝 Usage Examples

### Check Webhook Status:
```
https://ttsbot-a572faff13b4.herokuapp.com/webhookinfo
```

### Set Webhook Automatically:
```
https://ttsbot-a572faff13b4.herokuapp.com/setwebhook/auto
```

### Set Webhook Manually:
```
https://ttsbot-a572faff13b4.herokuapp.com/setwebhook?url=https://ttsbot-a572faff13b4.herokuapp.com/webhook
```

---

## 🎯 Benefits

✅ **No manual configuration needed** - URL is in code  
✅ **Easy to change** - Edit one line in config  
✅ **Environment variable support** - Override via Heroku config  
✅ **Auto-set endpoint** - One-click webhook setup  
✅ **Script support** - Use setup_webhook.py  

---

**Your webhook URL is now configured in code! 🎉**

