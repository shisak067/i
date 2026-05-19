import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import *
from utils import *
from maintenance import check_maintenance
from keyboards import get_main_keyboard, get_cancel_keyboard
from formatter import format_system_info, format_raw_result
from api_handler import *

# ==================== START COMMAND ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    
    user = update.effective_user
    args = context.args
    
    if args and args[0].startswith("ref_"):
        process_referral(user.id, args[0][4:])
    
    user_data = get_user(user.id)
    if user.username:
        user_data["username"] = user.username
        mongo.save_user(user_data)
    
    # New user alert to admins
    if user_data.get("total_searches", 0) == 0:
        alert_text = f"NEW USER JOINED!\n\nUser: {user.first_name}\nID: {user.id}\nUsername: @{user.username or 'None'}"
        
        for admin_id in OWNER_IDS:
            try:
                await context.bot.send_message(admin_id, alert_text)
            except:
                pass
        
        all_users = mongo.get_all_users()
        for u in all_users:
            if u.get("is_admin", False) and u["user_id"] not in OWNER_IDS:
                try:
                    await context.bot.send_message(u["user_id"], alert_text)
                except:
                    pass
    
    welcome = f"""
Welcome {user.first_name}!

{BOT_NAME} v{BOT_VERSION}

Available Services:
• Indian Number & Aadhar
• Pakistan Number, CNIC, Police
• GST Billing & PAN to GST
• Aadhar Family Details

Free {settings['daily_limit']} searches/day
1 coin = 1 extra search
Referral: +{settings['referral_coins']} coins

Start searching now!
"""
    await update.message.reply_text(welcome, reply_markup=get_main_keyboard(user.id))

# ==================== USER COMMANDS ====================
async def my_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    user = get_user(update.effective_user.id)
    if has_unlimited_coins(update.effective_user.id):
        text = "ADMIN/OWNER\nCoins: UNLIMITED"
    else:
        text = f"YOUR BALANCE\nCoins: {user['coins']}\n\nShare referral link to earn {settings['referral_coins']} coins!"
    await update.message.reply_text(text)

async def referral_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    user = get_user(update.effective_user.id)
    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start=ref_{user['referral_code']}"
    text = f"YOUR REFERRAL LINK\n{link}\n\nEarn {settings['referral_coins']} coins per referral!"
    await update.message.reply_text(text, disable_web_page_preview=True)

async def my_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    user = get_user(update.effective_user.id)
    today = date.today().isoformat()
    daily = 0 if user["last_search_date"] != today else user["daily_searches"]
    remaining = settings["daily_limit"] - daily
    
    history = mongo.get_search_history(update.effective_user.id, 1000)
    
    text = f"""
YOUR STATISTICS
┌─────────────────────────┐
│ Total Searches: {user['total_searches']}    │
│ Today: {daily}/{settings['daily_limit']}          │
│ Remaining: {remaining}            │
│ Coins: {user['coins']}               │
│ Referrals: {len(user.get('referrals', []))}    │
│ History: {len(history)} records        │
└─────────────────────────┘
"""
    await update.message.reply_text(text)

async def buy_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("50 Coins - Rs30", callback_data="buy_50")],
        [InlineKeyboardButton("100 Coins - Rs50", callback_data="buy_100")],
        [InlineKeyboardButton("250 Coins - Rs120", callback_data="buy_250")],
        [InlineKeyboardButton("500 Coins - Rs200", callback_data="buy_500")],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])
    text = f"BUY COINS\n\nUPI: {UPI_ID}\nContact: @{SUPPORT_USERNAME}"
    await update.message.reply_text(text, reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    text = f"""
HELP MENU

Commands:
/num <number> - Indian Number
/aadhar <aadhar> - Indian Aadhar
/stats - Your statistics
/coins - Check coins
/referral - Referral link
/redeem - Redeem key
/system - System info

Support: @{SUPPORT_USERNAME}
"""
    await update.message.reply_text(text)

async def system_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    from config import MAINTENANCE_MODE
    info = format_system_info(MAINTENANCE_MODE, settings)
    await update.message.reply_text(info)

async def search_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    user_id = update.effective_user.id
    history = mongo.get_search_history(user_id, 20)
    
    if not history:
        await update.message.reply_text("No search history found")
        return
    
    output = "YOUR SEARCH HISTORY\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, h in enumerate(history[:20], 1):
        timestamp = h.get("timestamp", datetime.now()).strftime("%Y-%m-%d %H:%M")
        output += f"{i}. {h.get('search_type', 'Unknown')}\n   Query: {h.get('query', '?')}\n   Date: {timestamp}\n\n"
    
    if len(output) > 4000:
        await update.message.reply_text("History too long, sending as file...")
    else:
        await update.message.reply_text(output)

# ==================== REDEEM KEY ====================
async def redeem_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    user_id = update.effective_user.id
    await update.message.reply_text(
        "Enter your redemption key:\n\nExample: ABC123XYZ456\n\nSend key to redeem coins",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_REDEEM_KEY

async def handle_redeem_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    key = update.message.text.strip()
    
    if key == "Cancel" or key == "Back":
        await update.message.reply_text("Cancelled", reply_markup=get_main_keyboard(user_id))
        return ConversationHandler.END
    
    success, message = redeem_key(user_id, key)
    await update.message.reply_text(message, reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

# ==================== COMMAND HANDLERS ====================
async def num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not settings.get("bot_active", True) and not is_admin(update.effective_user.id):
        await update.message.reply_text("Bot is currently disabled by admin!")
        return
    if not context.args:
        await update.message.reply_text("Usage: /num 9876543210")
        return
    user_id = update.effective_user.id
    can, _, use_coin_flag = can_search(user_id)
    if not can:
        await update.message.reply_text("Daily limit reached!")
        return
    if use_coin_flag:
        use_coin(user_id)
    
    number = context.args[0]
    await update.message.chat.send_action(action="typing")
    result = await search_indian_number(number)
    if "error" not in result:
        update_user_stats(user_id)
        save_search_result(user_id, "indian_number", number, result)
    formatted = format_raw_result(result, number, "Indian Number")
    await update.message.reply_text(formatted)

async def aadhar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not settings.get("bot_active", True) and not is_admin(update.effective_user.id):
        await update.message.reply_text("Bot is currently disabled by admin!")
        return
    if not context.args:
        await update.message.reply_text("Usage: /aadhar 123456789012")
        return
    user_id = update.effective_user.id
    can, _, use_coin_flag = can_search(user_id)
    if not can:
        await update.message.reply_text("Daily limit reached!")
        return
    if use_coin_flag:
        use_coin(user_id)
    
    aadhar = context.args[0]
    await update.message.chat.send_action(action="typing")
    result = await search_indian_aadhar(aadhar)
    if "error" not in result:
        update_user_stats(user_id)
        save_search_result(user_id, "indian_aadhar", aadhar, result)
    formatted = format_raw_result(result, aadhar, "Indian Aadhar")
    await update.message.reply_text(formatted)
