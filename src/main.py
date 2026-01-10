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

setup_logging()
log = logging.getLogger("automarket.market")


async def scan_once(client: SteamMarketClient, notifier, watchlist) -> None:
    for item in watchlist:
        # Fetch data for a specific item
        data = await client.fetch(APP_ID, item.name)

        # Skip if data was not fetched
        if not data:
            continue

        flip = build_opportunity(item.name, data)
        if not flip:
            continue

        # Check if flip is profitable
        profitable = flip.is_profitable()
        viable = flip.is_viable()

        # Log everything
        fmt, args = flip.format_log(profitable)
        log.info(fmt, *args)

        # Notify only viable opportunities
        if viable and notifier:
            await notifier.notify_opportunity(flip)


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
