import yaml

from core.models import WatchItem


def load_watchlist(path="src/config/watchlist.yaml") -> list[WatchItem]:
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return [
        WatchItem(
            name=item["name"],
            min_volume=item.get("min_volume", 0),
            min_profit=item.get("min_profit", 0.0),
        )
        for item in data.get("items", [])
    ]
