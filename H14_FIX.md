# 🔧 Fix H14 Error: "No web processes running"

## 🚨 Error Explanation

**H14 Error** means Heroku can't start your web dyno. This happens when:
1. App crashes on startup
2. Procfile has syntax errors
3. Missing dependencies
4. Import errors

---

## ✅ Fixes Applied

### 1. **Updated Procfile**
Simplified Procfile to avoid potential issues:
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1 --threads 2
```

### 2. **Check App Startup**

**Test locally:**
```bash
# Simulate Heroku startup
PORT=5000 gunicorn app:app --bind 0.0.0.0:5000
```

**Check for errors:**
```bash
# Test imports
python -c "import app; print('OK')"
```

---

## 🔧 Troubleshooting Steps

### Step 1: Check Build Logs
```bash
heroku logs --tail
```

Look for:
- ❌ Import errors
- ❌ Missing modules
- ❌ Syntax errors
- ❌ Configuration errors

### Step 2: Scale Dyno
```bash
heroku ps:scale web=1
```

### Step 3: Check Procfile
```bash
cat Procfile
```

Should be:
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1 --threads 2
```

### Step 4: Check Requirements
```bash
heroku run python -c "import app"
```

### Step 5: Restart
```bash
heroku restart
```

---

## 🐛 Common Causes

### 1. Import Errors
**Symptom:** App crashes on import
**Fix:** Check `heroku logs` for import errors

### 2. Missing Dependencies
**Symptom:** ModuleNotFoundError
**Fix:** Check `requirements.txt` has all packages

### 3. Port Binding Issue
**Symptom:** Can't bind to PORT
**Fix:** Use `$PORT` in Procfile (already done)

### 4. Memory Issues
**Symptom:** Dyno crashes
**Fix:** Reduce workers in Procfile

---

## ✅ Quick Fix Commands

```bash
# 1. Scale dyno
heroku ps:scale web=1

# 2. Check logs
heroku logs --tail

# 3. Restart
heroku restart

# 4. Test locally
PORT=5000 gunicorn app:app --bind 0.0.0.0:5000
```

---

## 📋 Deployment Checklist

- [ ] Procfile exists and is correct
- [ ] requirements.txt has all dependencies
- [ ] app.py imports successfully
- [ ] No syntax errors
- [ ] Dyno is scaled: `heroku ps:scale web=1`
- [ ] Check logs: `heroku logs --tail`

---

## 🚀 After Fix

Once fixed, verify:
1. Visit: `https://ttsbot-a572faff13b4.herokuapp.com/`
2. Check: `heroku ps` (should show web.1: up)
3. Test: `/health` endpoint

---

**Most likely fix:**
```bash
heroku ps:scale web=1
heroku restart
```

