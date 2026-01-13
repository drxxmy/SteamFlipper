import re
from urllib.parse import quote, unquote

_PRICE_RE = re.compile(r"[0-9]+(?:[.,][0-9]+)?")
_STEAM_MARKET_RE = re.compile(r"/market/listings/(?P<appid>\d+)/(?P<hash>.+)$")


def parse_price(price_str: str) -> float:
    """
    Converts Steam price string to float.
    Example: '1 234,56 руб.' → 1234.56
    """
    if not price_str:
        return 0.0

    # Replace comma with dot, remove spaces
    cleaned = price_str.replace(",", ".").replace(" ", "")
    match = _PRICE_RE.search(cleaned)

    return float(match.group()) if match else 0.0


def steam_market_url(appid: int, market_hash_name: str) -> str:
    """
    Returns a Steam market URL for the specified appid and item name.
    """
    return (
        f"https://steamcommunity.com/market/listings/"
        f"{appid}/{quote(market_hash_name, safe='')}"
    )


def parse_steam_market_url(url: str) -> tuple[int, str]:
    match = _STEAM_MARKET_RE.search(url)
    if not match:
        raise ValueError("Invalid Steam Market URL")

    appid = int(match.group("appid"))
    market_hash_name = unquote(match.group("hash"))

    return appid, market_hash_name
