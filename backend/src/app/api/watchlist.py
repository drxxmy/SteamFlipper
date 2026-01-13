import aiosqlite
from fastapi import APIRouter
from pydantic import BaseModel

from core.env import DB_PATH
from db.database import Database
from main import log, scan_item
from scraper.steam_market import SteamMarketClient

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class WatchlistAddIn(BaseModel):
    url: str


@router.post("")
async def add_watchlist_and_scan(
    data: WatchlistAddIn,
):
    async with aiosqlite.connect(DB_PATH) as conn:
        db = Database(conn)

        item = await db.add_watchlist_item(data.url)

        client = SteamMarketClient(currency=5)

        result = await scan_item(
            db=db,
            client=client,
            notifier=None,  # optional
            item=item,
        )

        if not result:
            return

        # Log flip
        fmt, args = result.flip.log_message(result.evaluation)
        log.log(result.evaluation.log_level, fmt, *args)

        await db.commit()

    return {"status": "ok"}
