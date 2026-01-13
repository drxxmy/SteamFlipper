import asyncio
import logging

import aiosqlite

from core.env import (
    CHECK_INTERVAL_SECONDS,
    DB_PATH,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)
from core.models import ScanResult, WatchlistItem
from db.database import Database
from logs.logging import setup_logging
from notifier.telegram import TelegramNotifier
from scraper.steam_market import SteamMarketClient, build_opportunity

setup_logging()
log = logging.getLogger("automarket.market")


async def scan_item(
    *,
    db: Database,
    client: SteamMarketClient,
    notifier: TelegramNotifier | None = None,
    item: WatchlistItem
) -> ScanResult | None:
    # Fetch data for a specific item
    data = await client.fetch(item.app_id, item.item_name)

    # Skip if data was not fetched
    if not data:
        return None

    flip = build_opportunity(item.item_name, data)

    # Skip if couldn't build a flip opportunity
    if not flip:
        return None

    # Evaluate flip
    result = flip.evaluate()
    await db.save_opportunity(flip, result)

    # Send notification in Telegram
    if result.should_notify and notifier:
        if not await db.already_notified(flip.name):
            await notifier.notify_opportunity(item.app_id, flip)
            await db.mark_notified(flip.name)

    return ScanResult(flip, result)


async def scan_once(
    client: SteamMarketClient, notifier: TelegramNotifier | None = None
) -> None:
    async with aiosqlite.connect(DB_PATH) as conn:
        db = Database(conn)
        watchlist = await db.fetch_watchlist()
        for item in watchlist:
            if not watchlist:
                log.warning("⚠️ Watchlist is empty")
                continue

            result = await scan_item(db=db, client=client, notifier=notifier, item=item)

            if not result:
                continue

            # Log flip
            fmt, args = result.flip.log_message(result.evaluation)
            log.log(result.evaluation.log_level, fmt, *args)

            if await db.already_notified(result.flip.name):
                log.debug("⏱ %s skipped (cooldown)", result.flip.name)

            await conn.commit()
            await asyncio.sleep(1.5)  # Sleep for 1.5 seconds before next scan


async def run() -> None:
    await Database.init()
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

            await scan_once(client, notifier)

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
