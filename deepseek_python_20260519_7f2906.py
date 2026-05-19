from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import *
from utils import *
from maintenance import check_maintenance, toggle_maintenance_mode, is_maintenance_mode
from keyboards import get_admin_keyboard, get_api_settings_keyboard, get_api_select_keyboard, get_cancel_keyboard
from formatter import format_system_info
from api_handler import *

# ==================== ADMIN PANEL ====================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text("Admin Panel", reply_markup=get_admin_keyboard())

async def bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    
    stats = mongo.get_stats()
    uptime = get_bot_uptime()
    sys_info = get_system_info()
    
    text = f"""
BOT STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bot Info:
• Name: {BOT_NAME}
• Version: {BOT_VERSION}
• Uptime: {uptime}
• Status: {'ACTIVE' if settings['bot_active'] else 'INACTIVE'}
• Maintenance: {'ACTIVE' if is_maintenance_mode() else 'INACTIVE'}

Users:
• Total: {stats['total_users']}
• Blocked: {len([u for u in mongo.get_all_users() if u.get('is_blocked', False)])}

Searches:
• Total: {stats['total_searches']}
• Daily Limit: {settings['daily_limit']}

Keys:
• Generated: {stats['total_keys']}
• Used: {stats['used_keys']}
• Unused: {stats['total_keys'] - stats['used_keys']}

System:
• CPU: {sys_info['cpu_percent']}%
• RAM: {sys_info['memory_percent']}%
• Disk: {sys_info['disk_percent']}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(text, reply_markup=get_admin_keyboard())

async def toggle_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    settings["bot_active"] = not settings["bot_active"]
    mongo.save_setting("bot_active", settings["bot_active"])
    status = "ACTIVE" if settings["bot_active"] else "INACTIVE"
    await update.message.reply_text(f"Bot is now {status}", reply_markup=get_admin_keyboard())

async def maintenance_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    
    status = toggle_maintenance_mode()
    await update.message.reply_text(
        f"Maintenance mode is now {'ACTIVE' if status else 'INACTIVE'}\n\n"
        f"Users will see: {MAINTENANCE_MESSAGE}",
        reply_markup=get_admin_keyboard()
    )

async def set_daily_limit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    await update.message.reply_text(
        f"Set Daily Search Limit\nCurrent: {settings['daily_limit']}\n\nEnter new limit:",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_SET_DAILY_LIMIT

async def set_daily_limit_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    text = update.message.text.strip()
    if text == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    try:
        limit = int(text)
        if limit < 1:
            raise ValueError
        settings["daily_limit"] = limit
        mongo.save_setting("daily_limit", limit)
        await update.message.reply_text(f"Daily limit set to {limit}", reply_markup=get_admin_keyboard())
    except:
        await update.message.reply_text("Invalid limit! Enter a positive number.", reply_markup=get_cancel_keyboard())
        return ASKING_SET_DAILY_LIMIT
    return ConversationHandler.END

async def all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    
    all_users_list = mongo.get_all_users()
    total = len(all_users_list)
    
    if total == 0:
        await update.message.reply_text("No users found", reply_markup=get_admin_keyboard())
        return
    
    text = f"Total Users: {total}\n\n"
    
    for i, user in enumerate(all_users_list[:20], 1):
        uid = user.get('user_id')
        username = user.get('username', 'No username')
        coins = user.get('coins', 0)
        searches = user.get('total_searches', 0)
        is_blocked = user.get('is_blocked', False)
        blocked_mark = "BLOCKED " if is_blocked else ""
        text += f"{i}. {blocked_mark}{uid} - @{username}\n   {coins} coins | {searches} searches\n"
    
    if total > 20:
        text += f"\n... and {total - 20} more users"
    
    await update.message.reply_text(text[:4000] if len(text) > 4000 else text, reply_markup=get_admin_keyboard())

async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    
    admins = list(OWNER_IDS)
    all_users_list = mongo.get_all_users()
    for user in all_users_list:
        if user.get("is_admin", False) and user['user_id'] not in admins:
            admins.append(user['user_id'])
    
    text = "ADMIN LIST\n\n"
    for uid in admins:
        user_data = get_user(uid)
        username = user_data.get("username", "No username")
        role = "OWNER" if uid in OWNER_IDS else "ADMIN"
        text += f"• {uid} - @{username} ({role})\n"
    
    await update.message.reply_text(text, reply_markup=get_admin_keyboard())

async def blocked_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    
    blocked_numbers_list = mongo.get_all_blocked_numbers()
    
    if not blocked_numbers_list:
        await update.message.reply_text("No blocked numbers", reply_markup=get_admin_keyboard())
        return
    
    text = "BLOCKED NUMBERS\n\n"
    for num_data in blocked_numbers_list[:30]:
        num = num_data.get('number')
        reason = num_data.get('reason', 'No reason')
        blocked_by = num_data.get('blocked_by', 'Unknown')
        text += f"Number: {num}\n   Reason: {reason}\n   Blocked by: {blocked_by}\n\n"
    
    if len(blocked_numbers_list) > 30:
        text += f"\n... and {len(blocked_numbers_list) - 30} more"
    
    await update.message.reply_text(text, reply_markup=get_admin_keyboard())

# ==================== BROADCAST ====================
async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    await update.message.reply_text("Send your broadcast message:", reply_markup=get_cancel_keyboard())
    return ASKING_BROADCAST

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    text = update.message.text
    if text == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    msg = await update.message.reply_text("Broadcasting...")
    success = 0
    failed = 0
    blocked = 0
    
    all_users_list = mongo.get_all_users()
    
    for user_data in all_users_list:
        uid = user_data['user_id']
        try:
            if user_data.get("is_blocked", False):
                blocked += 1
                continue
            await context.bot.send_message(uid, text)
            success += 1
        except:
            failed += 1
        await asyncio.sleep(0.05)
    
    await msg.edit_text(f"Broadcast Complete\nSent: {success}\nFailed: {failed}\nBlocked skipped: {blocked}")
    await update.message.reply_text("Done", reply_markup=get_admin_keyboard())
    return ConversationHandler.END

# ==================== BLOCK/UNBLOCK NUMBER ====================
async def block_number_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    await update.message.reply_text("Enter number to block:\nExample: 9876543210", reply_markup=get_cancel_keyboard())
    return ASKING_BLOCK_NUMBER

async def block_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    text = update.message.text.strip()
    if text == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    number = ''.join(filter(str.isdigit, text))
    if len(number) < 10:
        await update.message.reply_text("Invalid number!", reply_markup=get_cancel_keyboard())
        return ASKING_BLOCK_NUMBER
    
    mongo.save_blocked_number(number, {
        "blocked_by": update.effective_user.id,
        "reason": "Blocked by admin",
        "date": datetime.now().isoformat()
    })
    await update.message.reply_text(f"Number blocked: {number}", reply_markup=get_admin_keyboard())
    return ConversationHandler.END

async def unblock_number_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    await update.message.reply_text("Enter number to unblock:\nExample: 9876543210", reply_markup=get_cancel_keyboard())
    return ASKING_UNBLOCK_NUMBER

async def unblock_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    text = update.message.text.strip()
    if text == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    number = ''.join(filter(str.isdigit, text))
    blocked = mongo.get_blocked_number(number)
    if blocked:
        mongo.remove_blocked_number(number)
        await update.message.reply_text(f"Number unblocked: {number}", reply_markup=get_admin_keyboard())
    else:
        await update.message.reply_text(f"Number not found in block list: {number}", reply_markup=get_admin_keyboard())
    return ConversationHandler.END

# ==================== BLOCK/UNBLOCK USER ====================
async def block_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    await update.message.reply_text(
        "Enter user ID or @username to block:\n\nExample: 123456789 or @username\n\nOptional: Add reason after a space\nExample: 123456789 Spamming",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_BLOCK_USER

async def block_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    
    text = update.message.text.strip()
    if text == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    parts = text.split(" ", 1)
    identifier = parts[0]
    reason = parts[1] if len(parts) > 1 else "Blocked by admin"
    
    user_id = find_user_by_identifier(identifier)
    
    if user_id:
        if user_id in OWNER_IDS:
            await update.message.reply_text("Cannot block the owner!", reply_markup=get_admin_keyboard())
        else:
            block_user(user_id, reason, update.effective_user.id)
            user = get_user(user_id)
            username = user.get("username", "No username")
            
            try:
                await context.bot.send_message(
                    user_id,
                    f"You have been blocked from using this bot!\n\nReason: {reason}\n\nContact @{SUPPORT_USERNAME} for assistance."
                )
            except:
                pass
            
            await update.message.reply_text(f"User blocked: {user_id} (@{username})\nReason: {reason}", reply_markup=get_admin_keyboard())
    else:
        await update.message.reply_text(f"User not found: {identifier}", reply_markup=get_admin_keyboard())
    
    return ConversationHandler.END

async def unblock_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    await update.message.reply_text(
        "Enter user ID or @username to unblock:\n\nExample: 123456789 or @username",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_UNBLOCK_NUMBER

async def unblock_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    
    text = update.message.text.strip()
    if text == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    user_id = find_user_by_identifier(text)
    
    if user_id:
        user = get_user(user_id)
        if user.get("is_blocked", False):
            unblock_user(user_id)
            username = user.get("username", "No username")
            
            try:
                await context.bot.send_message(
                    user_id,
                    f"You have been unblocked!\n\nYou can now use the bot again."
                )
            except:
                pass
            
            await update.message.reply_text(f"User unblocked: {user_id} (@{username})", reply_markup=get_admin_keyboard())
        else:
            await update.message.reply_text(f"User {user_id} is not blocked.", reply_markup=get_admin_keyboard())
    else:
        await update.message.reply_text(f"User not found: {text}", reply_markup=get_admin_keyboard())
    
    return ConversationHandler.END

async def show_blocked_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    
    all_users = mongo.get_all_users()
    blocked_users = [u for u in all_users if u.get("is_blocked", False)]
    
    if not blocked_users:
        await update.message.reply_text("No blocked users", reply_markup=get_admin_keyboard())
        return
    
    output = "BLOCKED USERS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for user in blocked_users[:30]:
        username = user.get("username", "No username")
        reason = user.get("blocked_reason", "No reason")
        blocked_at = user.get("blocked_at", "Unknown")
        output += f"• {user['user_id']} - @{username}\n  {reason}\n  Date: {blocked_at[:10]}\n\n"
    
    if len(blocked_users) > 30:
        output += f"\n... and {len(blocked_users) - 30} more"
    
    await update.message.reply_text(output[:4000] if len(output) > 4000 else output, reply_markup=get_admin_keyboard())

# ==================== ADMIN MANAGEMENT ====================
async def set_referral_coins_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    await update.message.reply_text(f"Enter referral coins amount:\nCurrent: {settings['referral_coins']}\nExample: 15", reply_markup=get_cancel_keyboard())
    return ASKING_REFERRAL_AMOUNT

async def set_referral_coins_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    text = update.message.text.strip()
    if text == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    try:
        amount = int(text)
        if amount < 0:
            raise ValueError
        settings["referral_coins"] = amount
        mongo.save_setting("referral_coins", amount)
        await update.message.reply_text(f"Referral coins set to: {amount}", reply_markup=get_admin_keyboard())
    except:
        await update.message.reply_text("Invalid amount! Enter a positive number.", reply_markup=get_cancel_keyboard())
        return ASKING_REFERRAL_AMOUNT
    return ConversationHandler.END

async def add_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Only owner can add admins!")
        return ConversationHandler.END
    await update.message.reply_text("Enter user ID or @username to add as admin:\nExample: 123456789 or @username", reply_markup=get_cancel_keyboard())
    return ASKING_ADD_ADMIN

async def add_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_owner(update.effective_user.id):
        return ConversationHandler.END
    text = update.message.text.strip()
    if text == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    user_id = find_user_by_identifier(text)
    if user_id:
        user = get_user(user_id)
        user["is_admin"] = True
        mongo.save_user(user)
        await update.message.reply_text(f"Admin added: {user_id}", reply_markup=get_admin_keyboard())
    else:
        await update.message.reply_text(f"User not found: {text}", reply_markup=get_admin_keyboard())
    return ConversationHandler.END

async def remove_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Only owner can remove admins!")
        return ConversationHandler.END
    await update.message.reply_text("Enter user ID or @username to remove from admin:\nExample: 123456789 or @username", reply_markup=get_cancel_keyboard())
    return ASKING_REMOVE_ADMIN

async def remove_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_owner(update.effective_user.id):
        return ConversationHandler.END
    text = update.message.text.strip()
    if text == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    user_id = find_user_by_identifier(text)
    if user_id and user_id not in OWNER_IDS:
        user = get_user(user_id)
        user["is_admin"] = False
        mongo.save_user(user)
        await update.message.reply_text(f"Admin removed: {user_id}", reply_markup=get_admin_keyboard())
    else:
        await update.message.reply_text(f"User not found or is owner: {text}", reply_markup=get_admin_keyboard())
    return ConversationHandler.END

async def add_coins_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    await update.message.reply_text("Enter user ID or @username to add coins:\nExample: 123456789 or @username", reply_markup=get_cancel_keyboard())
    return ASKING_ADD_COINS_USER

async def add_coins_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    text = update.message.text.strip()
    if text == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    user_id = find_user_by_identifier(text)
    if user_id:
        context.user_data["add_coins_user"] = user_id
        await update.message.reply_text("Enter amount of coins to add:\nExample: 50", reply_markup=get_cancel_keyboard())
        return ASKING_ADD_COINS_AMOUNT
    else:
        await update.message.reply_text(f"User not found: {text}", reply_markup=get_admin_keyboard())
        return ConversationHandler.END

async def add_coins_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    text = update.message.text.strip()
    if text == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    try:
        amount = int(text)
        if amount <= 0:
            raise ValueError
        user_id = context.user_data.get("add_coins_user")
        if user_id:
            add_coins(user_id, amount)
            await update.message.reply_text(f"Added {amount} coins to user {user_id}", reply_markup=get_admin_keyboard())
        else:
            await update.message.reply_text("Error: User not found", reply_markup=get_admin_keyboard())
    except:
        await update.message.reply_text("Invalid amount! Enter a positive number.", reply_markup=get_cancel_keyboard())
        return ASKING_ADD_COINS_AMOUNT
    return ConversationHandler.END

# ==================== API SETTINGS ====================
async def api_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text("API Settings\nON = Enabled, OFF = Disabled\nTap to toggle:", reply_markup=get_api_settings_keyboard())

async def api_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    text = "API STATUS\n\n"
    for key, service in API_SERVICES.items():
        status = "ON" if is_api_enabled(key) else "OFF"
        text += f"{service['emoji']} {service['name']}: {status}\n"
    await update.message.reply_text(text, reply_markup=get_api_settings_keyboard())

async def toggle_api_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    text = update.message.text
    
    clean_text = text
    if clean_text.startswith("ON") or clean_text.startswith("OFF"):
        clean_text = clean_text[3:].strip()
    
    for key, service in API_SERVICES.items():
        if service['name'] in clean_text:
            new_status = toggle_api(key)
            status = "ON" if new_status else "OFF"
            await update.message.reply_text(
                f"{service['name']} is now {status}", 
                reply_markup=get_api_settings_keyboard()
            )
            return

async def update_api_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    await update.message.reply_text("Select API to Update:", reply_markup=get_api_select_keyboard())
    return ASKING_API_SELECT

async def update_api_url_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text("API Settings", reply_markup=get_api_settings_keyboard())
        return ConversationHandler.END
    
    for key, service in API_SERVICES.items():
        if service['name'] in text:
            context.user_data["updating_api"] = key
            current_url = get_api_url(key)
            await update.message.reply_text(
                f"Update {service['name']}\n\nCurrent: {current_url}\n\nSend new URL:",
                reply_markup=get_cancel_keyboard()
            )
            return ASKING_API_UPDATE
    return ConversationHandler.END

async def update_api_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    text = update.message.text.strip()
    if text == "Cancel":
        await update.message.reply_text("Cancelled", reply_markup=get_api_settings_keyboard())
        return ConversationHandler.END
    
    if not text.startswith("http"):
        await update.message.reply_text("Invalid URL! Must start with http:// or https://", reply_markup=get_cancel_keyboard())
        return ASKING_API_UPDATE
    
    key = context.user_data.get("updating_api")
    if key:
        if update_api_url(key, text):
            await update.message.reply_text(f"API Updated Successfully!\n{text[:50]}...", reply_markup=get_api_settings_keyboard())
        else:
            await update.message.reply_text("Failed to update API. Please try again.", reply_markup=get_api_settings_keyboard())
    return ConversationHandler.END

# ==================== EXIT ADMIN ====================
async def exit_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text("Exited Admin Panel", reply_markup=get_main_keyboard(update.effective_user.id))

async def back_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text("Admin Panel", reply_markup=get_admin_keyboard())