from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import MAINTENANCE_MODE, MAINTENANCE_MESSAGE, SUPPORT_USERNAME, DEVELOPER_USERNAME
from utils import is_admin

async def check_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if bot is in maintenance mode"""
    if MAINTENANCE_MODE:
        user_id = update.effective_user.id
        # Admins can bypass maintenance mode
        if is_admin(user_id):
            return False
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Contact Developer", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("Support Group", url=f"https://t.me/{DEVELOPER_USERNAME}")]
        ])
        
        await update.message.reply_text(
            f"{MAINTENANCE_MESSAGE}\n\nDeveloper: @{DEVELOPER_USERNAME}",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return True
    return False

def toggle_maintenance_mode() -> bool:
    """Toggle maintenance mode"""
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE
    return MAINTENANCE_MODE

def set_maintenance_mode(status: bool, message: str = None) -> bool:
    """Set maintenance mode with custom message"""
    global MAINTENANCE_MODE, MAINTENANCE_MESSAGE
    MAINTENANCE_MODE = status
    if message:
        MAINTENANCE_MESSAGE = message
    return MAINTENANCE_MODE

def is_maintenance_mode() -> bool:
    """Check if maintenance mode is active"""
    return MAINTENANCE_MODE
