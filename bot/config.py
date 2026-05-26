import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", 0))
    AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD", "MKBot@2026")
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    MONGO_URL = os.environ.get("MONGO_URL", "")
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080")
    PORT = int(os.environ.get("PORT", 8080))

    # Authorized users list - add user IDs here
    AUTH_USERS = [OWNER_ID]
