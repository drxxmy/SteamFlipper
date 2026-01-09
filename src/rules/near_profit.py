from core.models import FlipOpportunity


def is_nearly_profitable(item: FlipOpportunity) -> bool:
    return item.net_profit > -3.0
