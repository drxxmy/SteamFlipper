import yaml

from config.env import WATCHLIST_PATH
from core.models import WatchItem


def load_watchlist() -> list[WatchItem]:
    with open(WATCHLIST_PATH, "r") as f:
        data = yaml.safe_load(f)

    return [
        WatchItem(
            name=item["name"],
            min_volume=item.get("min_volume", 0),
            min_profit=item.get("min_profit", 0.0),
        )
        for item in data.get("items", [])
    ]
