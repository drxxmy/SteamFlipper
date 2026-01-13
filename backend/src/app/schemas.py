from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OpportunityOut(BaseModel):
    id: int
    item_name: str
    buy_price: float
    sell_price: float
    net_profit: float
    profit_pct: float
    volume: int
    spread_pct: float
    risk_level: str
    profitable: bool
    reject_reason: Optional[str]
    detected_at: datetime


class WatchlistIn(BaseModel):
    appid: int
    market_hash_name: str


class WatchlistOut(WatchlistIn):
    id: int
    added_at: datetime
