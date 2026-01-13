from datetime import UTC, datetime, timedelta
from typing import Iterable

import aiosqlite

from core.env import DB_PATH, NOTIFY_COOLDOWN_MINUTES
from core.models import FlipEvaluation, FlipOpportunity, WatchlistItem
from core.utils import parse_steam_market_url


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

            CREATE TABLE IF NOT EXISTS watchlist (
              id INTEGER PRIMARY KEY AUTOINCREMENT,

              app_id INTEGER NOT NULL,
              item_name TEXT NOT NULL,

              created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

              UNIQUE (app_id, item_name)
            );
            """
        )
        await db.commit()


async def already_notified(db: aiosqlite.Connection, item_name: str) -> bool:
    query = """
        SELECT notified_at
        FROM notifications
        WHERE item_name = ?
    """
    async with db.execute(query, (item_name,)) as cur:
        row = await cur.fetchone()

    if not row:
        return False

    notified_at = datetime.fromisoformat(row[0])
    cooldown = timedelta(minutes=NOTIFY_COOLDOWN_MINUTES)

    return datetime.now(UTC) - notified_at < cooldown


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


async def fetch_all(query: str, params: tuple = ()) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await db.execute_fetchall(query, params)
        return [dict(row) for row in rows]


async def execute(query: str, params: Iterable = ()) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(query, params)
        await db.commit()


async def add_watchlist_item(url: str) -> WatchlistItem:
    app_id, item_name = parse_steam_market_url(url)

    await execute(
        """
        INSERT OR IGNORE INTO watchlist (app_id, item_name)
        VALUES (?, ?)
        """,
        (app_id, item_name),
    )

    return WatchlistItem(
        app_id=app_id,
        item_name=item_name,
    )


async def fetch_watchlist() -> list[WatchlistItem]:
    rows = await fetch_all(
        """
        SELECT app_id, item_name
        FROM watchlist
        ORDER BY created_at ASC
        """
    )

    return [
        WatchlistItem(
            app_id=row["app_id"],
            item_name=row["item_name"],
        )
        for row in rows
    ]
