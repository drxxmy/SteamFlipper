import asyncio
import logging

import aiosqlite

from config.env import (
    CHECK_INTERVAL_SECONDS,
    DB_PATH,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)
from core.models import WatchlistItem
from db.database import (
    already_notified,
    fetch_watchlist,
    init_db,
    mark_notified,
    save_opportunity,
)
from logs.logging import setup_logging
from notifier.telegram import TelegramNotifier
from scraper.steam_market import SteamMarketClient, build_opportunity

setup_logging()
log = logging.getLogger("automarket.market")


async def scan_once(
    client: SteamMarketClient, notifier, watchlist: list[WatchlistItem]
) -> None:
    for item in watchlist:
        # Fetch data for a specific item
        data = await client.fetch(item.appid, item.market_hash_name)

        await asyncio.sleep(1.5)  # 1–2 seconds is safe

        # Skip if data was not fetched
        if not data:
            continue

        flip = build_opportunity(item.market_hash_name, data)

        # Skip if couldn't build a flip opportunity
        if not flip:
            continue

        async with aiosqlite.connect(DB_PATH) as db:
            # Evaluate flip
            result = flip.evaluate()

            await save_opportunity(db, flip, result)

            # Log flip
            fmt, args = flip.log_message(result)
            log.log(result.log_level, fmt, *args)

            # Send notification in Telegram
            if result.should_notify and notifier:
                if not await already_notified(db, flip.name):
                    await notifier.notify_opportunity(item.appid, flip)
                    await mark_notified(db, flip.name)
                else:
                    log.debug("⏱ %s skipped (cooldown)", flip.name)

            await db.commit()


async def run() -> None:
    await init_db()
    client = SteamMarketClient(currency=5)
    notifier = None
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        notifier = TelegramNotifier(
            TELEGRAM_BOT_TOKEN,
            TELEGRAM_CHAT_ID,
        )

    try:
        while True:
            log.info("🔄 Starting market scan")
            watchlist = await fetch_watchlist()

            if not watchlist:
                log.warning("⚠️ Watchlist is empty")
            else:
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
