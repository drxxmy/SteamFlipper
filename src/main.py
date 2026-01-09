import asyncio
import logging

from config.env import (
    APP_ID,
    CHECK_INTERVAL_SECONDS,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)
from core.watchlist import load_watchlist
from logs.logging import setup_logging
from notifier.telegram import TelegramNotifier
from scraper.steam_market import SteamMarketClient, build_opportunity
from strategy.profit import is_profitable

setup_logging()
log = logging.getLogger("automarket")


async def scan_once(client: SteamMarketClient, notifier, watchlist) -> None:
    for item in watchlist:
        # Fetch data for a specific item
        data = await client.fetch(APP_ID, item.name)

        # Skip if data was not fetched
        if not data:
            continue

        opp = build_opportunity(item.name, data)
        if not opp:
            continue

        # Check if opportunity is profitable
        profitable = is_profitable(opp)

        # Log opportunity
        fmt, args = opp.format_log(profitable)
        log.info(fmt, *args)

        # Send Telegram message
        if profitable and notifier:
            notifier.notify_opportunity(opp)


async def run() -> None:
    client = SteamMarketClient(currency=5)
    notifier = None
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        notifier = TelegramNotifier(
            TELEGRAM_BOT_TOKEN,
            TELEGRAM_CHAT_ID,
        )

    watchlist = load_watchlist()

    try:
        while True:
            log.info("🔄 Starting market scan")
            await scan_once(client, notifier, watchlist)
            log.info("😴 Sleeping for %d seconds", CHECK_INTERVAL_SECONDS)
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)

    except asyncio.CancelledError:
        pass

    except KeyboardInterrupt:
        log.info("🛑 Shutdown requested")

    finally:
        await client.close()
        log.info("👋 Steam Market client closed")


if __name__ == "__main__":
    asyncio.run(run())
