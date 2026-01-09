import asyncio
import logging

from config import CHECK_INTERVAL_SECONDS, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from logs.logging import setup_logging
from notifier.telegram import TelegramNotifier
from rules.near_profit import is_nearly_profitable
from rules.profit import is_profitable
from scraper.steam_market import SteamMarketClient, build_opportunity

ITEMS = [
    # CS2 examples (market_hash_name must be exact)
    "AK-47 | Redline (Field-Tested)",
    "Fracture Case",
]

APPID_CS2 = 730

setup_logging()
log = logging.getLogger("automarket")

notifier = None
if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    notifier = TelegramNotifier(
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHAT_ID,
    )


async def scan_once(client: SteamMarketClient) -> None:
    for name in ITEMS:
        data = await client.fetch_priceoverview(APPID_CS2, name)
        if not data:
            continue

        opp = build_opportunity(name, data)
        if not opp:
            continue

        log.info(
            "✅ %-40s | buy=%7.2f sell=%7.2f net=%7.2f vol=%d",
            opp.name,
            opp.buy_price,
            opp.sell_price,
            opp.net_profit,
            opp.volume,
        )

        if is_profitable(opp):
            if notifier:
                try:
                    await notifier.send(
                        f"💰 <b>PROFIT</b>\n"
                        f"{opp.name}\n"
                        f"Buy: {opp.buy_price:.2f} ₽\n"
                        f"Sell: {opp.sell_price:.2f} ₽\n"
                        f"Net: <b>{opp.net_profit:.2f} ₽</b>\n"
                        f"Volume: {opp.volume}"
                    )
                except Exception:
                    log.exception("❌ Telegram send failed...")

            log.info(
                "💰 PROFIT %-30s | Buy=%.2f Sell=%.2f Net=+%.2f",
                opp.name,
                opp.buy_price,
                opp.sell_price,
                opp.net_profit,
            )


async def run() -> None:
    client = SteamMarketClient(currency=5)

    try:
        while True:
            log.info("🔄 Starting market scan")
            await scan_once(client)
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
