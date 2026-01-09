from core.models import FlipOpportunity


def is_profitable(item: FlipOpportunity) -> bool:
    return item.net_profit >= 5.0 and item.volume >= 50
