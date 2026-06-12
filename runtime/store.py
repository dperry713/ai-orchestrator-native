# runtime/store.py
import aiosqlite
import json
from datetime import datetime

DB_PATH = "model_runner.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            graph TEXT,
            result TEXT
        )
        """)
        await db.commit()

async def save_run(graph: dict, result: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO runs (timestamp, graph, result) VALUES (?, ?, ?)",
            (
                datetime.utcnow().isoformat(),
                json.dumps(graph),
                json.dumps(result),
            ),
        )
        await db.commit()