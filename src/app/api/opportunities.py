from fastapi import APIRouter, Query

from app.schemas import OpportunityOut
from db.database import fetch_all

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("/", response_model=list[OpportunityOut])
async def list_opportunities(
    profitable: bool | None = None,
    limit: int = Query(100, le=500),
):
    query = "SELECT * FROM opportunities WHERE 1=1"
    params: list = []

    if profitable is not None:
        query += " AND profitable = ?"
        params.append(int(profitable))

    query += " ORDER BY detected_at DESC LIMIT ?"
    params.append(limit)

    return await fetch_all(query, tuple(params))
