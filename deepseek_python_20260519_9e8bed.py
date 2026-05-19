import random
import string
from datetime import datetime, date, timedelta
from typing import Dict, Any, Tuple, Optional, List
import psutil
import platform
import time
from config import *
from database import mongo

# Global settings (will be loaded from DB)
settings = {}
api_settings = {}

def load_settings():
    """Load settings from MongoDB"""
    global settings, api_settings
    
    settings = {
        "bot_active": mongo.get_setting("bot_active", True),
        "referral_coins": mongo.get_setting("referral_coins", DEFAULT_REFERRAL_COINS),
        "daily_limit": mongo.get_setting("daily_limit", DAILY_FREE_LIMIT)
    }
    
    api_settings = {"apis": {}}
    for key in DEFAULT_APIS.keys():
        api_data = mongo.get_api_setting(key)
        if api_data:
            api_settings["apis"][key] = api_data
        else:
            api_settings["apis"][key] = {"enabled": True, "url": DEFAULT_APIS[key]}
            mongo.save_api_setting(key, api_settings["apis"][key])

def save_all():
    """Save all settings to MongoDB"""
    mongo.save_setting("bot_active", settings["bot_active"])
    mongo.save_setting("referral_coins", settings["referral_coins"])
    mongo.save_setting("daily_limit", settings["daily_limit"])
    
    for service, data in api_settings.get("apis", {}).items():
        mongo.save_api_setting(service, data)

def get_user(user_id: int) -> dict:
    """Get or create user"""
    user = mongo.get_user(user_id)
    if not user:
        user = {
            "user_id": user_id,
            "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": None,
            "coins": 0,
            "total_searches": 0,
            "daily_searches": 0,
            "last_search_date": date.today().isoformat(),
            "referral_code": f"{user_id}_{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}",
            "referred_by": None,
            "referrals": [],
            "is_admin": False,
            "redeemed_keys": [],
            "is_blocked": False,
            "blocked_reason": None,
            "blocked_at": None
        }
        mongo.save_user(user)
        mongo.save_log("new_user", {"user_id": user_id, "username": user.get("username")})
    return user

