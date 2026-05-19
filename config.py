import time

# Bot Information
BOT_TOKEN = "8630078554:AAHZdh21I3D__fObqDOvco5ge8zFkb6yg54"
BOT_NAME = "KING OSINT"
BOT_VERSION = "26.4.8"
BOT_START_TIME = time.time()

# MongoDB Configuration
MONGO_URI = "mongodb+srv://king:kai@cluster0.pv2q7id.mongodb.net/?appName=Cluster0"
MONGO_DB_NAME = "OSINT_DB"

# Owner and Admin
OWNER_IDS = [1451422178]
ADMIN_USERNAMES = []

# Support
SUPPORT_USERNAME = "KINGGKAI"
DEVELOPER_USERNAME = "KINGGKAI"
SUPPORT_GROUP_LINK = "https://t.me/+zeKnIiKAGnk3ZGE1"
UPI_ID = "@kinggkai"

# API URLs
DEFAULT_APIS = {
    "num": "https://anon-num-info.vercel.app/num?key=numt0605&num=",
    "aadhar": "https://anon-num-info.vercel.app/aadhar?key=tempad705&id=",
    "pak_num": "https://anon-pak-info.vercel.app/num?key=temp1004&q=",
    "pak_cnic": "https://anon-pak-info.vercel.app/cnic?key=temp1004&q=",
    "pak_police": "https://anon-pak-info.vercel.app/police?key=temp1004&num=",
    "gst_billing": "https://anon-gst-info.vercel.app/advanced/gstin?key=temp25gst&gstin=",
    "pan_gst": "https://anon-gst-info.vercel.app/advanced/pan?key=temp25gst&pan=",
    "aadhar_family": "https://anon-family-info.vercel.app/aadhar?key=temp123&q="
}

# Default Settings
DAILY_FREE_LIMIT = 15
DEFAULT_REFERRAL_COINS = 10

# Maintenance Mode
MAINTENANCE_MODE = False
MAINTENANCE_MESSAGE = "🔧 *Bot is under maintenance*\\n\\nPlease try again after some time\\."

# API Services Mapping
API_SERVICES = {
    "num": {"name": "Indian Number", "emoji": "🔢"},
    "aadhar": {"name": "Indian Aadhar", "emoji": "🆔"},
    "pak_num": {"name": "Pakistan Number", "emoji": "🇵🇰"},
    "pak_cnic": {"name": "Pakistan CNIC", "emoji": "🪪"},
    "pak_police": {"name": "Pakistan Police", "emoji": "🚔"},
    "gst_billing": {"name": "GST Billing", "emoji": "💰"},
    "pan_gst": {"name": "PAN to GST", "emoji": "📇"},
    "aadhar_family": {"name": "Aadhar Family", "emoji": "👨‍👩‍👧"}
}

# Conversation States
ASKING_NUMBER = 1
ASKING_AADHAR = 2
ASKING_PAK_NUM = 3
ASKING_PAK_CNIC = 4
ASKING_PAK_POLICE = 5
ASKING_GST_BILLING = 6
ASKING_PAN_GST = 7
ASKING_AADHAR_FAMILY = 8
ASKING_BROADCAST = 10
ASKING_BLOCK_NUMBER = 11
ASKING_UNBLOCK_NUMBER = 12
ASKING_REFERRAL_AMOUNT = 13
ASKING_ADD_ADMIN = 14
ASKING_REMOVE_ADMIN = 15
ASKING_ADD_COINS_USER = 16
ASKING_ADD_COINS_AMOUNT = 17
ASKING_API_UPDATE = 18
ASKING_API_SELECT = 19
ASKING_SET_DAILY_LIMIT = 20
ASKING_REDEEM_KEY = 21
ASKING_REVOKE_KEY = 22
ASKING_REVOKE_KEY_ID = 23
ASKING_BLOCK_USER = 24
