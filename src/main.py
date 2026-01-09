import asyncio
import logging
import os

from dotenv import load_dotenv

from logs.logging import setup_logging
from rules.near_profit import is_nearly_profitable
from rules.profit import is_profitable
from scraper.steam_market import SteamMarketClient, build_opportunity

# Load variables from .env file
load_dotenv()

CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS"))

ITEMS = [
    # CS2 examples (market_hash_name must be exact)
    "AK-47 | Redline (Field-Tested)",
    "Fracture Case",
]

APPID_CS2 = 730

setup_logging()
log = logging.getLogger("automarket")


async def scan_once(client: SteamMarketClient) -> None:
    for name in ITEMS:
        data = await client.fetch_priceoverview(APPID_CS2, name)
        if not data:
            continue

        opp = build_opportunity(name, data)
        if not opp:
            continue

        log.info(
            "✅ CHECK %-40s | buy=%7.2f sell=%7.2f net=%7.2f vol=%d",
            opp.name,
            opp.buy_price,
            opp.sell_price,
            opp.net_profit,
            opp.volume,
        )

        if is_profitable(opp):
            log.info(
                "💰 PROFIT %-30s | buy=%.2f sell=%.2f net=+%.2f",
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
