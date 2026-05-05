# Bot Troubleshooting Guide - pella.app

## Issue: Bot Stuck at "Starting..."

### Quick Fix Checklist:

1. **Check BOT_TOKEN is Set**
   - Go to pella.app dashboard
   - Click **Settings** → **Environment Variables**
   - Verify `BOT_TOKEN` is set (should look like: `123456789:ABCdefGHIjklmnoPQRstuvWXYZ`)
   - If missing, get it from [@BotFather](https://t.me/botfather)

2. **Verify ADMIN_CHAT_ID**
   - `ADMIN_CHAT_ID` should be your Telegram user ID (numbers only)
   - Can be obtained by running `/myid` in the bot
   - Can be left empty initially (bot will still work)

3. **Restart the Bot**
   - Go to pella.app dashboard
   - Click "Restart" or "Stop" then "Start"
   - Check console for new output

4. **Check Console Output**
   - Look for any error messages
   - Bot should print checkmarks ✅ for variables found
   - Should show "🚀 Starting bot polling..." when ready

---

## What Should Happen:

When working correctly, console should show:
```
🔍 Checking environment variables...
BOT_TOKEN: ✅ Found
ADMIN_CHAT_ID: your_id_here

============================================================
🤖 DEXKIT BOT IS STARTING...
============================================================
🚀 Starting bot polling...
```

---

## Common Issues & Solutions:

### "BOT_TOKEN: ❌ Not found"
- **Solution**: Add BOT_TOKEN to pella.app environment variables
- Get token from [@BotFather](https://t.me/botfather)

### Bot restarts repeatedly
- **Solution**: Check BOT_TOKEN format - should be `numbers:LettersAndNumbers`
- Verify no extra spaces or quotes

### No response to messages
- **Solution**: Make sure bot is in "Polling" mode (default)
- Check that bot has permission to send messages

### Console shows errors
- **Solution**: 
  - Check pella.app logs
  - Verify all dependencies in requirements.txt
  - Restart the bot

---

## How to Get BOT_TOKEN:

1. Open Telegram
2. Search for **@BotFather**
3. Send `/newbot`
4. Choose a name for your bot
5. Copy the token provided (looks like: `123456789:ABCdefGHIjklmnoPQRstuvWXYZ`)
6. Paste in pella.app environment variables as `BOT_TOKEN`

---

## Need More Help?

- Check pella.app console for specific error messages
- Visit [pella Discord](https://discord.gg/QWVhbD9THW)
- Check [@BotFather](https://t.me/botfather) for token issues
