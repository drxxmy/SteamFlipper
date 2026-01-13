import aiosqlite
from fastapi import APIRouter, Query

from app.schemas import OpportunityOut
from core.env import DB_PATH
from db.database import Database

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("/", response_model=list[OpportunityOut])
async def list_opportunities(
    profitable: bool | None = None,
    limit: int = Query(100, le=500),
):
    async with aiosqlite.connect(DB_PATH) as conn:
        db = Database(conn)
        query = """
        SELECT *
        FROM (
            SELECT
                o.*,
                ROW_NUMBER() OVER (
                    PARTITION BY o.item_name
                    ORDER BY o.net_profit DESC, o.detected_at DESC
                ) AS rn
            FROM opportunities o
            WHERE 1=1
        )
        WHERE rn = 1
        """
        params: list = []

        if profitable is not None:
            query += " AND profitable = ?"
            params.append(int(profitable))

        query += """
        ORDER BY profit_pct DESC
        LIMIT ?
        """
        params.append(limit)

        return await db.fetch_all(query, tuple(params))
