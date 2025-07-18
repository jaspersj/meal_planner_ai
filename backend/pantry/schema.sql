-- backend/pantry/schema.sql
CREATE TABLE IF NOT EXISTS pantry_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  quantity REAL NOT NULL DEFAULT 0,
  unit TEXT,
  expires_at DATE
);