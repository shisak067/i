from telegram import ReplyKeyboardMarkup, KeyboardButton
from config import API_SERVICES
from utils import is_admin, is_api_enabled

def get_main_keyboard(user_id: int = None) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("Indian Number"), KeyboardButton("Indian Aadhar")],
        [KeyboardButton("Pak Number"), KeyboardButton("Pak CNIC")],
        [KeyboardButton("Pak Police"), KeyboardButton("Aadhar Family")],
        [KeyboardButton("GST Billing"), KeyboardButton("PAN to GST")],
        [KeyboardButton("My Coins"), KeyboardButton("Referral")],
        [KeyboardButton("Redeem Key"), KeyboardButton("Stats")],
        [KeyboardButton("System Info"), KeyboardButton("Help")]
    ]
    if user_id and is_admin(user_id):
        keyboard.append([KeyboardButton("Admin Panel")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("Bot Status"), KeyboardButton("All Users")],
        [KeyboardButton("Toggle Bot"), KeyboardButton("Maintenance Mode")],
        [KeyboardButton("Broadcast"), KeyboardButton("Block Number")],
        [KeyboardButton("Unblock Number"), KeyboardButton("Block User")],
        [KeyboardButton("Unblock User"), KeyboardButton("Add Admin")],
        [KeyboardButton("Remove Admin"), KeyboardButton("Admin List")],
        [KeyboardButton("Set Referral Coins"), KeyboardButton("Add Coins")],
        [KeyboardButton("Blocked List"), KeyboardButton("API Settings")],
        [KeyboardButton("Set Daily Limit"), KeyboardButton("Generate Keys")],
        [KeyboardButton("Key Stats"), KeyboardButton("Revoke Keys")],
        [KeyboardButton("Unused Keys"), KeyboardButton("Exit Admin")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_revoke_keys_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("Revoke Single Key")],
        [KeyboardButton("Revoke All Unused")],
        [KeyboardButton("Revoke By Type")],
        [KeyboardButton("Back to Admin")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_api_settings_keyboard() -> ReplyKeyboardMarkup:
    keyboard = []
    row = []
    for key, service in API_SERVICES.items():
        status = "ON" if is_api_enabled(key) else "OFF"
        button_text = f"{status} {service['name']}"
        row.append(KeyboardButton(button_text))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([KeyboardButton("Update API URL"), KeyboardButton("API Status")])
    keyboard.append([KeyboardButton("Back to Admin")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_api_select_keyboard() -> ReplyKeyboardMarkup:
    keyboard = []
    for key, service in API_SERVICES.items():
        keyboard.append([KeyboardButton(f"Update {service['name']}")])
    keyboard.append([KeyboardButton("Back")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[KeyboardButton("Cancel")]], resize_keyboard=True)

def get_back_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[KeyboardButton("Back")]], resize_keyboard=True)
