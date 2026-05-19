import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, ConversationHandler, CallbackQueryHandler
)
from config import BOT_TOKEN, ASKING_NUMBER, ASKING_AADHAR, ASKING_PAK_NUM, ASKING_PAK_CNIC
from config import ASKING_PAK_POLICE, ASKING_GST_BILLING, ASKING_PAN_GST, ASKING_AADHAR_FAMILY
from config import ASKING_BROADCAST, ASKING_BLOCK_NUMBER, ASKING_UNBLOCK_NUMBER, ASKING_REFERRAL_AMOUNT
from config import ASKING_ADD_ADMIN, ASKING_REMOVE_ADMIN, ASKING_ADD_COINS_USER, ASKING_ADD_COINS_AMOUNT
from config import ASKING_API_UPDATE, ASKING_API_SELECT, ASKING_SET_DAILY_LIMIT, ASKING_REDEEM_KEY
from config import ASKING_REVOKE_KEY, ASKING_REVOKE_KEY_ID, ASKING_BLOCK_USER

from database import mongo
from utils import load_settings
from maintenance import check_maintenance
from keyboards import get_main_keyboard, get_admin_keyboard
from user_handlers import *
from search_handlers import *
from admin_handlers import *
from key_handlers import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== CANCEL & BACK HANDLERS ====================
async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    context.user_data.clear()
    user_id = update.effective_user.id
    await update.message.reply_text("Cancelled", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

async def back_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_maintenance(update, context):
        return ConversationHandler.END
    user_id = update.effective_user.id
    if is_admin(user_id):
        await update.message.reply_text("Back to Admin Panel", reply_markup=get_admin_keyboard())
    else:
        await update.message.reply_text("Back to Main Menu", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END

# ==================== CALLBACK HANDLER ====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "close":
        await query.delete_message()
    elif query.data.startswith("buy_"):
        coins = query.data.split("_")[1]
        prices = {"50": 30, "100": 50, "250": 120, "500": 200}
        text = f"Purchase {coins} Coins\nAmount: Rs{prices.get(coins, 0)}\nUPI: {UPI_ID}\nContact: @{SUPPORT_USERNAME}"
        await query.edit_message_text(text)

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("An error occurred. Please try again later.")
    except:
        pass

# ==================== MAIN ====================
def main():
    load_settings()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Search conversation handlers
    search_handlers = [
        (MessageHandler(filters.Regex("^Indian Number$"), indian_number_button), ASKING_NUMBER, handle_indian_number),
        (MessageHandler(filters.Regex("^Indian Aadhar$"), indian_aadhar_button), ASKING_AADHAR, handle_indian_aadhar),
        (MessageHandler(filters.Regex("^Pak Number$"), pak_number_button), ASKING_PAK_NUM, handle_pak_number),
        (MessageHandler(filters.Regex("^Pak CNIC$"), pak_cnic_button), ASKING_PAK_CNIC, handle_pak_cnic),
        (MessageHandler(filters.Regex("^Pak Police$"), pak_police_button), ASKING_PAK_POLICE, handle_pak_police),
        (MessageHandler(filters.Regex("^GST Billing$"), gst_billing_button), ASKING_GST_BILLING, handle_gst_billing),
        (MessageHandler(filters.Regex("^PAN to GST$"), pan_gst_button), ASKING_PAN_GST, handle_pan_gst),
        (MessageHandler(filters.Regex("^Aadhar Family$"), aadhar_family_button), ASKING_AADHAR_FAMILY, handle_aadhar_family),
    ]
    
    for entry_handler, state, handler in search_handlers:
        app.add_handler(ConversationHandler(
            entry_points=[entry_handler],
            states={state: [MessageHandler(filters.TEXT & ~filters.COMMAND, handler)]},
            fallbacks=[
                MessageHandler(filters.Regex("^Cancel$"), cancel_operation),
                MessageHandler(filters.Regex("^Back$"), back_operation)
            ]
        ))
    
    # Redeem Key conversation
    app.add_handler(ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Redeem Key$"), redeem_key_command),
            CommandHandler("redeem", redeem_key_command)
        ],
        states={ASKING_REDEEM_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_redeem_key)]},
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel_operation)]
    ))
    
    # Revoke Single Key conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Revoke Single Key$"), revoke_single_key_start)],
        states={ASKING_REVOKE_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, revoke_single_key_input)]},
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel_operation)]
    ))
    
    # Revoke By Type conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Revoke By Type$"), revoke_by_type_start)],
        states={ASKING_REVOKE_KEY_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, revoke_by_type_input)]},
        fallbacks=[MessageHandler(filters.Regex("^Back$"), back_operation)]
    ))
    
    # Block User conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Block User$"), block_user_start)],
        states={ASKING_BLOCK_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, block_user_input)]},
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel_operation)]
    ))
    
    # Unblock User conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Unblock User$"), unblock_user_start)],
        states={ASKING_UNBLOCK_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, unblock_user_input)]},
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel_operation)]
    ))
    
    # API Update conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Update API URL$"), update_api_select)],
        states={
            ASKING_API_SELECT: [
                MessageHandler(filters.Regex("^Update "), update_api_url_start),
                MessageHandler(filters.Regex("^Back$"), back_to_admin)
            ],
            ASKING_API_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_api_url_input)],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^Cancel$"), cancel_operation),
            MessageHandler(filters.Regex("^Back$"), back_to_admin)
        ]
    ))
    
    # Broadcast conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Broadcast$"), broadcast_start)],
        states={ASKING_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_send)]},
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel_operation)]
    ))
    
    # Block Number conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Block Number$"), block_number_start)],
        states={ASKING_BLOCK_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, block_number_input)]},
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel_operation)]
    ))
    
    # Unblock Number conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Unblock Number$"), unblock_number_start)],
        states={ASKING_UNBLOCK_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, unblock_number_input)]},
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel_operation)]
    ))
    
    # Set Referral Coins conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Set Referral Coins$"), set_referral_coins_start)],
        states={ASKING_REFERRAL_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_referral_coins_input)]},
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel_operation)]
    ))
    
    # Add Admin conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Add Admin$"), add_admin_start)],
        states={ASKING_ADD_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_admin_input)]},
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel_operation)]
    ))
    
    # Remove Admin conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Remove Admin$"), remove_admin_start)],
        states={ASKING_REMOVE_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_admin_input)]},
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel_operation)]
    ))
    
    # Add Coins conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Add Coins$"), add_coins_start)],
        states={
            ASKING_ADD_COINS_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_coins_user_input)],
            ASKING_ADD_COINS_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_coins_amount_input)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel_operation)]
    ))
    
    # Set Daily Limit conversation
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Set Daily Limit$"), set_daily_limit_start)],
        states={ASKING_SET_DAILY_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_daily_limit_input)]},
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel_operation)]
    ))
    
    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", my_stats))
    app.add_handler(CommandHandler("coins", my_coins))
    app.add_handler(CommandHandler("referral", referral_link_command))
    app.add_handler(CommandHandler("buy", buy_coins))
    app.add_handler(CommandHandler("num", num_command))
    app.add_handler(CommandHandler("aadhar", aadhar_command))
    app.add_handler(CommandHandler("gen", generate_keys_command))
    app.add_handler(CommandHandler("key_stats", key_stats_command))
    app.add_handler(CommandHandler("system", system_info_command))
    app.add_handler(CommandHandler("history", search_history_command))
    app.add_handler(CommandHandler("revoke", revoke_all_unused))
    
    # Admin panel entries
    app.add_handler(MessageHandler(filters.Regex("^Admin Panel$"), admin_panel))
    app.add_handler(MessageHandler(filters.Regex("^API Settings$"), api_settings_menu))
    app.add_handler(MessageHandler(filters.Regex("^API Status$"), api_status))
    app.add_handler(MessageHandler(filters.Regex("^Bot Status$"), bot_status))
    app.add_handler(MessageHandler(filters.Regex("^All Users$"), all_users))
    app.add_handler(MessageHandler(filters.Regex("^Blocked List$"), blocked_list))
    app.add_handler(MessageHandler(filters.Regex("^Admin List$"), admin_list))
    app.add_handler(MessageHandler(filters.Regex("^Toggle Bot$"), toggle_bot))
    app.add_handler(MessageHandler(filters.Regex("^Maintenance Mode$"), maintenance_mode_command))
    app.add_handler(MessageHandler(filters.Regex("^Generate Keys$"), lambda u,c: u.message.reply_text("Use /gen count credits or /gen type count credits\nExample: /gen 20 10")))
    app.add_handler(MessageHandler(filters.Regex("^Key Stats$"), key_stats_command))
    app.add_handler(MessageHandler(filters.Regex("^Revoke Keys$"), revoke_keys_menu))
    app.add_handler(MessageHandler(filters.Regex("^Revoke All Unused$"), revoke_all_unused))
    app.add_handler(MessageHandler(filters.Regex("^Unused Keys$"), show_unused_keys))
    app.add_handler(MessageHandler(filters.Regex("^Blocked Users$"), show_blocked_users))
    app.add_handler(MessageHandler(filters.Regex("^Exit Admin$"), exit_admin))
    app.add_handler(MessageHandler(filters.Regex("^Back to Admin$"), back_to_admin))
    
    # User menu handlers
    app.add_handler(MessageHandler(filters.Regex("^My Coins$"), my_coins))
    app.add_handler(MessageHandler(filters.Regex("^Referral$"), referral_link_command))
    app.add_handler(MessageHandler(filters.Regex("^Stats$"), my_stats))
    app.add_handler(MessageHandler(filters.Regex("^System Info$"), system_info_command))
    app.add_handler(MessageHandler(filters.Regex("^Help$"), help_command))
    
    # API Toggle handler
    app.add_handler(MessageHandler(
        filters.Regex(r"^(ON|OFF) (Indian Number|Indian Aadhar|Pakistan Number|Pakistan CNIC|Pakistan Police|GST Billing|PAN to GST|Aadhar Family)$"),
        toggle_api_handler
    ))
    
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_error_handler(error_handler)
    
    logger.info("Bot started with all features!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()