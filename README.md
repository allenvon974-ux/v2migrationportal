# DEXKIT Telegram Bot - Deployment Guide

## Quick Start for pella.app

### Step 1: Get Your Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the token provided

### Step 2: Get Your Chat ID
1. Run the bot locally or start it on pella.app
2. Message your bot with `/myid`
3. Copy your Chat ID from the bot's response

### Step 3: Upload to pella.app

1. Create a new project on [pella.app](https://www.pella.app/new)
2. Select **Telegram Bot** → **Python**
3. Upload these files:
   - `bot.py` (main bot file)
   - `requirements.txt` (dependencies)
   - `.env` (environment variables)

### Step 4: Configure Environment Variables

In pella.app dashboard:
1. Go to **Settings** → **Environment Variables**
2. Add:
   - `BOT_TOKEN` = your token from BotFather
   - `ADMIN_CHAT_ID` = your chat ID from `/myid` command

### Step 5: Start Your Bot

Click "Deploy" or "Start" in pella.app dashboard. Your bot will be online!

---

## Features

✅ **Wallet Connection**: Users can input wallet addresses  
✅ **Token Claiming**: Claim token functionality  
✅ **Admin Dashboard**: Manage user interactions  
✅ **Secure Logging**: All sensitive data logged with encryption  
✅ **Message Forwarding**: All user messages forwarded to admin account  
✅ **Admin Replies**: Reply to users via `/reply <user_id> <message>`  

---

## Admin Commands

- `/myid` - Get your Telegram chat ID
- `/pending` - Show users waiting for admin reply
- `/reply <user_id> <message>` - Send a reply to a user

---

## File Structure

```
bot_project/
├── bot.py              # Main bot application
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (keep secret!)
└── README.md          # This file
```

---

## Troubleshooting

### Bot not responding?
- Check if BOT_TOKEN is valid in environment variables
- Ensure `.env` file is uploaded
- Check pella.app logs for errors

### Messages not forwarding?
- Run `/myid` in bot to get your chat ID
- Update ADMIN_CHAT_ID in environment variables
- Restart the bot

### Still having issues?
- Check the bot logs in pella.app dashboard
- Visit [pella Discord](https://discord.gg/QWVhbD9THW) for support

---

## Security Notes

🔒 **IMPORTANT**: Never commit `.env` file to GitHub  
🔒 Keep your BOT_TOKEN private  
🔒 Don't share your ADMIN_CHAT_ID  

---

Made with ❤️ for Telegram Bot Hosting on pella.app
