import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'app.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(	"""
		CREATE TABLE IF NOT EXISTS log_analyses (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			raw_log TEXT NOT NULL,
			line_count INTEGER NOT NULL,
			timestamp TEXT,
			severity TEXT NOT NULL,
			component TEXT NOT NULL,
			category TEXT NOT NULL,
			confidence REAL NOT NULL,
			suggested_actions TEXT NOT NULL,
			commands_to_check TEXT NOT NULL,
			analyzed_lines TEXT NOT NULL,
			created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
		)
		""")
    conn.commit()
    conn.close()