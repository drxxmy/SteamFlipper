import logging
from dataclasses import dataclass
from enum import Enum
from typing import NotRequired, TypedDict

from core.env import (
    MIN_PROFIT,
    MIN_ROI,
    MIN_VOLUME,
    RISK_HIGH_MIN_VOLUME,
    RISK_HIGH_SPREAD,
    RISK_MEDIUM_MIN_VOLUME,
    RISK_MEDIUM_SPREAD,
    STEAM_FEE,
)

MAX_NAME_LEN = 28


@dataclass(slots=True)
class WatchlistItem:
    app_id: int
    item_name: str


@dataclass
class SteamPriceOverview(TypedDict):
    success: bool
    lowest_price: NotRequired[str]
    median_price: NotRequired[str]
    volume: NotRequired[str]


class RejectReason(str, Enum):
    LOW_VOLUME = "LOW_VOLUME"
    LOW_PROFIT = "LOW_PROFIT"
    LOW_ROI = "LOW_ROI"
    NEGATIVE_ROI = "NEGATIVE_ROI"
    HIGH_RISK = "HIGH_RISK"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    def badge(self) -> str:
        match self:
            case self.LOW:
                return "🟢"
            case self.MEDIUM:
                return "🟡"
            case self.HIGH:
                return "🔴"


@dataclass(frozen=True)
class FlipEvaluation:
    profitable: bool
    reject_reason: RejectReason | None

    @property
    def log_level(self) -> int:
        return logging.INFO if self.profitable else logging.DEBUG

    @property
    def should_notify(self) -> bool:
        return self.profitable


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
        return self.sell_price * (1 - STEAM_FEE) - self.buy_price

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
        Classify risk based on liquidity and spread.
        """

        # HIGH risk: likely traps / illiquid / fake spikes
        if self.spread_pct >= RISK_HIGH_SPREAD or self.volume <= RISK_HIGH_MIN_VOLUME:
            return RiskLevel.HIGH

        # MEDIUM risk: tradable but requires caution
        if (
            self.spread_pct >= RISK_MEDIUM_SPREAD
            or self.volume <= RISK_MEDIUM_MIN_VOLUME
        ):
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def evaluate(self) -> FlipEvaluation:
        if self.profit_pct < 0:
            return FlipEvaluation(False, RejectReason.NEGATIVE_ROI)

        if self.risk_level == RiskLevel.HIGH:
            return FlipEvaluation(False, RejectReason.HIGH_RISK)

        if self.volume < MIN_VOLUME:
            return FlipEvaluation(False, RejectReason.LOW_VOLUME)

        if self.net_profit < MIN_PROFIT:
            return FlipEvaluation(False, RejectReason.LOW_PROFIT)

        if self.profit_pct < MIN_ROI:
            return FlipEvaluation(False, RejectReason.LOW_ROI)

        return FlipEvaluation(True, None)

    @property
    def short_name(self) -> str:
        if len(self.name) <= MAX_NAME_LEN:
            return self.name
        return self.name[: MAX_NAME_LEN - 1] + "…"

    def log_message(self, result: FlipEvaluation) -> tuple[str, tuple]:
        """
        Returns a log message format and arguments.
        """
        if result.profitable:
            return (
                f"💰 %-{MAX_NAME_LEN}s | BUY %.2f SELL %.2f NET +%.2f ROI %.2f%% VOL %d RISK %s",
                (
                    self.short_name,
                    self.buy_price,
                    self.sell_price,
                    self.net_profit,
                    self.profit_pct * 100,
                    self.volume,
                    self.risk_level.value,
                ),
            )

        reason = result.reject_reason.value if result.reject_reason else "—"

        return (
            f"❌ %-{MAX_NAME_LEN}s | [red]%s[/red] BUY %.2f SELL %.2f SPREAD %.3f NET %.2f ROI %.2f%% VOL %d RISK %s",
            (
                self.short_name,
                reason,
                self.buy_price,
                self.sell_price,
                self.spread_pct,
                self.net_profit,
                self.profit_pct * 100,
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
            f"{self.risk_level.badge()} Risk: <b>{self.risk_level.value}</b>\n"
            f"💳 Buy: {self.buy_price:.2f} ₽\n"
            f"💸 Sell: {self.sell_price:.2f} ₽\n"
            f"🤑 <b>Profit: +{self.net_profit:.2f} ₽ "
            f"({(self.profit_pct * 100):.2f}%)</b>\n"
            f"📦 Volume: {self.volume}"
        )


@dataclass(slots=True)
class ScanResult:
    flip: FlipOpportunity
    evaluation: FlipEvaluation
