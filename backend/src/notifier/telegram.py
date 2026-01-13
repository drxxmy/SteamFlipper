import logging

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from config.env import APP_ID
from core.models import FlipOpportunity
from core.utils import steam_market_url

log = logging.getLogger("automarket.telegram")


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def notify_opportunity(self, flip: FlipOpportunity) -> None:
        url = steam_market_url(APP_ID, flip.name)

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="🛒 Buy on Steam",
                        url=url,
                    ),
                    InlineKeyboardButton(
                        text="📈 Price Graph",
                        url=url + "#pricehistory",
                    ),
                ]
            ]
        )

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=flip.format_telegram(),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )

        except Exception:
            log.exception("❌ Telegram send failed...")
