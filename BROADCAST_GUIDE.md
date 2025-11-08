# 📢 User Tracking & Broadcast Features

## 🎯 New Features Added

### 1️⃣ **Automatic User Tracking**
- Every new user is automatically saved to `userid.json`
- Owner receives instant notification when a new user starts the bot
- Updated `userid.json` file is sent to owner automatically

### 2️⃣ **Broadcast System**
- Owner can send messages to all users
- Supports text, photos, videos, audio, and all media types
- Real-time progress tracking
- Detailed delivery statistics

### 3️⃣ **Bot Statistics**
- View total user count
- Access user database anytime
- Monitor bot performance

---

## 📋 Owner Commands

### `/broadcast` - Send Message to All Users

**Usage:**
1. Send `/broadcast` command
2. Bot shows total user count
3. Send your message (text or media)
4. Bot broadcasts to all users with progress updates

**Example:**
```
You: /broadcast

Bot: 📢 Broadcast Mode
     👥 Total Users: 7,299
     📝 Send me the message you want to broadcast...

You: 🎉 New feature update! Check out our latest voices!

Bot: 📤 Broadcasting...
     📊 Progress: 7,299/7,299
     ✅ Sent: 7,250
     ❌ Failed: 49
```

**Features:**
- ✅ Sends any message type (text, photo, video, etc.)
- ✅ Real-time progress updates every 50 users
- ✅ Tracks blocked users separately
- ✅ Shows detailed success/failure statistics
- ✅ Automatic rate limiting to avoid bans
- ❌ Cancel anytime with `/cancel`

---

### `/stats` - View Bot Statistics

**Usage:**
```
You: /stats

Bot: 📊 Bot Statistics
     👥 Total Registered Users: 7,299
     🤖 Bot Status: Active
     
     💡 Use /broadcast to message all users
     📋 Use /getuserlist to download user database
```

---

### `/getuserlist` - Download User Database

**Usage:**
```
You: /getuserlist

Bot: [Sends userid.json file]
     📋 User Database
     👥 Total Users: 7,299
```

---

## 🔔 Automatic Notifications

### New User Alert

When a new user starts the bot, you automatically receive:

```
Bot: 🎉 New User Alert!
     
     👤 User ID: 1234567890
     📊 Total Users: 7,300
     
     📎 Updated user database attached below.
     
     [userid.json file attached]
```

**What happens:**
1. User sends `/start` for the first time
2. User is added to `userid.json`
3. You receive notification with user ID
4. Updated `userid.json` is sent to you
5. User continues with normal bot flow

---

## 📊 Broadcast Statistics Explained

After each broadcast, you receive a detailed report:

```
✅ Broadcast Complete!

📊 Statistics:
👥 Total Users: 7,299
✅ Successfully Sent: 7,250
🚫 Blocked Bot: 35
❌ Failed: 14

📈 Success Rate: 99.3%
```

**Metrics:**
- **Total Users**: Users in database
- **Successfully Sent**: Messages delivered
- **Blocked Bot**: Users who blocked the bot
- **Failed**: Other delivery failures
- **Success Rate**: Percentage of successful deliveries

---

## 🛡️ Security Features

### Owner-Only Access
All broadcast features are **restricted to bot owner only**:
- Owner ID: `890382857` (configured in `bot/config.py`)
- Non-owners see: "⛔ This command is only available to the bot owner."

### Rate Limiting
- 50ms delay between messages (20 messages/second)
- Progress updates every 50 users
- Prevents Telegram rate limit bans

### Error Handling
- Gracefully handles blocked users
- Logs all failures for debugging
- Continues broadcasting even if some fail

---

## 📁 Technical Details

### File Structure

```
bot/
├── user_manager.py           # User tracking logic
└── handlers/
    └── broadcast_handler.py  # Broadcast commands

userid.json                   # User database (auto-updated)
```

### User Database Format

```json
[
    1587132450,
    923532098,
    6552312083,
    ...
]
```

Simple JSON array of user IDs, automatically sorted.

---

## 🎨 Usage Examples

### Example 1: Text Announcement
```
/broadcast
→ "🎉 New voices added! Check out our expanded collection!"
```

### Example 2: Photo with Caption
```
/broadcast
→ [Send photo with caption: "New update preview!"]
```

### Example 3: Video Message
```
/broadcast
→ [Send video: Tutorial on using the bot]
```

### Example 4: Formatted Message
```
/broadcast
→ **Important Update**
   
   🔥 New Features:
   • Faster voice generation
   • More language support
   • Better audio quality
```

---

## ⚠️ Important Notes

### Best Practices
1. **Test First**: Send to yourself before broadcasting
2. **Clear Message**: Make sure your message is clear and error-free
3. **Timing**: Broadcast during peak user hours for better engagement
4. **Frequency**: Don't spam - broadcast only when necessary
5. **Monitor Stats**: Check success rate to identify issues

### Limitations
- **Rate Limits**: Telegram has rate limits (handled automatically)
- **No Undo**: Can't recall messages after sending
- **Blocked Users**: Will show as failed, this is normal
- **Large Broadcasts**: 7000+ users takes ~6 minutes

### Troubleshooting

**Problem: Low success rate**
- Solution: Check if bot token is valid
- Solution: Ensure bot has proper permissions

**Problem: Broadcast timing out**
- Solution: This is normal for large user bases
- Solution: Bot will continue in background

**Problem: Users not receiving**
- Solution: They may have blocked the bot
- Solution: Check their user ID is in database

---

## 🔧 Configuration

### Change Owner ID
Edit `bot/config.py`:
```python
OWNER_ID = 890382857  # Your Telegram user ID
```

### Adjust Broadcast Speed
Edit `bot/handlers/broadcast_handler.py`:
```python
await asyncio.sleep(0.05)  # Delay in seconds
```

### Progress Update Frequency
Edit `bot/handlers/broadcast_handler.py`:
```python
if idx % 50 == 0:  # Update every N users
```

---

## 📈 Future Enhancements

Potential features for future versions:
- [ ] Scheduled broadcasts
- [ ] User segmentation (by country/language)
- [ ] Message templates
- [ ] Analytics dashboard
- [ ] Broadcast history
- [ ] A/B testing support
- [ ] Reply tracking

---

## 🆘 Support

If you encounter issues:
1. Check bot logs: Look at terminal output
2. Verify owner ID: Must match your Telegram user ID
3. Test with `/stats`: Ensure bot can access user database
4. Check file permissions: `userid.json` must be writable

---

**Happy Broadcasting! 📢**

