import asyncio

from rules.near_profit import is_nearly_profitable
from rules.profit import is_profitable
from scraper.steam_market import SteamMarketClient, build_opportunity

ITEMS = [
    # CS2 examples (market_hash_name must be exact)
    "AK-47 | Redline (Field-Tested)",
    "Fracture Case",
]

APPID_CS2 = 730


async def main():
    client = SteamMarketClient(currency=5)

    try:
        for name in ITEMS:
            data = await client.fetch_priceoverview(APPID_CS2, name)
            print(f"[DEBUG] raw data for {name}: {data}")
            if not data:
                continue

            opp = build_opportunity(name, data)
            if not opp:
                continue

            if is_nearly_profitable(opp):
                print(f"[NEAR] {opp.name} {opp.net_profit:.2f} RUB")

            if is_profitable(opp):
                print(
                    f"💰 {opp.name} | "
                    f"Profit: {opp.net_profit:.2f} RUB | "
                    f"Volume: {opp.volume}"
                )

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
