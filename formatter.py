import json
from typing import Dict

def clean_response_data(data: dict) -> dict:
    """Remove developer/usernames from response"""
    if isinstance(data, dict):
        for key in ["DEVELOPER", "developer", "DEVELOPER_USERNAME", "developer_username", "username", "USERNAME"]:
            if key in data:
                del data[key]
        
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = clean_response_data(value)
            elif isinstance(value, list):
                data[key] = [clean_response_data(item) if isinstance(item, dict) else item for item in value]
    elif isinstance(data, list):
        data = [clean_response_data(item) if isinstance(item, dict) else item for item in data]
    
    return data

def format_raw_result(result: Dict, query: str, search_type: str) -> str:
    """Return raw API response in JSON format"""
    cleaned_result = clean_response_data(result.copy())
    formatted_json = json.dumps(cleaned_result, indent=2, ensure_ascii=False)
    
    output = f"""
SEARCH RESULT
Query: {query}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```json
{formatted_json}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
return output

def format_system_info(maintenance_mode: bool, settings: dict) -> str:
"""Format system information"""
from utils import get_bot_uptime, get_system_info
from config import BOT_NAME, BOT_VERSION

sys_info = get_system_info()
uptime = get_bot_uptime()

output = f"""
SYSTEM INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bot Info:
• Name: {BOT_NAME}
• Version: {BOT_VERSION}
• Uptime: {uptime}
• Maintenance Mode: {'ACTIVE' if maintenance_mode else 'INACTIVE'}

System:
• OS: {sys_info['platform']} {sys_info['platform_release']}
• Python: {sys_info['python_version']}

Resource Usage:
• CPU: {sys_info['cpu_percent']}%
• RAM: {sys_info['memory_used']}MB / {sys_info['memory_total']}MB ({sys_info['memory_percent']}%)
• Disk: {sys_info['disk_used']}MB / {sys_info['disk_total']}MB ({sys_info['disk_percent']}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
return output

def format_keys(key_type: str, count: int, credits: int, keys: list) -> str:
"""Format generated keys"""
output = f"""
KEYS GENERATED SUCCESSFULLY!

Key Type: {key_type}
Count: {count}
Credits per Key: {credits}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
for i, key in enumerate(keys, 1):
output += f"\n{i}. {key}"
output += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
return output
