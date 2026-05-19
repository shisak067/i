import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import *
from utils import *
from maintenance import check_maintenance
from keyboards import get_admin_keyboard, get_revoke_keys_keyboard, get_cancel_keyboard
from formatter import format_keys

# ==================== GENERATE KEYS ====================
async def generate_keys_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Only admins can generate keys!")
        return
    
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "Usage:\n\n"
            "1. /gen count credits - Generate normal keys\n"
            "   Example: /gen 20 10\n\n"
            "2. /gen type count credits - Generate custom type keys\n"
            "   Example: /gen KING 10 10"
        )
        return
    
    try:
        if len(args) == 2:
            count = int(args[0])
            credits = int(args[1])
            key_type = "normal"
        elif len(args) == 3:
            key_type = args[0].upper()
            count = int(args[1])
            credits = int(args[2])
        else:
            await update.message.reply_text("Invalid format! Use: /gen [type] count credits")
            return
        
        if count <= 0 or count > 500:
            await update.message.reply_text("Count must be between 1 and 500")
            return
        
        if credits <= 0 or credits > 100000:
            await update.message.reply_text("Credits must be between 1 and 100000")
            return
        
        await update.message.reply_text(f"Generating {count} keys with {credits} credits each...")
        
        keys = generate_keys(key_type, count, credits)
        
        key_text = format_keys(key_type, count, credits, keys)
        
        if len(key_text) > 4000:
            file_path = f"/tmp/keys_{datetime.now().timestamp()}.txt"
            with open(file_path, 'w') as f:
                f.write(key_text)
            with open(file_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename="generated_keys.txt",
                    caption=f"Generated {count} keys of type {key_type}"
                )
            os.unlink(file_path)
        else:
            await update.message.reply_text(key_text)
        
    except ValueError:
        await update.message.reply_text("Invalid numbers! Use: /gen [type] count credits\nExample: /gen 20 10")
    except Exception as e:
        await update.message.reply_text(f"Error generating keys: {str(e)}")

# ==================== REVOKE KEYS ====================
async def revoke_keys_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Only admins can revoke keys!")
        return
    await update.message.reply_text(
        "Revoke Keys Menu\n\n"
        "• Revoke Single Key - Delete a specific unused key\n"
        "• Revoke All Unused - Delete all unused keys\n"
        "• Revoke By Type - Delete unused keys of a specific type",
        reply_markup=get_revoke_keys_keyboard()
    )

async def revoke_single_key_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    await update.message.reply_text(
        "Enter the key to revoke:\n\nExample: ABC123XYZ456 or KING_XYZ123",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_REVOKE_KEY

async def revoke_single_key_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    key = update.message.text.strip()
    
    if key == "Cancel" or key == "Back":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    success, message = revoke_key(key)
    await update.message.reply_text(message, reply_markup=get_admin_keyboard())
    return ConversationHandler.END

async def revoke_all_unused(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Only admins can revoke keys!")
        return
    
    await update.message.reply_text("Revoking all unused keys...")
    success, message = revoke_all_unused_keys("all")
    await update.message.reply_text(message, reply_markup=get_admin_keyboard())

async def revoke_by_type_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END
    
    all_keys = mongo.get_all_keys()
    key_types = set()
    for key in all_keys:
        if not key.get("is_used", False):
            key_types.add(key.get("key_type", "normal"))
    
    if not key_types:
        await update.message.reply_text("No unused keys found!", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    keyboard = []
    for kt in key_types:
        keyboard.append([KeyboardButton(f"Revoke {kt}")])
    keyboard.append([KeyboardButton("Back")])
    
    await update.message.reply_text(
        "Select key type to revoke:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ASKING_REVOKE_KEY_ID

async def revoke_by_type_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if text == "Back":
        await update.message.reply_text("Cancelled", reply_markup=get_admin_keyboard())
        return ConversationHandler.END
    
    if text.startswith("Revoke "):
        key_type = text.replace("Revoke ", "")
        await update.message.reply_text(f"Revoking all unused keys of type '{key_type}'...")
        success, message = revoke_all_unused_keys(key_type)
        await update.message.reply_text(message, reply_markup=get_admin_keyboard())
    
    return ConversationHandler.END

async def show_unused_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Only admins can view unused keys!")
        return
    
    unused_keys = get_unused_keys()
    
    if not unused_keys:
        await update.message.reply_text("No unused keys found!", reply_markup=get_admin_keyboard())
        return
    
    by_type = {}
    for key in unused_keys:
        ktype = key.get("key_type", "normal")
        if ktype not in by_type:
            by_type[ktype] = []
        by_type[ktype].append(key["key"])
    
    output = f"UNUSED KEYS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nTotal: {len(unused_keys)}\n\n"
    
    for ktype, keys in by_type.items():
        output += f"{ktype} ({len(keys)}):\n"
        for k in keys[:10]:
            output += f"{k}\n"
        if len(keys) > 10:
            output += f"... and {len(keys) - 10} more\n"
        output += "\n"
    
    await update.message.reply_text(output[:4000] if len(output) > 4000 else output)
    await update.message.reply_text("Done", reply_markup=get_admin_keyboard())

async def key_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Only admins can view key stats!")
        return
    
    all_keys = mongo.get_all_keys()
    total_keys = len(all_keys)
    used_keys = sum(1 for k in all_keys if k.get("is_used", False))
    unused_keys = total_keys - used_keys
    
    key_types = {}
    for key in all_keys:
        ktype = key.get("key_type", "unknown")
        if ktype not in key_types:
            key_types[ktype] = {"total": 0, "used": 0}
        key_types[ktype]["total"] += 1
        if key.get("is_used", False):
            key_types[ktype]["used"] += 1
    
    text = f"""
KEY STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Keys: {total_keys}
Used Keys: {used_keys}
Unused Keys: {unused_keys}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

By Type:"""
    
    for ktype, stats in key_types.items():
        text += f"\n• {ktype}: {stats['used']}/{stats['total']} used"
    
    await update.message.reply_text(text, reply_markup=get_admin_keyboard())
