from dataclasses import dataclass


@dataclass
class FlipOpportunity:
    name: str
    buy_price: float
    sell_price: float
    volume: int

    @property
    def net_profit(self) -> float:
        """
        Net profit after Steam market fees.

        Steam takes a 15% fee on each sale, so only 85% of the sell price
        is actually received. This value represents the real, final profit
        (or loss) of a flip after buying and selling the item.
        """
        return self.sell_price * 0.85 - self.buy_price

    @property
    def spread_pct(self) -> float:
        """
        Relative price spread between buy and sell prices.

        Expressed as a fraction of the buy price. Large spreads often indicate
        low liquidity, price manipulation, or rare outlier sales rather than
        stable, repeatable profit opportunities.
        """
        return (self.sell_price - self.buy_price) / self.buy_price


@dataclass
class WatchItem:
    name: str
    min_volume: int = 0
    min_profit: float = 0.0
