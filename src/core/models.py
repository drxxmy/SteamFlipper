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

    def format_log(self, profitable: bool) -> tuple[str, tuple]:
        """
        Return a logging format string and arguments.
        """
        icon = "💰" if profitable else "✅"
        net_fmt = "+%.2f" if profitable else "%7.2f"

        return (
            f"{icon} %-30s | buy=%7.2f sell=%7.2f net={net_fmt} "
            f"profit=%6.2f%% vol=%6d risk=%s",
            (
                self.name,
                self.buy_price,
                self.sell_price,
                self.net_profit,
                self.profit_pct,
                self.volume,
                self.risk_level.value,
            ),
        )

    def format_telegram(self) -> str:
        """
        Format Telegram notification message.
        """
        return (
            f"<b>{self.name}</b>\n"
            f"⚠️ Risk: <b>{self.risk_level.value}</b>\n"
            f"💳 Buy: {self.buy_price:.2f} ₽\n"
            f"💸 Sell: {self.sell_price:.2f} ₽\n"
            f"🤑 <b>Profit: +{self.net_profit:.2f} ₽ "
            f"({self.profit_pct:.2f}%)</b>\n"
            f"📦 Volume: {self.volume}"
        )


@dataclass
class WatchItem:
    name: str
    min_volume: int = 0
    min_profit: float = 0.0
