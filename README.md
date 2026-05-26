# MK File Stream Bot

Telegram Bot for File to Direct Link + Streaming Player

## Features
- File to Download Link
- File to Stream Link with Web Player
- VLC/MX Player/PlayIt Support
- Audio Track Switcher
- Password Auth System
- MongoDB Storage

## Deploy to Render

1. Fork this repo
2. Create Web Service on Render
3. Add Environment Variables from `.env.example`
4. Deploy!

## Environment Variables
- `API_ID` - Telegram API ID
- `API_HASH` - Telegram API Hash
- `BOT_TOKEN` - Bot Token from @BotFather
- `LOG_CHANNEL` - Channel ID for file storage
- `AUTH_PASSWORD` - Password for auth
- `MONGO_URL` - MongoDB connection string
- `BASE_URL` - Your Render URL

## Usage
1. `/start` - Start bot
2. `/auth password` - Authorize
3. Send file - Get links
