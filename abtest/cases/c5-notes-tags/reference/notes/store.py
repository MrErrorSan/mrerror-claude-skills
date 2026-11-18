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
CREATE TABLE IF NOT EXISTS note_tags (
    note_id INTEGER NOT NULL REFERENCES notes(id),
    tag TEXT NOT NULL,
    PRIMARY KEY (note_id, tag)
);
"""
MAX_TAGS = 10


def clean_tags(tags) -> list[str]:
    out = sorted({str(t).strip().lower() for t in tags if str(t).strip()})
    if len(out) > MAX_TAGS:
        raise ValueError(f"at most {MAX_TAGS} tags per note")
    return out


def connect(path: str = "notes.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def add_note(conn, owner: str, title: str, body: str = "", tags=()) -> int:
    tags = clean_tags(tags)
    cur = conn.execute(
        "INSERT INTO notes (owner, title, body, created_at) VALUES (?, ?, ?, ?)",
        (owner, title, body, time.time()))
    conn.executemany("INSERT INTO note_tags VALUES (?, ?)", [(cur.lastrowid, t) for t in tags])
    conn.commit()
    return cur.lastrowid


def set_tags(conn, owner: str, note_id: int, tags) -> bool:
    tags = clean_tags(tags)
    if not conn.execute("SELECT 1 FROM notes WHERE id = ? AND owner = ?", (note_id, owner)).fetchone():
        return False
    conn.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
    conn.executemany("INSERT INTO note_tags VALUES (?, ?)", [(note_id, t) for t in tags])
    conn.commit()
    return True


def list_notes(conn, owner: str, archived: bool = False, tag: str | None = None) -> list[dict]:
    sql = ("SELECT id, title, body, archived, created_at FROM notes WHERE owner = ? AND archived = ?")
    params = [owner, int(archived)]
    if tag is not None:
        sql += " AND id IN (SELECT note_id FROM note_tags WHERE tag = ?)"
        params.append(tag.strip().lower())
    rows = [dict(r) for r in conn.execute(sql + " ORDER BY created_at DESC, id DESC", params)]
    for r in rows:
        r["tags"] = [t["tag"] for t in conn.execute(
            "SELECT tag FROM note_tags WHERE note_id = ? ORDER BY tag", (r["id"],))]
    return rows


def archive_note(conn, owner: str, note_id: int) -> bool:
    cur = conn.execute("UPDATE notes SET archived = 1 WHERE id = ? AND owner = ?",
                       (note_id, owner))
    conn.commit()
    return cur.rowcount == 1
