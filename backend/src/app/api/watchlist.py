import aiosqlite
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.env import DB_PATH
from db.database import add_watchlist_item
from main import scan_item
from scraper.steam_market import SteamMarketClient

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class WatchlistAddIn(BaseModel):
    url: str


@router.post("/")
async def add_to_watchlist(data: WatchlistAddIn):
    try:
        await add_watchlist_item(data.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok"}


@router.post("/watchlist")
async def add_watchlist_and_scan(
    data: WatchlistAddIn,
):
    async with aiosqlite.connect(DB_PATH) as db:
        item = await add_watchlist_item(data.url)

        client = SteamMarketClient(currency=5)

        await scan_item(
            db=db,
            client=client,
            notifier=None,  # optional
            item=item,
        )

        await db.commit()

    return {"status": "ok"}
