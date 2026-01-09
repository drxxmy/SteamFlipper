import asyncio
import logging

from config import APP_ID, CHECK_INTERVAL_SECONDS, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from core.watchlist import load_watchlist
from logs.logging import setup_logging
from notifier.telegram import TelegramNotifier
from rules.near_profit import is_nearly_profitable
from rules.profit import is_profitable
from scraper.steam_market import SteamMarketClient, build_opportunity

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

        # Log opportunity
        log.info(
            "✅ %-30s | buy=%7.2f sell=%7.2f net=%7.2f vol=%6d spread=%6.2f%%",
            opp.name,
            opp.buy_price,
            opp.sell_price,
            opp.net_profit,
            opp.volume,
            opp.spread_pct * 100,
        )

        # Check if opportunity is profitable
        if is_profitable(opp):
            # Send a telegram notification
            if notifier:
                try:
                    await notifier.send(
                        f"<b>{opp.name}</b>\n"
                        f"💳 Buy: {opp.buy_price:.2f} ₽\n"
                        f"💸 Sell: {opp.sell_price:.2f} ₽\n"
                        f"🤑 <b>Net: +{opp.net_profit:.2f} ₽</b>\n"
                    )
                except Exception:
                    log.exception("❌ Telegram send failed...")

            # Log into the terminal
            log.info(
                "💰 %-30s | buy=%7.2f sell=%7.2f net=+%.2f vol=%6d spread=%6.2f%%",
                opp.name,
                opp.buy_price,
                opp.sell_price,
                opp.net_profit,
                opp.volume,
                opp.spread_pct * 100,
            )


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
