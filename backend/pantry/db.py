# backend/pantry/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "pantry.db"
DB_PATH.parent.mkdir(exist_ok=True)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as c:
        c.executescript(Path(__file__).with_name("schema.sql").read_text())

def list_items():
    with get_conn() as c:
        return c.execute("SELECT * FROM pantry_items").fetchall()

def add_item(name, qty, unit=None, expires_at=None):
    with get_conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO pantry_items (name, quantity, unit, expires_at) "
            "VALUES (?, COALESCE((SELECT quantity FROM pantry_items WHERE name=?),0) + ?, ?, ?)",
            (name, name, qty, unit, expires_at)
        )
        c.commit()

def update_item(name, qty=None, unit=None, expires_at=None):
    fields, params = [], []
    if qty is not None:
        fields.append("quantity=?"); params.append(qty)
    if unit is not None:
        fields.append("unit=?"); params.append(unit)
    if expires_at is not None:
        fields.append("expires_at=?"); params.append(expires_at)
    params.append(name)
    with get_conn() as c:
        c.execute(f"UPDATE pantry_items SET {','.join(fields)} WHERE name=?", params)
        c.commit()

def remove_item(name):
    with get_conn() as c:
        c.execute("DELETE FROM pantry_items WHERE name=?", (name,))
        c.commit()