from datetime import UTC, datetime, timedelta
from typing import Iterable

import aiosqlite

from core.env import DB_PATH, NOTIFY_COOLDOWN_MINUTES
from core.models import FlipEvaluation, FlipOpportunity, WatchlistItem
from core.utils import parse_steam_market_url


class Database:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db
        self.db.row_factory = aiosqlite.Row

    # -------------------------
    # context manager
    # -------------------------

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.db.commit()

    # -------------------------
    # lifecycle
    # -------------------------

    @staticmethod
    async def init() -> None:
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
                    notified_at DATETIME NOT NULL,
                    PRIMARY KEY (item_name)
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

    # -------------------------
    # generic helpers
    # -------------------------

    async def fetch_all(self, query: str, params: Iterable = ()) -> list[dict]:
        async with self.db.execute(query, params) as cur:
            rows = await cur.fetchall()
            return [dict(row) for row in rows]

    async def fetch_one(self, query: str, params: Iterable = ()) -> dict | None:
        async with self.db.execute(query, params) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def execute(self, query: str, params: Iterable = ()) -> None:
        await self.db.execute(query, params)

    async def commit(self) -> None:
        await self.db.commit()

    # -------------------------
    # notifications
    # -------------------------

    async def already_notified(self, item_name: str) -> bool:
        row = await self.fetch_one(
            """
            SELECT notified_at
            FROM notifications
            WHERE item_name = ?
            """,
            (item_name,),
        )

        if row is None:
            return False

        notified_at = datetime.fromisoformat(row["notified_at"])
        cooldown = timedelta(minutes=NOTIFY_COOLDOWN_MINUTES)

        return datetime.now(UTC) - notified_at < cooldown

    async def mark_notified(self, item_name: str) -> None:
        await self.execute(
            """
            INSERT INTO notifications (item_name, notified_at)
            VALUES (?, ?)
            ON CONFLICT(item_name)
            DO UPDATE SET notified_at = excluded.notified_at
            """,
            (item_name, datetime.now(UTC).isoformat()),
        )

    # -------------------------
    # opportunities
    # -------------------------

    async def save_opportunity(
        self,
        flip: FlipOpportunity,
        evaluation: FlipEvaluation,
    ) -> None:
        await self.execute(
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
                (evaluation.reject_reason.value if evaluation.reject_reason else None),
                datetime.now(UTC),
            ),
        )

    # -------------------------
    # watchlist
    # -------------------------

    async def add_watchlist_item(self, url: str) -> WatchlistItem:
        app_id, item_name = parse_steam_market_url(url)

        await self.execute(
            """
            INSERT OR IGNORE INTO watchlist (app_id, item_name)
            VALUES (?, ?)
            """,
            (app_id, item_name),
        )

        return WatchlistItem(app_id=app_id, item_name=item_name)

    async def fetch_watchlist(self) -> list[WatchlistItem]:
        rows = await self.fetch_all(
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
