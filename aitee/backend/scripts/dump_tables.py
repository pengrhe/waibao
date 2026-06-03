"""Quick check: list SQLite tables in current DB."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

db = Path(__file__).resolve().parent.parent / "aitee.db"
if not db.exists():
    print(f"db not found: {db}")
    sys.exit(1)

con = sqlite3.connect(str(db))
rows = con.execute("select name from sqlite_master where type='table' order by name").fetchall()
print(f"tables_count: {len(rows)}")
for r in rows:
    print(f" - {r[0]}")
