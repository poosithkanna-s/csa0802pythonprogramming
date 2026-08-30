"""SQLite persistence layer for bins and their fill-level readings."""

import sqlite3
from typing import List, Optional, Tuple

from .models import Bin


class WasteDatabase:
    """Wraps sqlite3 to store and query bins and readings.

    Usage:
        db = WasteDatabase("waste.db")
        db.insert_bin(some_bin)
        db.insert_readings(readings)
        latest = db.latest_readings()
    """

    def __init__(self, path: str = "waste.db"):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS bins (
                bin_id INTEGER PRIMARY KEY,
                x REAL NOT NULL,
                y REAL NOT NULL,
                capacity_l INTEGER NOT NULL
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS readings (
                reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bin_id INTEGER NOT NULL,
                fill_pct REAL NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (bin_id) REFERENCES bins(bin_id)
            )"""
        )
        self.conn.commit()

    def insert_bin(self, b: Bin) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO bins (bin_id, x, y, capacity_l) VALUES (?,?,?,?)",
            (b.bin_id, b.x, b.y, b.capacity_l),
        )
        self.conn.commit()

    def insert_bins(self, bins: List[Bin]) -> None:
        self.conn.executemany(
            "INSERT OR REPLACE INTO bins (bin_id, x, y, capacity_l) VALUES (?,?,?,?)",
            [(b.bin_id, b.x, b.y, b.capacity_l) for b in bins],
        )
        self.conn.commit()

    def insert_readings(self, readings: List[Tuple[int, float, str]]) -> None:
        self.conn.executemany(
            "INSERT INTO readings (bin_id, fill_pct, timestamp) VALUES (?,?,?)",
            readings,
        )
        self.conn.commit()

    def latest_readings(self) -> List[Tuple[int, float, str]]:
        """Return (bin_id, fill_pct, timestamp) for each bin's most recent reading."""
        cur = self.conn.execute(
            """
            SELECT r.bin_id, r.fill_pct, r.timestamp
            FROM readings r
            INNER JOIN (
                SELECT bin_id, MAX(timestamp) AS max_ts
                FROM readings
                GROUP BY bin_id
            ) latest ON r.bin_id = latest.bin_id AND r.timestamp = latest.max_ts
            ORDER BY r.bin_id
            """
        )
        return cur.fetchall()

    def history_for_bin(self, bin_id: int) -> List[Tuple[float, str]]:
        """Return (fill_pct, timestamp) history for a single bin, oldest first."""
        cur = self.conn.execute(
            "SELECT fill_pct, timestamp FROM readings WHERE bin_id = ? ORDER BY timestamp ASC",
            (bin_id,),
        )
        return cur.fetchall()

    def get_bin(self, bin_id: int) -> Optional[Tuple[int, float, float, int]]:
        cur = self.conn.execute(
            "SELECT bin_id, x, y, capacity_l FROM bins WHERE bin_id = ?", (bin_id,)
        )
        return cur.fetchone()

    def all_bins(self) -> List[Tuple[int, float, float, int]]:
        cur = self.conn.execute("SELECT bin_id, x, y, capacity_l FROM bins ORDER BY bin_id")
        return cur.fetchall()

    def close(self) -> None:
        self.conn.close()
