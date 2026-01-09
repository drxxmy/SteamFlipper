from dataclasses import dataclass

from .risks import RiskLevel


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
    def profit_pct(self) -> float:
        """
        Return on investment (ROI) after Steam fees.

        Represents how much the invested capital grows (or shrinks)
        relative to the buy price.
        """
        if self.buy_price <= 0:
            return 0.0

        return self.net_profit / self.buy_price

    @property
    def spread_pct(self) -> float:
        """
        Relative price spread between buy and sell prices.

        Expressed as a fraction of the buy price. Large spreads often indicate
        low liquidity, price manipulation, or rare outlier sales rather than
        stable, repeatable profit opportunities.
        """
        return (self.sell_price - self.buy_price) / self.buy_price

    @property
    def risk_level(self) -> RiskLevel:
        """
        Classify risk based on liquidity and price spread.
        """

        # Extremely wide spreads are almost always outliers
        if self.spread_pct > 0.40:
            return RiskLevel.HIGH

        # Low volume = hard to exit position
        if self.volume < 50:
            return RiskLevel.HIGH

        # Medium risk: still tradable, but watch closely
        if self.spread_pct > 0.25 or self.volume < 150:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW


@dataclass
class WatchItem:
    name: str
    min_volume: int = 0
    min_profit: float = 0.0
