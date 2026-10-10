"""Founder-root authentication for the local ORBIT dashboard."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from memory import connect, now

PBKDF2_ROUNDS = 310_000
SESSION_HOURS = 12

def initialise_auth():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS founder_account(
            id INTEGER PRIMARY KEY CHECK(id=1), username TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL)""")
        db.execute("""CREATE TABLE IF NOT EXISTS auth_sessions(
            token_hash TEXT PRIMARY KEY, username TEXT NOT NULL,
            expires_at TEXT NOT NULL, created_at TEXT NOT NULL, last_seen TEXT NOT NULL)""")

def founder_exists() -> bool:
    initialise_auth()
    with connect() as db:
        return db.execute("SELECT 1 FROM founder_account WHERE id=1").fetchone() is not None

def _password_hash(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS).hex()

def setup_founder(username: str, password: str) -> None:
    initialise_auth()
    username=username.strip()
    if len(username)<3 or len(username)>64:
        raise ValueError("Username must be between 3 and 64 characters.")
    if len(password)<12 or len(password)>256:
        raise ValueError("Founder password must be at least 12 characters.")
    salt=secrets.token_bytes(16)
    with connect() as db:
        if db.execute("SELECT 1 FROM founder_account WHERE id=1").fetchone():
            raise ValueError("Founder account is already configured. Use login.")
        db.execute("INSERT INTO founder_account(id,username,salt,password_hash,created_at) VALUES(1,?,?,?,?)",
                   (username,salt.hex(),_password_hash(password,salt),now()))

def create_session(username: str, password: str) -> tuple[str, str] | None:
    initialise_auth()
    with connect() as db:
        row=db.execute("SELECT username,salt,password_hash FROM founder_account WHERE id=1").fetchone()
    if not row or not secrets.compare_digest(row["username"],username.strip()):
        return None
    salt=bytes.fromhex(row["salt"])
    if not secrets.compare_digest(row["password_hash"],_password_hash(password,salt)):
        return None
    token=secrets.token_urlsafe(32)
    token_hash=hashlib.sha256(token.encode()).hexdigest()
    created=datetime.now(timezone.utc)
    expires=(created+timedelta(hours=SESSION_HOURS)).isoformat()
    with connect() as db:
        db.execute("INSERT INTO auth_sessions(token_hash,username,expires_at,created_at,last_seen) VALUES(?,?,?,?,?)",
                   (token_hash,row["username"],expires,created.isoformat(),created.isoformat()))
    return token,row["username"]

def authenticate(token: str | None) -> str | None:
    if not token:
        return None
    token_hash=hashlib.sha256(token.encode()).hexdigest()
    with connect() as db:
        row=db.execute("SELECT username,expires_at FROM auth_sessions WHERE token_hash=?",(token_hash,)).fetchone()
        if not row:
            return None
        if row["expires_at"] <= now():
            db.execute("DELETE FROM auth_sessions WHERE token_hash=?",(token_hash,))
            return None
        db.execute("UPDATE auth_sessions SET last_seen=? WHERE token_hash=?",(now(),token_hash))
        return row["username"]

def revoke_session(token: str | None) -> None:
    if not token:
        return
    token_hash=hashlib.sha256(token.encode()).hexdigest()
    with connect() as db:
        db.execute("DELETE FROM auth_sessions WHERE token_hash=?",(token_hash,))
