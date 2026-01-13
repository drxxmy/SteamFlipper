from datetime import UTC, datetime, timedelta
from pathlib import Path

import aiosqlite

from config.env import NOTIFY_COOLDOWN_MINUTES
from core.models import FlipEvaluation, FlipOpportunity

DB_PATH = Path("./src/db/steamflipper.db")


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(
            """
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                buy_price REAL NOT NULL,
                sell_price REAL NOT NULL,
                net_profit REAL NOT NULL,
                profit_pct REAL NOT NULL,
                volume INTEGER NOT NULL,
                spread_pct REAL NOT NULL,
                risk_level TEXT NOT NULL,
                profitable BOOLEAN NOT NULL,
                reject_reason TEXT,
                detected_at DATETIME NOT NULL
            );

            CREATE TABLE IF NOT EXISTS notifications (
                item_name TEXT NOT NULL,
                buy_price REAL NOT NULL,
                sell_price REAL NOT NULL,
                notified_at DATETIME NOT NULL,
                PRIMARY KEY (item_name, buy_price, sell_price)
            );
            """
        )
        await db.commit()


async def already_notified(db: aiosqlite.Connection, item_name: str) -> bool:
    query = """
        SELECT last_notified_at
        FROM notifications
        WHERE item_name = ?
    """
    async with db.execute(query, (item_name,)) as cur:
        row = await cur.fetchone()

    if not row:
        return False

    last_notified_at = datetime.fromisoformat(row[0])
    cooldown = timedelta(minutes=NOTIFY_COOLDOWN_MINUTES)

    return datetime.now(UTC) - last_notified_at < cooldown


async def mark_notified(db: aiosqlite.Connection, item_name: str) -> None:
    await db.execute(
        """
        INSERT INTO notifications (item_name, last_notified_at)
        VALUES (?, ?)
        ON CONFLICT(item_name)
        DO UPDATE SET last_notified_at = excluded.last_notified_at,
        """,
        (
            item_name,
            datetime.now(UTC).isoformat(),
        ),
    )
    await db.commit()


async def save_opportunity(
    db: aiosqlite.Connection,
    flip: FlipOpportunity,
    evaluation: FlipEvaluation,
) -> None:
    """
    Persist every evaluated flip (viable or rejected).
    """
    await db.execute(
        """
        INSERT INTO opportunities (
            item_name,
            buy_price,
            sell_price,
            net_profit,
            profit_pct,
            volume,
            spread_pct,
            risk_level,
            profitable,
            reject_reason,
            detected_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            flip.name,
            flip.buy_price,
            flip.sell_price,
            flip.net_profit,
            flip.profit_pct,
            flip.volume,
            flip.spread_pct,
            flip.risk_level.value,
            evaluation.profitable,
            evaluation.reject_reason.value if evaluation.reject_reason else None,
            datetime.now(UTC),
        ),
    )
