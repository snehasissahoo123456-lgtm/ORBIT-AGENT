import json
import sqlite3
from datetime import datetime, timezone
from config import settings


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect():
    db = sqlite3.connect(settings.database, timeout=10)
    db.row_factory = sqlite3.Row
    return db


def initialise():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL,
            content TEXT NOT NULL, created_at TEXT NOT NULL)""")
        db.execute("""CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT, goal TEXT NOT NULL,
            state TEXT NOT NULL, plan_json TEXT NOT NULL,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
        db.execute("""CREATE TABLE IF NOT EXISTS audit_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
            detail TEXT NOT NULL, created_at TEXT NOT NULL)""")


def add_message(role: str, content: str):
    with connect() as db:
        db.execute("INSERT INTO messages(role,content,created_at) VALUES(?,?,?)",
                   (role, content[:20000], now()))


def get_messages(limit: int = 30):
    with connect() as db:
        rows = db.execute("SELECT role,content,created_at FROM messages ORDER BY id DESC LIMIT ?",
                          (max(1, min(limit, 100)),)).fetchall()
    return [dict(r) for r in reversed(rows)]


def create_task(goal: str, state: str, plan: dict) -> int:
    timestamp = now()
    with connect() as db:
        cur = db.execute("INSERT INTO tasks(goal,state,plan_json,created_at,updated_at) VALUES(?,?,?,?,?)",
                         (goal, state, json.dumps(plan, ensure_ascii=False), timestamp, timestamp))
        task_id = cur.lastrowid
    audit("task_created", f"id={task_id}; goal={goal[:400]}")
    return int(task_id)


def get_tasks(limit: int = 30):
    with connect() as db:
        rows = db.execute("SELECT id,goal,state,created_at,updated_at FROM tasks ORDER BY id DESC LIMIT ?",
                          (max(1, min(limit, 100)),)).fetchall()
    return [dict(r) for r in rows]


def audit(event: str, detail: str):
    with connect() as db:
        db.execute("INSERT INTO audit_log(event,detail,created_at) VALUES(?,?,?)",
                   (event[:100], detail.replace("\\n", " ")[:2000], now()))


def get_audit(limit: int = 50):
    with connect() as db:
        rows = db.execute("SELECT event,detail,created_at FROM audit_log ORDER BY id DESC LIMIT ?",
                          (max(1, min(limit, 200)),)).fetchall()
    return [dict(r) for r in rows]
