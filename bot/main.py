import asyncio
import secrets
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
import aiofiles
from bot.config import Config
from bot.database import db

app = Client("FileStreamBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

# Web server for streaming
routes = web.RouteTableDef()

@routes.get("/")
async def home(request):
    return web.Response(text="MK File Stream Bot - Online ✅")

@routes.get("/watch/{file_id}")
async def watch(request):
    file_id = request.match_info['file_id']
    file_data = await db.get_file(file_id)
    if not file_data:
        return web.Response(text="File Not Found", status=404)

    template = await get_player_html()
    return web.Response(text=template, content_type='text/html')

@routes.get("/dl/{file_id}")
async def download(request):
    file_id = request.match_info['file_id']
    file_data = await db.get_file(file_id)
    if not file_data:
        return web.Response(text="File Not Found", status=404)

    msg = await app.get_messages(Config.LOG_CHANNEL, file_data['msg_id'])
    file = await app.download_media(msg, in_memory=True)

    return web.Response(
        body=file.getbuffer(),
        headers={
            'Content-Disposition': f'attachment; filename="{file_data["file_name"]}"',
            'Content-Type': 'application/octet-stream'
        }
    )

async def get_player_html():
    async with aiofiles.open('web/templates/player.html', mode='r') as f:
        return await f.read()

# Bot Handlers
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user_id = message.from_user.id
    await db.add_user(user_id)

    if user_id in Config.AUTH_USERS or await db.is_auth(user_id):
        await message.reply_text(
            "👋 **MK File Stream Bot**\n\n"
            "Send me any file and I'll give you:\n"
            "📥 Download Link\n"
            "🎬 Streaming Link with Player\n\n"
            "**Features:**\n"
            "• Open in VLC/MX Player\n"
            "• Change Audio Track\n"
            "• Direct Download\n\n"
            "Just send a file to start!"
        )
    else:
        await message.reply_text(
            "🔒 **Authentication Required**\n\n"
            "This bot is private. Send password to use:\n"
            "`/auth your_password`"
        )

@app.on_message(filters.command("auth"))
async def auth(client, message: Message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/auth password`")

    password = message.command[1]
    if password == Config.AUTH_PASSWORD:
        await db.auth_user(user_id)
        Config.AUTH_USERS.append(user_id)
        await message.reply_text("✅ **Authorized!**\n\nNow send me a file.")
    else:
        await message.reply_text("❌ **Wrong Password**\n\nOnly authorized users can use this bot.")

@app.on_message(filters.document | filters.video | filters.audio)
async def handle_file(client, message: Message):
    user_id = message.from_user.id

    if user_id not in Config.AUTH_USERS and not await db.is_auth(user_id):
        return await message.reply_text("🔒 **Not Authorized**\n\nUse `/auth password` first.")

    msg = await message.reply_text("📤 **Uploading to Channel...**")

    # Forward to log channel
    log_msg = await message.forward(Config.LOG_CHANNEL)

    # Generate unique file ID
    file_id = secrets.token_urlsafe(10)
    file = message.document or message.video or message.audio
    file_name = file.file_name or "file"
    file_size = file.file_size

    await db.add_file(file_id, file_name, file_size, log_msg.id)

    download_link = f"{Config.BASE_URL}/dl/{file_id}"
    stream_link = f"{Config.BASE_URL}/watch/{file_id}"

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Stream Online", url=stream_link)],
        [InlineKeyboardButton("📥 Download", url=download_link)]
    ])

    await msg.edit_text(
        f"✅ **File Uploaded!**\n\n"
        f"📁 **Name:** `{file_name}`\n"
        f"💾 **Size:** `{humanbytes(file_size)}`\n\n"
        f"**Links:**\n"
        f"🎬 Stream: `{stream_link}`\n"
        f"📥 Download: `{download_link}`",
        reply_markup=buttons
    )

def humanbytes(size):
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    while size > power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}"

async def start_web():
    web_app = web.Application()
    web_app.add_routes(routes)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', Config.PORT)
    await site.start()
    print(f"Web Server started on port {Config.PORT}")

async def main():
    await start_web()
    await app.start()
    print("Bot Started!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
