import os

from dotenv import load_dotenv

load_dotenv()

# Load variables from .env file
APP_ID = int(os.getenv("APP_ID", "730"))
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "300"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

STEAM_FEE = float(os.getenv("STEAM_FEE", "0.15"))  # ~15%
MIN_VOLUME = int(os.getenv("MIN_VOLUME", "20"))
MIN_ROI = float(os.getenv("MIN_ROI", "0.03"))  # 3%
MIN_PROFIT = float(os.getenv("MIN_PROFIT", "5.0"))  # RUB
