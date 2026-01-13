import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Load variables from .env file
APP_ID = int(os.getenv("APP_ID", "730"))
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "300"))

DB_PATH = Path(os.getenv("DB_PATH", "db/database.db"))

WATCHLIST_PATH = Path(os.getenv("WATCHLIST_PATH", "config/watchlist.yaml"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

STEAM_FEE = float(os.getenv("STEAM_FEE", "0.15"))  # ~15%
MIN_VOLUME = int(os.getenv("MIN_VOLUME", "20"))
MIN_ROI = float(os.getenv("MIN_ROI", "0.03"))  # 3%
MIN_PROFIT = float(os.getenv("MIN_PROFIT", "5.0"))  # RUB

RISK_HIGH_SPREAD = float(os.getenv("RISK_HIGH_SPREAD", 0.40))
RISK_MEDIUM_SPREAD = float(os.getenv("RISK_MEDIUM_SPREAD", 0.25))

RISK_HIGH_MIN_VOLUME = int(os.getenv("RISK_HIGH_MIN_VOLUME", 50))
RISK_MEDIUM_MIN_VOLUME = int(os.getenv("RISK_MEDIUM_MIN_VOLUME", 150))

NOTIFY_COOLDOWN_MINUTES = int(os.getenv("NOTIFY_COOLDOWN_MINUTES", 30))
