import json
import sqlite3
from pathlib import Path


class LocalBuffer:
    def __init__(self):
        db_path = Path.home() / ".trialforge_buffer.db"
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS batches (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              payload TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'pending'
            )
            """
        )
        self.conn.commit()

    def push(self, batch: dict):
        self.conn.execute("INSERT INTO batches (payload, status) VALUES (?, 'pending')", (json.dumps(batch),))
        self.conn.commit()

    def flush(self) -> list[dict]:
        rows = self.conn.execute("SELECT id, payload FROM batches WHERE status = 'pending'").fetchall()
        ids = [row[0] for row in rows]
        if ids:
            placeholders = ",".join("?" for _ in ids)
            self.conn.execute(f"UPDATE batches SET status = 'flushing' WHERE id IN ({placeholders})", ids)
            self.conn.commit()
        return [{"id": row[0], "payload": json.loads(row[1])} for row in rows]

    def ack(self, ids: list):
        if not ids:
            return
        placeholders = ",".join("?" for _ in ids)
        self.conn.execute(f"DELETE FROM batches WHERE id IN ({placeholders})", ids)
        self.conn.commit()

    def nack(self, ids: list):
        if not ids:
            return
        placeholders = ",".join("?" for _ in ids)
        self.conn.execute(f"UPDATE batches SET status = 'pending' WHERE id IN ({placeholders})", ids)
        self.conn.commit()
