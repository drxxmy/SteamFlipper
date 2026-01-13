import logging
from asyncio import Semaphore, sleep
from json import JSONDecodeError
from typing import cast

from httpx import AsyncClient, RequestError, Response, Timeout

from core.models import FlipOpportunity, SteamPriceOverview
from core.utils import parse_price

STEAM_PRICEOVERVIEW_URL = "https://steamcommunity.com/market/priceoverview/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# Global semaphore to protect yourself
_SEMAPHORE = Semaphore(3)

log = logging.getLogger("steamflipper.scraper")


class SteamMarketClient:
    def __init__(self, currency: int = 5) -> None:
        """
        currency=5 → RUB
        """
        self.currency: int = currency
        self.failures: int = 0
        self._client: AsyncClient = AsyncClient(
            headers=HEADERS,
            timeout=Timeout(10.0),
        )

    async def fetch(self, app_id: int, item_name: str) -> SteamPriceOverview | None:
        """
        Returns raw Steam priceoverview JSON or None.
        Never raises.
        """
        params = {
            "appid": app_id,
            "currency": self.currency,
            "market_hash_name": item_name,
        }

        delay: float = min(5.0, 1.2 + self.failures * 0.8)

        async with _SEMAPHORE:
            # Mandatory delay (Steam is sensitive)
            await sleep(delay)

            try:
                resp: Response = await self._client.get(
                    STEAM_PRICEOVERVIEW_URL, params=params
                )

                if resp.status_code == 429:
                    log.warning("⏳ Rate limited, backing off")
                    await sleep(60)
                    return None

                if resp.status_code != 200:
                    self.failures += 1
                    log.warning(
                        "❗ %s Steam HTTP %d",
                        item_name,
                        resp.status_code,
                    )
                    return None

                try:
                    data: SteamPriceOverview = cast(SteamPriceOverview, resp.json())
                except JSONDecodeError:
                    self.failures += 1
                    log.warning("❗ %s Invalid JSON", item_name)
                    return None

                if not data.get("success"):
                    self.failures += 1
                    log.warning("❗ %s Steam rate-limited", item_name)
                    return None

                # Reset failures counter on success
                self.failures = 0
                return data

            except RequestError as e:
                self.failures += 1
                log.warning(
                    "❗ %s Network error %s %s: %r",
                    item_name,
                    e.request.method if e.request else "?",
                    e.request.url if e.request else "?",
                    e,
                )
                return None

    async def close(self) -> None:
        await self._client.aclose()


def build_opportunity(name: str, data: SteamPriceOverview) -> FlipOpportunity | None:
    try:
        lowest: str | None = data.get("lowest_price")
        median: str | None = data.get("median_price")

        if not lowest or not median:
            return None

        buy_price: float = parse_price(lowest)
        sell_price: float = parse_price(median)
        volume: int = int(data.get("volume", "0").replace(",", ""))

        if buy_price <= 0 or sell_price <= 0:
            return None

        return FlipOpportunity(
            name=name,
            buy_price=buy_price,
            sell_price=sell_price,
            volume=volume,
        )
    except Exception:
        return None