def update_user_stats(user_id: int):
    """Update user search statistics"""
    user = get_user(user_id)
    today = date.today().isoformat()
    if user["last_search_date"] != today:
        user["daily_searches"] = 0
        user["last_search_date"] = today
    user["daily_searches"] += 1
    user["total_searches"] += 1
    user["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mongo.save_user(user)

def add_coins(user_id: int, amount: int):
    """Add coins to user"""
    user = get_user(user_id)
    user["coins"] += amount
    mongo.save_user(user)

def use_coin(user_id: int) -> bool:
    """Use a coin for search"""
    if has_unlimited_coins(user_id):
        return True
    user = get_user(user_id)
    if user["coins"] > 0:
        user["coins"] -= 1
        mongo.save_user(user)
        return True
    return False

def is_user_blocked(user_id: int) -> Tuple[bool, str]:
    """Check if user is blocked"""
    user = get_user(user_id)
    if user.get("is_blocked", False):
        return True, user.get("blocked_reason", "No reason provided")
    return False, ""

def block_user(user_id: int, reason: str = "Blocked by admin", blocked_by: int = None) -> bool:
    """Block a user"""
    user = get_user(user_id)
    user["is_blocked"] = True
    user["blocked_reason"] = reason
    user["blocked_at"] = datetime.now().isoformat()
    user["blocked_by"] = blocked_by
    mongo.save_user(user)
    mongo.save_log("user_blocked", {"user_id": user_id, "reason": reason, "blocked_by": blocked_by})
    return True

def unblock_user(user_id: int) -> bool:
    """Unblock a user"""
    user = get_user(user_id)
    user["is_blocked"] = False
    user["blocked_reason"] = None
    user["blocked_at"] = None
    user["blocked_by"] = None
    mongo.save_user(user)
    mongo.save_log("user_unblocked", {"user_id": user_id})
    return True

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    if user_id in OWNER_IDS:
        return True
    user = get_user(user_id)
    return user.get("is_admin", False)

def is_owner(user_id: int) -> bool:
    """Check if user is owner"""
    return user_id in OWNER_IDS

def has_unlimited_coins(user_id: int) -> bool:
    """Check if user has unlimited coins"""
    return is_admin(user_id)

def can_search(user_id: int) -> Tuple[bool, int, bool]:
    """Check if user can perform a search"""
    blocked, reason = is_user_blocked(user_id)
    if blocked:
        return False, 0, False
    
    if has_unlimited_coins(user_id):
        return True, 999999, False
    
    user = get_user(user_id)
    today = date.today().isoformat()
    if user["last_search_date"] != today:
        user["daily_searches"] = 0
        user["last_search_date"] = today
        mongo.save_user(user)
    
    remaining = settings["daily_limit"] - user["daily_searches"]
    if remaining > 0:
        return True, remaining, False
    elif user["coins"] > 0:
        return True, 0, True
    else:
        return False, 0, False

def get_api_url(service: str) -> str:
    """Get API URL from settings"""
    return api_settings.get("apis", {}).get(service, {}).get("url", DEFAULT_APIS.get(service, ""))

def is_api_enabled(service: str) -> bool:
    """Check if API is enabled"""
    return api_settings.get("apis", {}).get(service, {}).get("enabled", True)

def update_api_url(service: str, new_url: str) -> bool:
    """Update API URL"""
    try:
        if service not in api_settings.get("apis", {}):
            api_settings["apis"][service] = {"enabled": True, "url": DEFAULT_APIS.get(service, "")}
        api_settings["apis"][service]["url"] = new_url
        mongo.save_api_setting(service, api_settings["apis"][service])
        return True
    except Exception as e:
        return False

def toggle_api(service: str) -> bool:
    """Toggle API enabled status"""
    try:
        current = api_settings["apis"][service]["enabled"]
        api_settings["apis"][service]["enabled"] = not current
        mongo.save_api_setting(service, api_settings["apis"][service])
        return not current
    except Exception as e:
        return False

def generate_keys(key_type: str, count: int, credits: int) -> list:
    """Generate multiple keys"""
    keys = []
    for _ in range(count):
        key_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        full_key = f"{key_type}_{key_id}" if key_type != "normal" else key_id
        key_data = {
            "key": full_key,
            "key_type": key_type,
            "credits": credits,
            "used_by": None,
            "used_at": None,
            "created_at": datetime.now().isoformat(),
            "is_used": False
        }
        mongo.save_key(full_key, key_data)
        keys.append(full_key)
    return keys

def redeem_key(user_id: int, key: str) -> Tuple[bool, str]:
    """Redeem a key"""
    key_data = mongo.get_key(key)
    
    if not key_data:
        return False, "Invalid key! Key not found."
    
    if key_data.get("is_used", False):
        used_by = key_data.get("used_by")
        return False, f"Key already used! Used by user ID: {used_by}"
    
    key_data["is_used"] = True
    key_data["used_by"] = user_id
    key_data["used_at"] = datetime.now().isoformat()
    mongo.save_key(key, key_data)
    
    credits = key_data.get("credits", 0)
    add_coins(user_id, credits)
    
    user = get_user(user_id)
    if "redeemed_keys" not in user:
        user["redeemed_keys"] = []
    user["redeemed_keys"].append({
        "key": key,
        "credits": credits,
        "redeemed_at": datetime.now().isoformat()
    })
    mongo.save_user(user)
    
    return True, f"Key redeemed successfully! You received {credits} coins!"

def revoke_key(key: str) -> Tuple[bool, str]:
    """Revoke/delete an unused key"""
    key_data = mongo.get_key(key)
    
    if not key_data:
        return False, "Key not found!"
    
    if key_data.get("is_used", False):
        return False, "Cannot revoke a used key!"
    
    if mongo.delete_key(key):
        return True, f"Key revoked successfully: {key}"
    return False, "Failed to revoke key!"

def revoke_all_unused_keys(key_type: str = None) -> Tuple[bool, str]:
    """Revoke all unused keys"""
    count = mongo.delete_unused_keys(key_type)
    if count > 0:
        type_msg = f" of type '{key_type}'" if key_type and key_type != "all" else ""
        return True, f"Revoked {count} unused keys{type_msg}!"
    return False, "No unused keys found to revoke!"

def process_referral(new_user_id: int, ref_code: str) -> bool:
    """Process referral"""
    all_users = mongo.get_all_users()
    referrer_id = None
    
    for user in all_users:
        if user.get("referral_code") == ref_code:
            referrer_id = user["user_id"]
            break
    
    if referrer_id and referrer_id != new_user_id:
        user = get_user(new_user_id)
        user["referred_by"] = referrer_id
        mongo.save_user(user)
        add_coins(referrer_id, settings["referral_coins"])
        referrer = get_user(referrer_id)
        if str(new_user_id) not in referrer.get("referrals", []):
            referrer.setdefault("referrals", []).append(str(new_user_id))
            mongo.save_user(referrer)
        return True
    return False

def find_user_by_identifier(identifier: str) -> Optional[int]:
    """Find user by ID or username"""
    if identifier.isdigit():
        user = mongo.get_user(int(identifier))
        if user:
            return int(identifier)
        return None
    
    username = identifier.lstrip('@').lower()
    all_users = mongo.get_all_users()
    for user in all_users:
        if user.get("username", "").lower() == username:
            return user["user_id"]
    return None

def get_bot_uptime() -> str:
    """Get bot uptime"""
    uptime_seconds = int(time.time() - BOT_START_TIME)
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)

def get_system_info() -> dict:
    """Get system information"""
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used": psutil.virtual_memory().used // (1024**2),
            "memory_total": psutil.virtual_memory().total // (1024**2),
            "disk_percent": psutil.disk_usage('/').percent,
            "disk_used": psutil.disk_usage('/').used // (1024**2),
            "disk_total": psutil.disk_usage('/').total // (1024**2),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "python_version": platform.python_version()
        }
    except:
        return {
            "cpu_percent": 0,
            "memory_percent": 0,
            "memory_used": 0,
            "memory_total": 0,
            "disk_percent": 0,
            "disk_used": 0,
            "disk_total": 0,
            "platform": "Unknown",
            "platform_release": "Unknown",
            "python_version": "Unknown"
        }