"""SQLite storage for notes."""
import sqlite3
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    archived INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL
);
"""


def connect(path: str = "notes.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def add_note(conn, owner: str, title: str, body: str = "") -> int:
    cur = conn.execute(
        "INSERT INTO notes (owner, title, body, created_at) VALUES (?, ?, ?, ?)",
        (owner, title, body, time.time()))
    conn.commit()
    return cur.lastrowid


def list_notes(conn, owner: str, archived: bool = False) -> list[dict]:
    rows = conn.execute(
        "SELECT id, title, body, archived, created_at FROM notes "
        "WHERE owner = ? AND archived = ? ORDER BY created_at DESC, id DESC",
        (owner, int(archived)))
    return [dict(r) for r in rows]


def archive_note(conn, owner: str, note_id: int) -> bool:
    cur = conn.execute("UPDATE notes SET archived = 1 WHERE id = ? AND owner = ?",
                       (note_id, owner))
    conn.commit()
    return cur.rowcount == 1
