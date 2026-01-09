import logging

from telegram import Bot
from telegram.constants import ParseMode

from core.models import FlipOpportunity

log = logging.getLogger("automarket.telegram")


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send(self, text: str) -> None:
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    async def notify_opportunity(self, opp: FlipOpportunity) -> None:
        try:
            await self.send(opp.format_telegram())
        except Exception:
            log.exception("❌ Telegram send failed...")
