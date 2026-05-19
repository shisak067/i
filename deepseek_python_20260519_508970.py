from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import *
from utils import *
from maintenance import check_maintenance
from keyboards import get_main_keyboard, get_cancel_keyboard
from formatter import format_raw_result
from api_handler import *

# ==================== SEARCH CHECK ====================
async def check_and_start_search(update: Update, context: ContextTypes.DEFAULT_TYPE, search_type: str) -> bool:
    user_id = update.effective_user.id
    can, remaining, use_coin_flag = can_search(user_id)
    
    if not can:
        user = get_user(user_id)
        await update.message.reply_text(
            f"Daily Limit Reached!\nYour Coins: {user['coins']}\n\nBuy more coins or share referral link!",
            reply_markup=get_main_keyboard(user_id)
        )
        return False
    
    if use_coin_flag:
        await update.message.reply_text("Using 1 coin for this search.")
        context.user_data["use_coin"] = True
    else:
        context.user_data["use_coin"] = False
    
    context.user_data["search_type"] = search_type
    return True

# ==================== SEARCH BUTTON HANDLERS ====================
async def indian_number_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not settings.get("bot_active", True) and not is_admin(update.effective_user.id):
        await update.message.reply_text("Bot is currently disabled by admin!", reply_markup=get_main_keyboard(update.effective_user.id))
        return ConversationHandler.END
    if not await check_and_start_search(update, context, "num"):
        return ConversationHandler.END
    await update.message.reply_text(
        "Enter Indian Mobile Number\nExample: 9876543210",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_NUMBER

async def indian_aadhar_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not settings.get("bot_active", True) and not is_admin(update.effective_user.id):
        await update.message.reply_text("Bot is currently disabled by admin!", reply_markup=get_main_keyboard(update.effective_user.id))
        return ConversationHandler.END
    if not await check_and_start_search(update, context, "aadhar"):
        return ConversationHandler.END
    await update.message.reply_text(
        "Enter 12-digit Aadhar Number\nExample: 123456789012",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_AADHAR

async def pak_number_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not settings.get("bot_active", True) and not is_admin(update.effective_user.id):
        await update.message.reply_text("Bot is currently disabled by admin!", reply_markup=get_main_keyboard(update.effective_user.id))
        return ConversationHandler.END
    if not await check_and_start_search(update, context, "pak_num"):
        return ConversationHandler.END
    await update.message.reply_text(
        "Enter Pakistan Mobile Number\nExample: 3001234567",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_PAK_NUM

async def pak_cnic_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not settings.get("bot_active", True) and not is_admin(update.effective_user.id):
        await update.message.reply_text("Bot is currently disabled by admin!", reply_markup=get_main_keyboard(update.effective_user.id))
        return ConversationHandler.END
    if not await check_and_start_search(update, context, "pak_cnic"):
        return ConversationHandler.END
    await update.message.reply_text(
        "Enter 13-digit Pakistan CNIC\nExample: 1234567890123",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_PAK_CNIC

async def pak_police_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not settings.get("bot_active", True) and not is_admin(update.effective_user.id):
        await update.message.reply_text("Bot is currently disabled by admin!", reply_markup=get_main_keyboard(update.effective_user.id))
        return ConversationHandler.END
    if not await check_and_start_search(update, context, "pak_police"):
        return ConversationHandler.END
    await update.message.reply_text(
        "Enter Pakistan Mobile Number for Police Record\nExample: 3001234567",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_PAK_POLICE

async def gst_billing_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not settings.get("bot_active", True) and not is_admin(update.effective_user.id):
        await update.message.reply_text("Bot is currently disabled by admin!", reply_markup=get_main_keyboard(update.effective_user.id))
        return ConversationHandler.END
    if not await check_and_start_search(update, context, "gst_billing"):
        return ConversationHandler.END
    await update.message.reply_text(
        "Enter 15-digit GSTIN\nExample: 09AAYFK4129N1ZF",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_GST_BILLING

async def pan_gst_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not settings.get("bot_active", True) and not is_admin(update.effective_user.id):
        await update.message.reply_text("Bot is currently disabled by admin!", reply_markup=get_main_keyboard(update.effective_user.id))
        return ConversationHandler.END
    if not await check_and_start_search(update, context, "pan_gst"):
        return ConversationHandler.END
    await update.message.reply_text(
        "Enter 10-character PAN\nExample: AAYFK4129N",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_PAN_GST

async def aadhar_family_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if await check_maintenance(update, context):
        return ConversationHandler.END
    if not settings.get("bot_active", True) and not is_admin(update.effective_user.id):
        await update.message.reply_text("Bot is currently disabled by admin!", reply_markup=get_main_keyboard(update.effective_user.id))
        return ConversationHandler.END
    if not await check_and_start_search(update, context, "aadhar_family"):
        return ConversationHandler.END
    await update.message.reply_text(
        "Enter 12-digit Aadhar Number for Family Details\nExample: 123456789012",
        reply_markup=get_cancel_keyboard()
    )
    return ASKING_AADHAR_FAMILY

# ==================== INPUT HANDLERS ====================
async def handle_indian_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "Cancel" or text == "Back":
        await update.message.reply_text("Cancelled", reply_markup=get_main_keyboard(user_id))
        return ConversationHandler.END
    
    number = ''.join(filter(str.isdigit, text))
    if len(number) < 10:
        await update.message.reply_text("Invalid number!", reply_markup=get_cancel_keyboard())
        return ASKING_NUMBER
    
    if context.user_data.get("use_coin", False):
        if not use_coin(user_id):
            await update.message.reply_text("Not enough coins!", reply_markup=get_main_keyboard(user_id))
            return ConversationHandler.END
    
    await update.message.chat.send_action(action="typing")
    status_msg = await update.message.reply_text("Searching...")
    
    result = await search_indian_number(number)
    await status_msg.delete()
    
    if "error" not in result:
        update_user_stats(user_id)
        save_search_result(user_id, "indian_number", number, result)
    
    formatted = format_raw_result(result, number, "Indian Number")
    await update.message.reply_text(formatted)
    await update.message.reply_text("Search Complete", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

async def handle_indian_aadhar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "Cancel" or text == "Back":
        await update.message.reply_text("Cancelled", reply_markup=get_main_keyboard(user_id))
        return ConversationHandler.END
    
    aadhar = ''.join(filter(str.isdigit, text))
    if len(aadhar) != 12:
        await update.message.reply_text("Invalid Aadhar! Must be 12 digits.", reply_markup=get_cancel_keyboard())
        return ASKING_AADHAR
    
    if context.user_data.get("use_coin", False):
        if not use_coin(user_id):
            await update.message.reply_text("Not enough coins!", reply_markup=get_main_keyboard(user_id))
            return ConversationHandler.END
    
    await update.message.chat.send_action(action="typing")
    status_msg = await update.message.reply_text("Searching Aadhar...")
    
    result = await search_indian_aadhar(aadhar)
    await status_msg.delete()
    
    if "error" not in result:
        update_user_stats(user_id)
        save_search_result(user_id, "indian_aadhar", aadhar, result)
    
    formatted = format_raw_result(result, aadhar, "Indian Aadhar")
    await update.message.reply_text(formatted)
    await update.message.reply_text("Search Complete", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

async def handle_pak_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "Cancel" or text == "Back":
        await update.message.reply_text("Cancelled", reply_markup=get_main_keyboard(user_id))
        return ConversationHandler.END
    
    number = ''.join(filter(str.isdigit, text))
    if context.user_data.get("use_coin", False):
        if not use_coin(user_id):
            await update.message.reply_text("Not enough coins!", reply_markup=get_main_keyboard(user_id))
            return ConversationHandler.END
    
    await update.message.chat.send_action(action="typing")
    status_msg = await update.message.reply_text("Searching Pakistan Number...")
    
    result = await search_pak_number(number)
    await status_msg.delete()
    
    if "error" not in result:
        update_user_stats(user_id)
        save_search_result(user_id, "pak_number", number, result)
    
    formatted = format_raw_result(result, number, "Pakistan Number")
    await update.message.reply_text(formatted)
    await update.message.reply_text("Search Complete", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

async def handle_pak_cnic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "Cancel" or text == "Back":
        await update.message.reply_text("Cancelled", reply_markup=get_main_keyboard(user_id))
        return ConversationHandler.END
    
    cnic = ''.join(filter(str.isdigit, text))
    if len(cnic) != 13:
        await update.message.reply_text("Invalid CNIC! Must be 13 digits.", reply_markup=get_cancel_keyboard())
        return ASKING_PAK_CNIC
    
    if context.user_data.get("use_coin", False):
        if not use_coin(user_id):
            await update.message.reply_text("Not enough coins!", reply_markup=get_main_keyboard(user_id))
            return ConversationHandler.END
    
    await update.message.chat.send_action(action="typing")
    status_msg = await update.message.reply_text("Searching Pakistan CNIC...")
    
    result = await search_pak_cnic(cnic)
    await status_msg.delete()
    
    if "error" not in result:
        update_user_stats(user_id)
        save_search_result(user_id, "pak_cnic", cnic, result)
    
    formatted = format_raw_result(result, cnic, "Pakistan CNIC")
    await update.message.reply_text(formatted)
    await update.message.reply_text("Search Complete", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

async def handle_pak_police(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "Cancel" or text == "Back":
        await update.message.reply_text("Cancelled", reply_markup=get_main_keyboard(user_id))
        return ConversationHandler.END
    
    number = ''.join(filter(str.isdigit, text))
    if context.user_data.get("use_coin", False):
        if not use_coin(user_id):
            await update.message.reply_text("Not enough coins!", reply_markup=get_main_keyboard(user_id))
            return ConversationHandler.END
    
    await update.message.chat.send_action(action="typing")
    status_msg = await update.message.reply_text("Checking Police Records...")
    
    result = await search_pak_police(number)
    await status_msg.delete()
    
    if "error" not in result:
        update_user_stats(user_id)
        save_search_result(user_id, "pak_police", number, result)
    
    formatted = format_raw_result(result, number, "Pakistan Police")
    await update.message.reply_text(formatted)
    await update.message.reply_text("Search Complete", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

async def handle_gst_billing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip().upper()
    if text == "Cancel" or text == "Back":
        await update.message.reply_text("Cancelled", reply_markup=get_main_keyboard(user_id))
        return ConversationHandler.END
    
    gstin = text
    if len(gstin) != 15:
        await update.message.reply_text("Invalid GSTIN! Must be 15 characters.", reply_markup=get_cancel_keyboard())
        return ASKING_GST_BILLING
    
    if context.user_data.get("use_coin", False):
        if not use_coin(user_id):
            await update.message.reply_text("Not enough coins!", reply_markup=get_main_keyboard(user_id))
            return ConversationHandler.END
    
    await update.message.chat.send_action(action="typing")
    status_msg = await update.message.reply_text("Fetching GST Billing...")
    
    result = await search_gst_billing(gstin)
    await status_msg.delete()
    
    if "error" not in result:
        update_user_stats(user_id)
        save_search_result(user_id, "gst_billing", gstin, result)
    
    formatted = format_raw_result(result, gstin, "GST Billing")
    await update.message.reply_text(formatted)
    await update.message.reply_text("Search Complete", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

async def handle_pan_gst(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip().upper()
    if text == "Cancel" or text == "Back":
        await update.message.reply_text("Cancelled", reply_markup=get_main_keyboard(user_id))
        return ConversationHandler.END
    
    pan = text
    if len(pan) != 10:
        await update.message.reply_text("Invalid PAN! Must be 10 characters.", reply_markup=get_cancel_keyboard())
        return ASKING_PAN_GST
    
    if context.user_data.get("use_coin", False):
        if not use_coin(user_id):
            await update.message.reply_text("Not enough coins!", reply_markup=get_main_keyboard(user_id))
            return ConversationHandler.END
    
    await update.message.chat.send_action(action="typing")
    status_msg = await update.message.reply_text("Searching PAN to GST...")
    
    result = await search_pan_gst(pan)
    await status_msg.delete()
    
    if "error" not in result:
        update_user_stats(user_id)
        save_search_result(user_id, "pan_gst", pan, result)
    
    formatted = format_raw_result(result, pan, "PAN to GST")
    await update.message.reply_text(formatted)
    await update.message.reply_text("Search Complete", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

async def handle_aadhar_family(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "Cancel" or text == "Back":
        await update.message.reply_text("Cancelled", reply_markup=get_main_keyboard(user_id))
        return ConversationHandler.END
    
    aadhar = ''.join(filter(str.isdigit, text))
    if len(aadhar) != 12:
        await update.message.reply_text("Invalid Aadhar! Must be 12 digits.", reply_markup=get_cancel_keyboard())
        return ASKING_AADHAR_FAMILY
    
    if context.user_data.get("use_coin", False):
        if not use_coin(user_id):
            await update.message.reply_text("Not enough coins!", reply_markup=get_main_keyboard(user_id))
            return ConversationHandler.END
    
    await update.message.chat.send_action(action="typing")
    status_msg = await update.message.reply_text("Searching Family Details...")
    
    result = await search_aadhar_family(aadhar)
    await status_msg.delete()
    
    if "error" not in result:
        update_user_stats(user_id)
        save_search_result(user_id, "aadhar_family", aadhar, result)
    
    formatted = format_raw_result(result, aadhar, "Aadhar Family")
    await update.message.reply_text(formatted)
    await update.message.reply_text("Search Complete", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END