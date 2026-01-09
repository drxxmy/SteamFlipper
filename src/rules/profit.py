from core.models import FlipOpportunity
from core.risks import RiskLevel


def is_profitable(item: FlipOpportunity) -> bool:
    # Minimum profit of a flip
    if item.net_profit < 15:
        return False

    # Filter items with low liquidity
    if item.volume < 100:
        return False

    # Filter high risk flips
    if item.risk_level == RiskLevel.HIGH:
        return False

    return True
