from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db.database import add_watchlist_item

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
