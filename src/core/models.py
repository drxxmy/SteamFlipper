from dataclasses import dataclass


@dataclass
class FlipOpportunity:
    name: str
    buy_price: float
    sell_price: float
    volume: int

    @property
    def net_profit(self) -> float:
        return self.sell_price * 0.85 - self.buy_price


@dataclass
class WatchItem:
    name: str
    min_volume: int = 0
    min_profit: float = 0.0
