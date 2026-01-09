from core.models import FlipOpportunity


def is_profitable(item: FlipOpportunity) -> bool:
    # Minimum profit of a flip
    if item.net_profit < 15:
        return False

    # Filter items with low liquidity
    if item.volume < 100:
        return False

    # Filter items with risky spreads (over 30%)
    if item.spread_pct > 0.30:
        return False

    return True
