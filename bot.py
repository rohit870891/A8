from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN, LOG_CHANNEL, PORT
from pyrogram import utils as pyroutils
import uvicorn
from fastapi import FastAPI

# Set Pyrogram minimum channel ID for logging
pyroutils.MIN_CHANNEL_ID = LOG_CHANNEL

# Bot configuration
API_ID = API_ID
API_HASH = API_HASH
BOT_TOKEN = BOT_TOKEN
PORT = PORT  # Ensure you define this in `config.py`

# Initialize Pyrogram Client (Polling)
app = Client(
    "anime_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
)

# FastAPI server for optional status monitoring
server = FastAPI()

@server.get("/")
def home():
    return {"status": "running", "message": "Bot is active"}

@server.get("/status")
def status():
    return {"status": "ok", "users": len(get_all_users())}  # Example function to get user count

def run_server():
    """ Run the FastAPI server for status checking """
    uvicorn.run(server, host="0.0.0.0", port=PORT, log_level="info")

if __name__ == "__main__":
    import threading

    # Start FastAPI server in a separate thread
    threading.Thread(target=run_server, daemon=True).start()

    print("Bot is starting...")
    app.run()