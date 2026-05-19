import json
import logging
import os
from datetime import datetime, date
from typing import Dict, Any, Tuple, Optional, List
from pymongo import MongoClient

logger = logging.getLogger(__name__)

DATA_DIR = "bot_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class MongoDBManager:
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.is_connected = False
        self.connect()
    
    def connect(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.is_connected = True
            logger.info("MongoDB connected successfully")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            self.is_connected = False
            return False
    
    def is_available(self) -> bool:
        if not self.is_connected:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except:
            self.is_connected = False
            return False
    
    def get_collection(self, name: str):
        if self.is_available() and self.db is not None:
            return self.db[name]
        return None
    
    def save_user(self, user_data: dict):
        collection = self.get_collection("users")
        if collection is not None:
            try:
                collection.update_one(
                    {"user_id": user_data["user_id"]},
                    {"$set": user_data},
                    upsert=True
                )
                return True
            except Exception as e:
                logger.error(f"Error saving user: {e}")
        return self._save_user_file(user_data)
    
    def _save_user_file(self, user_data: dict):
        users_file = f"{DATA_DIR}/users.json"
        try:
            users = {}
            if os.path.exists(users_file):
                with open(users_file, 'r') as f:
                    users = json.load(f)
            users[str(user_data["user_id"])] = user_data
            with open(users_file, 'w') as f:
                json.dump(users, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving user to file: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[dict]:
        collection = self.get_collection("users")
        if collection is not None:
            try:
                user = collection.find_one({"user_id": user_id})
                if user:
                    user.pop("_id", None)
                    return user
            except Exception as e:
                logger.error(f"Error getting user: {e}")
        return self._get_user_file(user_id)
    
    def _get_user_file(self, user_id: int) -> Optional[dict]:
        users_file = f"{DATA_DIR}/users.json"
        try:
            if os.path.exists(users_file):
                with open(users_file, 'r') as f:
                    users = json.load(f)
                return users.get(str(user_id))
        except Exception as e:
            logger.error(f"Error getting user from file: {e}")
        return None
    
    def get_all_users(self) -> List[dict]:
        collection = self.get_collection("users")
        if collection is not None:
            try:
                users = list(collection.find({}))
                for user in users:
                    user.pop("_id", None)
                return users
            except Exception as e:
                logger.error(f"Error getting users: {e}")
        return self._get_all_users_file()
    
    def _get_all_users_file(self) -> List[dict]:
        users_file = f"{DATA_DIR}/users.json"
        try:
            if os.path.exists(users_file):
                with open(users_file, 'r') as f:
                    users_dict = json.load(f)
                return list(users_dict.values())
        except Exception as e:
            logger.error(f"Error getting users from file: {e}")
        return []
    
    def save_setting(self, key: str, value: any):
        collection = self.get_collection("settings")
        if collection is not None:
            try:
                collection.update_one(
                    {"key": key},
                    {"$set": {"value": value, "updated_at": datetime.now()}},
                    upsert=True
                )
                return True
            except Exception as e:
                logger.error(f"Error saving setting: {e}")
        return self._save_setting_file(key, value)
    
    def _save_setting_file(self, key: str, value: any):
        settings_file = f"{DATA_DIR}/settings.json"
        try:
            settings = {}
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            settings[key] = value
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving setting to file: {e}")
            return False
    
    def get_setting(self, key: str, default: any = None) -> any:
        collection = self.get_collection("settings")
        if collection is not None:
            try:
                setting = collection.find_one({"key": key})
                if setting:
                    return setting.get("value", default)
            except Exception as e:
                logger.error(f"Error getting setting: {e}")
        return self._get_setting_file(key, default)
    
    def _get_setting_file(self, key: str, default: any = None) -> any:
        settings_file = f"{DATA_DIR}/settings.json"
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                return settings.get(key, default)
        except Exception as e:
            logger.error(f"Error getting setting from file: {e}")
        return default
    
    def save_api_setting(self, service: str, data: dict):
        collection = self.get_collection("api_settings")
        if collection is not None:
            try:
                collection.update_one(
                    {"service": service},
                    {"$set": data},
                    upsert=True
                )
                return True
            except Exception as e:
                logger.error(f"Error saving API setting: {e}")
        return self._save_api_setting_file(service, data)
    
    def _save_api_setting_file(self, service: str, data: dict):
        api_file = f"{DATA_DIR}/api_settings.json"
        try:
            api_settings = {}
            if os.path.exists(api_file):
                with open(api_file, 'r') as f:
                    api_settings = json.load(f)
            api_settings[service] = data
            with open(api_file, 'w') as f:
                json.dump(api_settings, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving API setting to file: {e}")
            return False
    
    def get_api_setting(self, service: str) -> Optional[dict]:
        collection = self.get_collection("api_settings")
        if collection is not None:
            try:
                setting = collection.find_one({"service": service})
                if setting:
                    setting.pop("_id", None)
                    return setting
            except Exception as e:
                logger.error(f"Error getting API setting: {e}")
        return self._get_api_setting_file(service)
    
    def _get_api_setting_file(self, service: str) -> Optional[dict]:
        api_file = f"{DATA_DIR}/api_settings.json"
        try:
            if os.path.exists(api_file):
                with open(api_file, 'r') as f:
                    api_settings = json.load(f)
                return api_settings.get(service)
        except Exception as e:
            logger.error(f"Error getting API setting from file: {e}")
        return None
    
    def save_key(self, key: str, data: dict):
        collection = self.get_collection("generated_keys")
        if collection is not None:
            try:
                collection.update_one(
                    {"key": key},
                    {"$set": data},
                    upsert=True
                )
                return True
            except Exception as e:
                logger.error(f"Error saving key: {e}")
        return self._save_key_file(key, data)
    
    def _save_key_file(self, key: str, data: dict):
        keys_file = f"{DATA_DIR}/generated_keys.json"
        try:
            keys = {}
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    keys = json.load(f)
            keys[key] = data
            with open(keys_file, 'w') as f:
                json.dump(keys, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving key to file: {e}")
            return False
    
    def get_key(self, key: str) -> Optional[dict]:
        collection = self.get_collection("generated_keys")
        if collection is not None:
            try:
                key_data = collection.find_one({"key": key})
                if key_data:
                    key_data.pop("_id", None)
                    return key_data
            except Exception as e:
                logger.error(f"Error getting key: {e}")
        return self._get_key_file(key)
    
    def _get_key_file(self, key: str) -> Optional[dict]:
        keys_file = f"{DATA_DIR}/generated_keys.json"
        try:
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    keys = json.load(f)
                return keys.get(key)
        except Exception as e:
            logger.error(f"Error getting key from file: {e}")
        return None
    
    def get_all_keys(self) -> List[dict]:
        collection = self.get_collection("generated_keys")
        if collection is not None:
            try:
                keys = list(collection.find({}))
                for key in keys:
                    key.pop("_id", None)
                return keys
            except Exception as e:
                logger.error(f"Error getting keys: {e}")
        return self._get_all_keys_file()
    
    def _get_all_keys_file(self) -> List[dict]:
        keys_file = f"{DATA_DIR}/generated_keys.json"
        try:
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    keys_dict = json.load(f)
                return list(keys_dict.values())
        except Exception as e:
            logger.error(f"Error getting keys from file: {e}")
        return []
    
    def delete_key(self, key: str) -> bool:
        collection = self.get_collection("generated_keys")
        if collection is not None:
            try:
                result = collection.delete_one({"key": key})
                return result.deleted_count > 0
            except Exception as e:
                logger.error(f"Error deleting key: {e}")
        return self._delete_key_file(key)
    
    def _delete_key_file(self, key: str) -> bool:
        keys_file = f"{DATA_DIR}/generated_keys.json"
        try:
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    keys = json.load(f)
                if key in keys:
                    del keys[key]
                    with open(keys_file, 'w') as f:
                        json.dump(keys, f, indent=2)
                    return True
        except Exception as e:
            logger.error(f"Error deleting key from file: {e}")
        return False
    
    def delete_unused_keys(self, key_type: str = None) -> int:
        collection = self.get_collection("generated_keys")
        if collection is not None:
            try:
                query = {"is_used": False}
                if key_type and key_type != "all":
                    query["key_type"] = key_type
                result = collection.delete_many(query)
                return result.deleted_count
            except Exception as e:
                logger.error(f"Error deleting unused keys: {e}")
        return self._delete_unused_keys_file(key_type)
    
    def _delete_unused_keys_file(self, key_type: str = None) -> int:
        keys_file = f"{DATA_DIR}/generated_keys.json"
        try:
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    keys = json.load(f)
                to_delete = []
                for k, data in keys.items():
                    if not data.get("is_used", False):
                        if not key_type or key_type == "all" or data.get("key_type") == key_type:
                            to_delete.append(k)
                for k in to_delete:
                    del keys[k]
                with open(keys_file, 'w') as f:
                    json.dump(keys, f, indent=2)
                return len(to_delete)
        except Exception as e:
            logger.error(f"Error deleting unused keys from file: {e}")
        return 0
    
    def save_search_result(self, user_id: int, search_type: str, query: str, result: dict):
        collection = self.get_collection("search_history")
        if collection is not None:
            try:
                if "DEVELOPER" in result:
                    del result["DEVELOPER"]
                if "developer" in result:
                    del result["developer"]
                collection.insert_one({
                    "user_id": user_id,
                    "search_type": search_type,
                    "query": query,
                    "result": result,
                    "timestamp": datetime.now()
                })
                return True
            except Exception as e:
                logger.error(f"Error saving search result: {e}")
        return False
    
    def get_search_history(self, user_id: int, limit: int = 50) -> List[dict]:
        collection = self.get_collection("search_history")
        if collection is not None:
            try:
                history = list(collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit))
                for h in history:
                    h.pop("_id", None)
                return history
            except Exception as e:
                logger.error(f"Error getting search history: {e}")
        return []
    
    def save_blocked_number(self, number: str, data: dict):
        collection = self.get_collection("blocked_numbers")
        if collection is not None:
            try:
                collection.update_one(
                    {"number": number},
                    {"$set": data},
                    upsert=True
                )
                return True
            except Exception as e:
                logger.error(f"Error saving blocked number: {e}")
        return self._save_blocked_number_file(number, data)
    
    def _save_blocked_number_file(self, number: str, data: dict):
        blocked_file = f"{DATA_DIR}/blocked.json"
        try:
            blocked = {}
            if os.path.exists(blocked_file):
                with open(blocked_file, 'r') as f:
                    blocked = json.load(f)
            blocked[number] = data
            with open(blocked_file, 'w') as f:
                json.dump(blocked, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving blocked number to file: {e}")
            return False
    
    def get_blocked_number(self, number: str) -> Optional[dict]:
        collection = self.get_collection("blocked_numbers")
        if collection is not None:
            try:
                return collection.find_one({"number": number})
            except Exception as e:
                logger.error(f"Error getting blocked number: {e}")
        return self._get_blocked_number_file(number)
    
    def _get_blocked_number_file(self, number: str) -> Optional[dict]:
        blocked_file = f"{DATA_DIR}/blocked.json"
        try:
            if os.path.exists(blocked_file):
                with open(blocked_file, 'r') as f:
                    blocked = json.load(f)
                return blocked.get(number)
        except Exception as e:
            logger.error(f"Error getting blocked number from file: {e}")
        return None
    
    def get_all_blocked_numbers(self) -> List[dict]:
        collection = self.get_collection("blocked_numbers")
        if collection is not None:
            try:
                return list(collection.find({}))
            except Exception as e:
                logger.error(f"Error getting blocked numbers: {e}")
        return self._get_all_blocked_numbers_file()
    
    def _get_all_blocked_numbers_file(self) -> List[dict]:
        blocked_file = f"{DATA_DIR}/blocked.json"
        try:
            if os.path.exists(blocked_file):
                with open(blocked_file, 'r') as f:
                    blocked_dict = json.load(f)
                return [{"number": k, **v} for k, v in blocked_dict.items()]
        except Exception as e:
            logger.error(f"Error getting blocked numbers from file: {e}")
        return []
    
    def remove_blocked_number(self, number: str) -> bool:
        collection = self.get_collection("blocked_numbers")
        if collection is not None:
            try:
                result = collection.delete_one({"number": number})
                return result.deleted_count > 0
            except Exception as e:
                logger.error(f"Error removing blocked number: {e}")
        return self._remove_blocked_number_file(number)
    
    def _remove_blocked_number_file(self, number: str) -> bool:
        blocked_file = f"{DATA_DIR}/blocked.json"
        try:
            if os.path.exists(blocked_file):
                with open(blocked_file, 'r') as f:
                    blocked = json.load(f)
                if number in blocked:
                    del blocked[number]
                    with open(blocked_file, 'w') as f:
                        json.dump(blocked, f, indent=2)
                    return True
        except Exception as e:
            logger.error(f"Error removing blocked number from file: {e}")
        return False
    
    def save_log(self, log_type: str, data: dict):
        collection = self.get_collection("logs")
        if collection is not None:
            try:
                collection.insert_one({
                    "type": log_type,
                    "data": data,
                    "timestamp": datetime.now()
                })
                return True
            except Exception as e:
                logger.error(f"Error saving log: {e}")
        return False
    
    def get_stats(self) -> dict:
        stats = {"total_users": 0, "total_keys": 0, "used_keys": 0, "total_searches": 0}
        users = self.get_all_users()
        stats["total_users"] = len(users)
        keys = self.get_all_keys()
        stats["total_keys"] = len(keys)
        stats["used_keys"] = sum(1 for k in keys if k.get("is_used", False))
        collection = self.get_collection("search_history")
        if collection is not None:
            try:
                stats["total_searches"] = collection.count_documents({})
            except:
                pass
        return stats