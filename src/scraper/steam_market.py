import asyncio
import logging
from typing import Optional

import httpx

from core.models import FlipOpportunity
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
_SEMAPHORE = asyncio.Semaphore(3)

log = logging.getLogger("automarket")


class SteamMarketClient:
    def __init__(self, currency: int = 5):
        """
        currency=5 → RUB
        """
        self.currency = currency
        self.failures = 0
        self._client = httpx.AsyncClient(
            headers=HEADERS,
            timeout=httpx.Timeout(10.0),
        )

    async def fetch(self, appid: int, market_hash_name: str) -> Optional[dict]:
        """
        Returns raw Steam priceoverview JSON or None.
        Never raises.
        """
        params = {
            "appid": appid,
            "currency": self.currency,
            "market_hash_name": market_hash_name,
        }

        delay = min(5.0, 1.2 + self.failures * 0.8)

        async with _SEMAPHORE:
            # Mandatory delay (Steam is sensitive)
            await asyncio.sleep(delay)

            try:
                resp = await self._client.get(STEAM_PRICEOVERVIEW_URL, params=params)

                if resp.status_code != 200:
                    self.failures += 1
                    log.warning(
                        "(%s) Steam HTTP %d",
                        market_hash_name,
                        resp.status_code,
                    )
                    return None

                data = resp.json()

                # Steam sometimes returns {"success": false}
                if not data:
                    log.warning("(%s) Empty response", market_hash_name)
                elif not data.get("success"):
                    log.warning("(%s) Steam rate-limited", market_hash_name)

                if not data:
                    self.failures += 1
                    log.warning("(%s) Empty response", market_hash_name)
                    return None

                if not data.get("success"):
                    self.failures += 1
                    log.warning("(%s) Steam rate-limited", market_hash_name)
                    return None

                # Reset failures counter on success
                self.failures = 0
                return data

            except httpx.RequestError as e:
                self.failures += 1
                log.warning(
                    "(%s) Network error %s %s: %r",
                    market_hash_name,
                    e.request.method if e.request else "?",
                    e.request.url if e.request else "?",
                    e,
                )
                return None

            except ValueError:
                self.failures += 1
                log.warning("(%s) Invalid JSON", market_hash_name)
                return None

    async def close(self) -> None:
        await self._client.aclose()


def build_opportunity(name: str, data: dict) -> Optional[FlipOpportunity]:
    try:
        buy_price = parse_price(data.get("lowest_price"))
        sell_price = parse_price(data.get("median_price"))
        volume = int(data.get("volume", "0").replace(",", ""))

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
