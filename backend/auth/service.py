from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets

from database import get_db

PASSWORD_ITERATIONS = 310_000
TOKEN_TTL_DAYS = 7

def now_utc(): return datetime.now(timezone.utc)

def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return salt.hex(), digest.hex()

def verify_password(password, salt_hex, digest_hex):
    try: salt, expected = bytes.fromhex(salt_hex), bytes.fromhex(digest_hex)
    except (TypeError, ValueError): return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return hmac.compare_digest(actual, expected)

def token_hash(token): return hashlib.sha256(token.encode("utf-8")).hexdigest()

def public_user(row):
    return {"id": row["id"], "email": row["email"], "email_verified": bool(row["email_verified"]), "created_at": row["created_at"]}

def init_auth_db():
    conn = get_db()
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            email_verified INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS auth_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_sessions(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_auth_sessions_expires_at ON auth_sessions(expires_at)")
        conn.commit()
    finally: conn.close()

def create_user(email, password):
    salt, digest = hash_password(password)
    created_at = now_utc().isoformat(timespec="seconds")
    conn = get_db()
    try:
        conn.execute("INSERT INTO users(email,password_salt,password_hash,email_verified,created_at) VALUES(?,?,?,0,?)", (email, salt, digest, created_at))
        conn.commit()
        return public_user(conn.execute("SELECT id,email,email_verified,created_at FROM users WHERE email=?", (email,)).fetchone())
    finally: conn.close()

def authenticate_user(email, password):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not row or not verify_password(password, row["password_salt"], row["password_hash"]): return None
        return public_user(row)
    finally: conn.close()

def create_session(user_id):
    token = secrets.token_urlsafe(48)
    now = now_utc()
    expires = now + timedelta(days=TOKEN_TTL_DAYS)
    conn = get_db()
    try:
        conn.execute("INSERT INTO auth_sessions(user_id,token_hash,created_at,expires_at) VALUES(?,?,?,?)",
                     (user_id, token_hash(token), now.isoformat(timespec="seconds"), expires.isoformat(timespec="seconds")))
        conn.commit()
    finally: conn.close()
    return token, expires.isoformat(timespec="seconds")

def get_user_by_token(token):
    conn = get_db()
    try:
        row = conn.execute("""SELECT u.id,u.email,u.email_verified,u.created_at
            FROM auth_sessions s JOIN users u ON u.id=s.user_id
            WHERE s.token_hash=? AND s.expires_at>?""",
            (token_hash(token), now_utc().isoformat(timespec="seconds"))).fetchone()
        return public_user(row) if row else None
    finally: conn.close()

def revoke_session(token):
    conn = get_db()
    try:
        conn.execute("DELETE FROM auth_sessions WHERE token_hash=?", (token_hash(token),))
        conn.commit()
    finally: conn.close()
