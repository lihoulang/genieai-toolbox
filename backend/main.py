"""
uni-ai-starter Backend
Production-oriented API surface for auth, chat, balance, moderation, and account deletion.
"""
import json
import os
import random
import secrets
import sqlite3
import string
import time
import hashlib
from base64 import b64decode, b64encode
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
DATE_FMT = "%Y-%m-%d"

# ===========================================
# Configuration
# ===========================================
DS_API_KEY = os.environ.get("DS_API_KEY", "")
DS_API_URL = os.environ.get("DS_API_URL", "https://api.deepseek.com/chat/completions")
DS_MODEL_NAME = os.environ.get("DS_MODEL_NAME", "deepseek-chat")

QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "")
QWEN_API_URL = os.environ.get("QWEN_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
QWEN_MODEL_NAME = os.environ.get("QWEN_MODEL_NAME", "qwen-vl-max")
QWEN_TEXT_MODEL = os.environ.get("QWEN_TEXT_MODEL", "qwen-max")

DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
DOUBAO_API_URL = os.environ.get("DOUBAO_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
DOUBAO_MODEL_NAME = os.environ.get("DOUBAO_MODEL_NAME", "doubao-seed-1-6-lite-250615")
DOUBAO_MODEL_ID_MAP_RAW = os.environ.get("DOUBAO_MODEL_ID_MAP", "")
MEMBERSHIP_CODE_MAP_RAW = os.environ.get("MEMBERSHIP_CODE_MAP", "")
GOOGLE_PLAY_SUBSCRIPTION_MAP_RAW = os.environ.get("GOOGLE_PLAY_SUBSCRIPTION_MAP", "")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_URL = os.environ.get("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions")
GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemini-2.5-flash")

DB_PATH = os.environ.get("DB_PATH", "app.db")
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))
RATE_LIMIT_MAX = int(os.environ.get("RATE_LIMIT_MAX", "30"))
SESSION_TTL_DAYS = int(os.environ.get("SESSION_TTL_DAYS", "30"))
ALLOWED_ORIGINS_RAW = os.environ.get("ALLOWED_ORIGINS", "*")
FREE_PIN_LIMIT = int(os.environ.get("FREE_PIN_LIMIT", "3"))
VIP_PIN_LIMIT = int(os.environ.get("VIP_PIN_LIMIT", "20"))
GOOGLE_PLAY_PACKAGE_NAME = os.environ.get("GOOGLE_PLAY_PACKAGE_NAME", "").strip()
GOOGLE_PLAY_SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_PLAY_SERVICE_ACCOUNT_FILE", "").strip()
GOOGLE_PLAY_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_PLAY_SERVICE_ACCOUNT_JSON", "").strip()
GOOGLE_PLAY_API_BASE = os.environ.get("GOOGLE_PLAY_API_BASE", "https://androidpublisher.googleapis.com/androidpublisher/v3")
GOOGLE_PLAY_RTDN_BEARER_TOKEN = os.environ.get("GOOGLE_PLAY_RTDN_BEARER_TOKEN", "").strip()

DEFAULT_DOUBAO_MODEL_ID_MAP = {
    "doubao-seed-1-8-251228": "ep-20260113140843-nbf4d",
    "doubao-seed-1-6-lite-251015": "ep-20260128151607-9qnld",
    "doubao-1-5-lite-32k-250115": "ep-20260128151956-wllft",
}

DEFAULT_MEMBERSHIP_CODE_MAP = {
    "DEMO30": {"days": 30, "level": 1, "label": "月度会员"},
    "DEMO365": {"days": 365, "level": 2, "label": "年度会员"},
}

DEFAULT_GOOGLE_PLAY_SUBSCRIPTION_MAP = {
    "genie.monthly": {"level": 1, "label": "Google Play 月度会员"},
    "genie.yearly": {"level": 2, "label": "Google Play 年度会员"},
}


def now_str() -> str:
    return datetime.utcnow().strftime(DATETIME_FMT)


def today_str() -> str:
    return datetime.utcnow().strftime(DATE_FMT)


def parse_dt(value: str) -> datetime:
    return datetime.strptime(value, DATETIME_FMT)


def parse_dt_safe(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return parse_dt(value)
    except ValueError:
        return None


def parse_origins(raw: str) -> list[str]:
    if not raw or raw.strip() == "*":
        return ["*"]
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_model_id_map(raw: str, fallback: dict[str, str]) -> dict[str, str]:
    if not raw.strip():
        return dict(fallback)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return {str(key): str(value) for key, value in parsed.items()}
    except json.JSONDecodeError:
        pass
    return dict(fallback)


def parse_membership_code_map(raw: str, fallback: dict[str, dict]) -> dict[str, dict]:
    if not raw.strip():
        return dict(fallback)
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            return dict(fallback)
        normalized = {}
        for code, config in parsed.items():
            if not isinstance(config, dict):
                continue
            days = int(config.get("days", 0))
            level = max(int(config.get("level", 1)), 1)
            label = str(config.get("label", "")).strip() or f"Lv{level} 会员"
            if days > 0:
                normalized[str(code).strip().upper()] = {"days": days, "level": level, "label": label}
        return normalized or dict(fallback)
    except (TypeError, ValueError, json.JSONDecodeError):
        return dict(fallback)


def parse_google_subscription_map(raw: str, fallback: dict[str, dict]) -> dict[str, dict]:
    if not raw.strip():
        return dict(fallback)
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            return dict(fallback)
        normalized = {}
        for key, config in parsed.items():
            if not isinstance(config, dict):
                continue
            level = max(int(config.get("level", 1)), 1)
            label = str(config.get("label", "")).strip() or f"Google Play Lv{level} 会员"
            normalized[str(key).strip()] = {"level": level, "label": label}
        return normalized or dict(fallback)
    except (TypeError, ValueError, json.JSONDecodeError):
        return dict(fallback)


DOUBAO_MODEL_ID_MAP = parse_model_id_map(DOUBAO_MODEL_ID_MAP_RAW, DEFAULT_DOUBAO_MODEL_ID_MAP)
MEMBERSHIP_CODE_MAP = parse_membership_code_map(MEMBERSHIP_CODE_MAP_RAW, DEFAULT_MEMBERSHIP_CODE_MAP)
GOOGLE_PLAY_SUBSCRIPTION_MAP = parse_google_subscription_map(
    GOOGLE_PLAY_SUBSCRIPTION_MAP_RAW,
    DEFAULT_GOOGLE_PLAY_SUBSCRIPTION_MAP,
)


# ===========================================
# Database
# ===========================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(cursor: sqlite3.Cursor, table_name: str, column_name: str, definition: str):
    columns = {item["name"] for item in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()}
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        balance INTEGER DEFAULT 150,
        last_sign_date TEXT,
        sign_streak INTEGER DEFAULT 0,
        nickname TEXT DEFAULT '',
        invite_code TEXT DEFAULT '',
        invited_by INTEGER DEFAULT 0,
        created_at TEXT
    )""")
    ensure_column(c, "users", "vip_level", "INTEGER DEFAULT 0")
    ensure_column(c, "users", "vip_until", "TEXT DEFAULT ''")
    ensure_column(c, "users", "vip_joined_at", "TEXT DEFAULT ''")
    ensure_column(c, "users", "vip_source", "TEXT DEFAULT ''")
    c.execute("""CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT DEFAULT '新对话',
        pinned INTEGER DEFAULT 0,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        conversation_id INTEGER DEFAULT 0,
        role TEXT NOT NULL,
        content TEXT,
        image TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS balance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount INTEGER,
        reason TEXT,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token_hash TEXT UNIQUE NOT NULL,
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        last_used_at TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS ai_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        conversation_id INTEGER DEFAULT 0,
        reason TEXT NOT NULL,
        message_content TEXT,
        created_at TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS membership_redemptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        plan_label TEXT DEFAULT '',
        vip_level INTEGER DEFAULT 1,
        granted_days INTEGER DEFAULT 0,
        granted_until TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS google_play_subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        package_name TEXT NOT NULL,
        product_id TEXT NOT NULL,
        base_plan_id TEXT DEFAULT '',
        offer_id TEXT DEFAULT '',
        purchase_token TEXT UNIQUE NOT NULL,
        linked_purchase_token TEXT DEFAULT '',
        latest_order_id TEXT DEFAULT '',
        subscription_state TEXT DEFAULT '',
        acknowledgement_state TEXT DEFAULT '',
        auto_renew_enabled INTEGER DEFAULT 0,
        expiry_time TEXT DEFAULT '',
        started_at TEXT DEFAULT '',
        is_test_purchase INTEGER DEFAULT 0,
        external_account_id TEXT DEFAULT '',
        obfuscated_external_account_id TEXT DEFAULT '',
        raw_response TEXT DEFAULT '',
        last_synced_at TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS google_play_notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        package_name TEXT DEFAULT '',
        purchase_token TEXT DEFAULT '',
        subscription_id TEXT DEFAULT '',
        notification_type INTEGER DEFAULT 0,
        payload TEXT DEFAULT '',
        created_at TEXT NOT NULL
    )""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_msg_user_conv ON messages(user_id, conversation_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_conv_user ON conversations(user_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_balance_user ON balance_logs(user_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_session_token ON user_sessions(token_hash)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_membership_redemption_code ON membership_redemptions(code)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_gp_sub_purchase_token ON google_play_subscriptions(purchase_token)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_gp_sub_user_id ON google_play_subscriptions(user_id)")
    conn.commit()
    conn.close()


init_db()


# ===========================================
# App
# ===========================================
app = FastAPI(title="uni-ai-starter API")
allowed_origins = parse_origins(ALLOWED_ORIGINS_RAW)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ===========================================
# Schemas
# ===========================================
class UserAuth(BaseModel):
    username: str
    password: str
    invite_code: str = ""


class ProfileUpdate(BaseModel):
    nickname: str = ""


class ChatRequest(BaseModel):
    user_id: int
    message: str = ""
    messages: list = Field(default_factory=list)
    image_base64: str | None = None
    conversation_id: int = 0
    model: str = "deepseek"


class AIReportRequest(BaseModel):
    user_id: int
    conversation_id: int = 0
    reason: str
    message_content: str = ""


class MembershipRedeemRequest(BaseModel):
    code: str


class GooglePlayVerifyRequest(BaseModel):
    purchase_token: str
    product_id: str = ""
    package_name: str = ""


class GooglePlaySyncRequest(BaseModel):
    purchase_token: str
    package_name: str = ""


# ===========================================
# Security
# ===========================================
def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${b64encode(salt).decode()}${b64encode(derived).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    if stored_hash.startswith("scrypt$"):
        try:
            _, salt_b64, digest_b64 = stored_hash.split("$", 2)
            salt = b64decode(salt_b64.encode())
            expected = b64decode(digest_b64.encode())
            actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
            return secrets.compare_digest(actual, expected)
        except Exception:
            return False

    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return secrets.compare_digest(legacy, stored_hash)


def maybe_upgrade_password(conn: sqlite3.Connection, user_id: int, password: str, stored_hash: str):
    if stored_hash.startswith("scrypt$"):
        return
    if verify_password(password, stored_hash):
        conn.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(password), user_id))
        conn.commit()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(user_id: int) -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=SESSION_TTL_DAYS)
    expires_at_str = expires_at.strftime(DATETIME_FMT)
    conn = get_db()
    conn.execute(
        "INSERT INTO user_sessions (user_id, token_hash, expires_at, created_at, last_used_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, hash_token(token), expires_at_str, now_str(), now_str()),
    )
    conn.commit()
    conn.close()
    return token, expires_at_str


def revoke_token(token: str):
    conn = get_db()
    conn.execute("DELETE FROM user_sessions WHERE token_hash = ?", (hash_token(token),))
    conn.commit()
    conn.close()


def get_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "").strip()
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或登录已失效")
    token = auth[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="未登录或登录已失效")
    return token


def require_user(request: Request) -> int:
    token = get_bearer_token(request)
    token_hash = hash_token(token)
    conn = get_db()
    row = conn.execute(
        "SELECT user_id, expires_at FROM user_sessions WHERE token_hash = ?",
        (token_hash,),
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=401, detail="登录态失效，请重新登录")

    expires_at = parse_dt(row["expires_at"])
    if expires_at <= datetime.utcnow():
        conn.execute("DELETE FROM user_sessions WHERE token_hash = ?", (token_hash,))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")

    conn.execute(
        "UPDATE user_sessions SET last_used_at = ? WHERE token_hash = ?",
        (now_str(), token_hash),
    )
    conn.commit()
    conn.close()
    return int(row["user_id"])


def enforce_self(request: Request, expected_user_id: int) -> int:
    authed_user_id = require_user(request)
    if authed_user_id != expected_user_id:
        raise HTTPException(status_code=403, detail="无权访问其他用户数据")
    return authed_user_id


def ensure_conversation_owner(conv_id: int, user_id: int):
    conn = get_db()
    row = conn.execute("SELECT user_id FROM conversations WHERE id = ?", (conv_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="会话不存在")
    if int(row["user_id"]) != user_id:
        raise HTTPException(status_code=403, detail="无权操作该会话")


# ===========================================
# Domain helpers
# ===========================================
def generate_invite_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def get_vip_name(level: int) -> str:
    if level >= 2:
        return "年度会员"
    if level >= 1:
        return "月度会员"
    return "普通用户"


def build_membership_payload(level: int, vip_until: str) -> dict:
    expires_at = parse_dt_safe(vip_until)
    active = bool(level > 0 and expires_at and expires_at > datetime.utcnow())
    effective_level = level if active else 0
    return {
        "vip_level": effective_level,
        "vip_active": active,
        "vip_name": get_vip_name(effective_level),
        "vip_until": vip_until if active else "",
        "pin_limit": VIP_PIN_LIMIT if active else FREE_PIN_LIMIT,
        "can_export_history": active,
    }


def get_user_membership(user_id: int) -> dict:
    conn = get_db()
    row = conn.execute("SELECT vip_level, vip_until FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="用户不存在")
    return build_membership_payload(int(row["vip_level"] or 0), row["vip_until"] or "")


def activate_membership(user_id: int, level: int, days: int, source: str, plan_label: str, code: str = "") -> dict:
    conn = get_db()
    row = conn.execute("SELECT vip_level, vip_until, vip_joined_at FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="用户不存在")

    now_dt = datetime.utcnow()
    current_until = parse_dt_safe(row["vip_until"] or "")
    base_dt = current_until if current_until and current_until > now_dt else now_dt
    new_until = (base_dt + timedelta(days=max(days, 1))).strftime(DATETIME_FMT)
    new_level = max(int(row["vip_level"] or 0), max(level, 1))

    conn.execute(
        "UPDATE users SET vip_level = ?, vip_until = ?, vip_joined_at = ?, vip_source = ? WHERE id = ?",
        (
            new_level,
            new_until,
            row["vip_joined_at"] or now_str(),
            source[:50],
            user_id,
        ),
    )
    if code:
        conn.execute(
            "INSERT INTO membership_redemptions (code, user_id, plan_label, vip_level, granted_days, granted_until, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (code, user_id, plan_label[:50], new_level, max(days, 1), new_until, now_str()),
        )
    conn.commit()
    conn.close()

    membership = build_membership_payload(new_level, new_until)
    membership["plan_label"] = plan_label
    membership["granted_days"] = max(days, 1)
    return membership


def set_membership_expiry(user_id: int, level: int, vip_until: str, source: str, plan_label: str) -> dict:
    conn = get_db()
    row = conn.execute("SELECT vip_level FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="用户不存在")
    conn.execute(
        "UPDATE users SET vip_level = ?, vip_until = ?, vip_joined_at = CASE WHEN vip_joined_at = '' THEN ? ELSE vip_joined_at END, vip_source = ? WHERE id = ?",
        (max(level, 1), vip_until, now_str(), source[:50], user_id),
    )
    conn.commit()
    conn.close()
    membership = build_membership_payload(max(level, 1), vip_until)
    membership["plan_label"] = plan_label
    return membership


def clear_google_play_membership_if_owned(user_id: int) -> None:
    conn = get_db()
    row = conn.execute("SELECT vip_source FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        return
    if not str(row["vip_source"] or "").startswith("google_play"):
        conn.close()
        return
    conn.execute(
        "UPDATE users SET vip_until = ?, vip_source = ? WHERE id = ?",
        (now_str(), "google_play_inactive", user_id),
    )
    conn.commit()
    conn.close()


def parse_google_time(value: str) -> tuple[datetime | None, str]:
    if not value:
        return None, ""
    try:
        normalized = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc.replace(tzinfo=None), dt_utc.strftime(DATETIME_FMT)
    except ValueError:
        return None, ""
    except Exception:
        return None, ""


def resolve_google_play_plan(product_id: str, base_plan_id: str = "") -> dict | None:
    if product_id and base_plan_id:
        composite = f"{product_id}:{base_plan_id}"
        if composite in GOOGLE_PLAY_SUBSCRIPTION_MAP:
            return GOOGLE_PLAY_SUBSCRIPTION_MAP[composite]
    if product_id in GOOGLE_PLAY_SUBSCRIPTION_MAP:
        return GOOGLE_PLAY_SUBSCRIPTION_MAP[product_id]
    return None


def is_google_subscription_entitled(subscription_state: str, expiry_dt: datetime | None) -> bool:
    active_states = {"SUBSCRIPTION_STATE_ACTIVE", "SUBSCRIPTION_STATE_IN_GRACE_PERIOD", "SUBSCRIPTION_STATE_CANCELED"}
    if subscription_state not in active_states:
        return False
    return bool(expiry_dt and expiry_dt > datetime.utcnow())


def require_google_play_config(package_name: str = "") -> str:
    effective_package_name = (package_name or GOOGLE_PLAY_PACKAGE_NAME).strip()
    if not effective_package_name:
        raise HTTPException(status_code=500, detail="未配置 Google Play 包名")
    if not GOOGLE_PLAY_SERVICE_ACCOUNT_FILE and not GOOGLE_PLAY_SERVICE_ACCOUNT_JSON:
        raise HTTPException(status_code=500, detail="未配置 Google Play 服务账号")
    return effective_package_name


def get_google_play_access_token() -> str:
    try:
        from google.auth.transport.requests import Request as GoogleAuthRequest
        from google.oauth2 import service_account
    except ImportError as exc:
        raise HTTPException(status_code=500, detail=f"缺少 google-auth 依赖：{exc}") from exc

    info = None
    if GOOGLE_PLAY_SERVICE_ACCOUNT_JSON:
        try:
            info = json.loads(GOOGLE_PLAY_SERVICE_ACCOUNT_JSON)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=500, detail=f"Google Play 服务账号 JSON 无效：{exc}") from exc

    try:
        if info:
            creds = service_account.Credentials.from_service_account_info(
                info,
                scopes=["https://www.googleapis.com/auth/androidpublisher"],
            )
        else:
            creds = service_account.Credentials.from_service_account_file(
                GOOGLE_PLAY_SERVICE_ACCOUNT_FILE,
                scopes=["https://www.googleapis.com/auth/androidpublisher"],
            )
        creds.refresh(GoogleAuthRequest())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"获取 Google Play access token 失败：{exc}") from exc

    if not creds.token:
        raise HTTPException(status_code=500, detail="Google Play access token 为空")
    return str(creds.token)


def google_play_request(method: str, path: str, json_body: dict | None = None) -> dict:
    access_token = get_google_play_access_token()
    url = f"{GOOGLE_PLAY_API_BASE.rstrip('/')}/{path.lstrip('/')}"
    try:
        resp = requests.request(
            method.upper(),
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            json=json_body,
            timeout=30,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Google Play 请求失败：{exc}") from exc

    if resp.status_code >= 400:
        detail = resp.text[:500]
        raise HTTPException(status_code=502, detail=f"Google Play 接口异常：HTTP {resp.status_code} {detail}")
    if not resp.text.strip():
        return {}
    try:
        return resp.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=f"Google Play 返回了非 JSON 响应：{exc}") from exc


def google_play_fetch_subscription_purchase(package_name: str, purchase_token: str) -> dict:
    return google_play_request(
        "GET",
        f"applications/{package_name}/purchases/subscriptionsv2/tokens/{purchase_token}",
    )


def google_play_acknowledge_subscription(package_name: str, product_id: str, purchase_token: str) -> None:
    if not product_id:
        return
    google_play_request(
        "POST",
        f"applications/{package_name}/purchases/subscriptions/{product_id}/tokens/{purchase_token}:acknowledge",
        json_body={},
    )


def extract_google_play_subscription_context(payload: dict, product_id_hint: str = "") -> dict:
    line_items = payload.get("lineItems") or []
    primary_item = line_items[0] if line_items else {}
    for item in line_items:
        item_expiry_dt, _ = parse_google_time(item.get("expiryTime", ""))
        current_expiry_dt, _ = parse_google_time(primary_item.get("expiryTime", ""))
        if item_expiry_dt and (not current_expiry_dt or item_expiry_dt > current_expiry_dt):
            primary_item = item

    product_id = primary_item.get("productId") or product_id_hint or ""
    offer_details = primary_item.get("offerDetails") or {}
    auto_plan = primary_item.get("autoRenewingPlan") or {}
    expiry_dt, expiry_str = parse_google_time(primary_item.get("expiryTime", ""))
    start_dt, start_str = parse_google_time(payload.get("startTime", ""))

    return {
        "subscription_state": payload.get("subscriptionState", ""),
        "acknowledgement_state": payload.get("acknowledgementState", ""),
        "purchase_token": payload.get("latestPurchaseOrderId", ""),
        "latest_order_id": payload.get("latestOrderId", "") or payload.get("latestPurchaseOrderId", ""),
        "product_id": product_id,
        "base_plan_id": offer_details.get("basePlanId", ""),
        "offer_id": offer_details.get("offerId", ""),
        "linked_purchase_token": payload.get("linkedPurchaseToken", ""),
        "auto_renew_enabled": 1 if auto_plan.get("autoRenewEnabled") else 0,
        "expiry_dt": expiry_dt,
        "expiry_str": expiry_str,
        "started_at": start_str,
        "is_test_purchase": 1 if payload.get("testPurchase") else 0,
        "external_account_id": (payload.get("externalAccountIdentifiers") or {}).get("externalAccountId", ""),
        "obfuscated_external_account_id": (payload.get("externalAccountIdentifiers") or {}).get("obfuscatedExternalAccountId", ""),
        "line_item_count": len(line_items),
    }


def upsert_google_play_subscription(user_id: int, package_name: str, purchase_token: str, purchase_payload: dict, context: dict) -> None:
    conn = get_db()
    conn.execute(
        """
        INSERT INTO google_play_subscriptions (
            user_id, package_name, product_id, base_plan_id, offer_id, purchase_token, linked_purchase_token,
            latest_order_id, subscription_state, acknowledgement_state, auto_renew_enabled, expiry_time,
            started_at, is_test_purchase, external_account_id, obfuscated_external_account_id, raw_response,
            last_synced_at, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(purchase_token) DO UPDATE SET
            user_id = excluded.user_id,
            package_name = excluded.package_name,
            product_id = excluded.product_id,
            base_plan_id = excluded.base_plan_id,
            offer_id = excluded.offer_id,
            linked_purchase_token = excluded.linked_purchase_token,
            latest_order_id = excluded.latest_order_id,
            subscription_state = excluded.subscription_state,
            acknowledgement_state = excluded.acknowledgement_state,
            auto_renew_enabled = excluded.auto_renew_enabled,
            expiry_time = excluded.expiry_time,
            started_at = excluded.started_at,
            is_test_purchase = excluded.is_test_purchase,
            external_account_id = excluded.external_account_id,
            obfuscated_external_account_id = excluded.obfuscated_external_account_id,
            raw_response = excluded.raw_response,
            last_synced_at = excluded.last_synced_at
        """,
        (
            user_id,
            package_name,
            context["product_id"],
            context["base_plan_id"],
            context["offer_id"],
            purchase_token,
            context["linked_purchase_token"],
            context["latest_order_id"],
            context["subscription_state"],
            context["acknowledgement_state"],
            context["auto_renew_enabled"],
            context["expiry_str"],
            context["started_at"],
            context["is_test_purchase"],
            context["external_account_id"],
            context["obfuscated_external_account_id"],
            json.dumps(purchase_payload, ensure_ascii=False),
            now_str(),
            now_str(),
        ),
    )
    conn.commit()
    conn.close()


def sync_google_subscription_purchase(
    user_id: int,
    purchase_token: str,
    package_name: str = "",
    product_id_hint: str = "",
    source: str = "google_play_client_verify",
) -> dict:
    purchase_token = purchase_token.strip()
    if not purchase_token:
        raise HTTPException(status_code=400, detail="purchase_token 不能为空")

    effective_package_name = require_google_play_config(package_name)
    purchase_payload = google_play_fetch_subscription_purchase(effective_package_name, purchase_token)
    context = extract_google_play_subscription_context(purchase_payload, product_id_hint=product_id_hint)
    if not context["product_id"]:
        raise HTTPException(status_code=400, detail="Google Play 返回的订阅缺少 productId")

    plan = resolve_google_play_plan(context["product_id"], context["base_plan_id"])
    if not plan:
        raise HTTPException(status_code=400, detail=f"未配置该订阅商品映射：{context['product_id']}")

    if context["acknowledgement_state"] == "ACKNOWLEDGEMENT_STATE_PENDING":
        google_play_acknowledge_subscription(effective_package_name, context["product_id"], purchase_token)
        context["acknowledgement_state"] = "ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED"

    upsert_google_play_subscription(user_id, effective_package_name, purchase_token, purchase_payload, context)

    entitled = is_google_subscription_entitled(context["subscription_state"], context["expiry_dt"])
    membership = None
    if entitled:
        membership = set_membership_expiry(
            user_id=user_id,
            level=int(plan["level"]),
            vip_until=context["expiry_str"],
            source=source,
            plan_label=str(plan["label"]),
        )
    else:
        clear_google_play_membership_if_owned(user_id)
        membership = get_user_membership(user_id)

    return {
        "package_name": effective_package_name,
        "purchase_token": purchase_token,
        "product_id": context["product_id"],
        "base_plan_id": context["base_plan_id"],
        "subscription_state": context["subscription_state"],
        "acknowledgement_state": context["acknowledgement_state"],
        "expiry_time": context["expiry_str"],
        "auto_renew_enabled": bool(context["auto_renew_enabled"]),
        "is_test_purchase": bool(context["is_test_purchase"]),
        "membership": membership,
    }


def get_google_play_subscription_owner(purchase_token: str) -> int | None:
    conn = get_db()
    row = conn.execute("SELECT user_id FROM google_play_subscriptions WHERE purchase_token = ?", (purchase_token,)).fetchone()
    conn.close()
    if not row:
        return None
    return int(row["user_id"])


def save_google_play_notification(package_name: str, purchase_token: str, subscription_id: str, notification_type: int, payload: dict) -> None:
    conn = get_db()
    conn.execute(
        """
        INSERT INTO google_play_notifications (package_name, purchase_token, subscription_id, notification_type, payload, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            package_name,
            purchase_token,
            subscription_id,
            notification_type,
            json.dumps(payload, ensure_ascii=False),
            now_str(),
        ),
    )
    conn.commit()
    conn.close()


def verify_google_play_rtdn_request(request: Request) -> None:
    if not GOOGLE_PLAY_RTDN_BEARER_TOKEN:
        return
    auth = request.headers.get("Authorization", "").strip()
    expected = f"Bearer {GOOGLE_PLAY_RTDN_BEARER_TOKEN}"
    if auth != expected:
        raise HTTPException(status_code=401, detail="RTDN 鉴权失败")



def get_user_balance(user_id: int) -> int:
    conn = get_db()
    row = conn.execute("SELECT balance FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return int(row["balance"]) if row else 0


def add_balance(user_id: int, amount: int, reason: str = "签到"):
    conn = get_db()
    conn.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
    conn.execute(
        "INSERT INTO balance_logs (user_id, amount, reason, created_at) VALUES (?, ?, ?, ?)",
        (user_id, amount, reason, now_str()),
    )
    conn.commit()
    conn.close()


def refund_balance(user_id: int, amount: int, reason: str):
    if amount <= 0:
        return
    add_balance(user_id, amount, reason)


def deduct_balance_if_enough(user_id: int, amount: int, reason: str) -> bool:
    conn = get_db()
    row = conn.execute("SELECT balance FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="用户不存在")
    if int(row["balance"]) < amount:
        conn.close()
        return False

    conn.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, user_id))
    conn.execute(
        "INSERT INTO balance_logs (user_id, amount, reason, created_at) VALUES (?, ?, ?, ?)",
        (user_id, -amount, reason, now_str()),
    )
    conn.commit()
    conn.close()
    return True


rate_limit_store = defaultdict(list)


def check_rate_limit(user_id: int) -> bool:
    now_ts = time.time()
    rate_limit_store[user_id] = [item for item in rate_limit_store[user_id] if now_ts - item < RATE_LIMIT_WINDOW]
    if len(rate_limit_store[user_id]) >= RATE_LIMIT_MAX:
        return True
    rate_limit_store[user_id].append(now_ts)
    return False


def normalize_chat_role(role: str) -> str:
    if role == "ai":
        return "assistant"
    return role


def normalize_qwen_api_url(url: str) -> str:
    normalized = (url or "").rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    if normalized.endswith("/compatible-mode/v1"):
        return f"{normalized}/chat/completions"
    if normalized.endswith("/api/v3"):
        return f"{normalized}/chat/completions"
    if normalized.endswith("/openai"):
        return f"{normalized}/chat/completions"
    return normalized


def resolve_qwen_vision_model(model_name: str) -> str:
    lowered = (model_name or "").lower()
    if "vl" in lowered or "omni" in lowered:
        return model_name
    return os.environ.get("QWEN_VISION_FALLBACK", "qwen-vl-max")


def resolve_doubao_model(model_name: str) -> str:
    return DOUBAO_MODEL_ID_MAP.get(model_name, model_name)


def resolve_text_model_config(model_name: str) -> tuple[str, str, str, str]:
    if model_name == "qwen":
        return normalize_qwen_api_url(QWEN_API_URL), QWEN_API_KEY, QWEN_TEXT_MODEL, "Qwen"
    if model_name == "doubao":
        return normalize_qwen_api_url(DOUBAO_API_URL), DOUBAO_API_KEY, resolve_doubao_model(DOUBAO_MODEL_NAME), "豆包"
    if model_name == "gemini":
        return normalize_qwen_api_url(GEMINI_API_URL), GEMINI_API_KEY, GEMINI_MODEL_NAME, "Gemini"
    return DS_API_URL, DS_API_KEY, DS_MODEL_NAME, "DeepSeek"


# ===========================================
# Public auth routes
# ===========================================
@app.post("/register")
async def register(user: UserAuth):
    username = user.username.strip()
    password = user.password
    invite_code = user.invite_code.strip().upper()

    if len(username) < 2:
        return {"code": 400, "msg": "用户名至少2个字符"}
    if len(password) < 6:
        return {"code": 400, "msg": "密码至少6位"}

    conn = get_db()
    try:
        code = generate_invite_code()
        conn.execute(
            "INSERT INTO users (username, password, balance, invite_code, created_at) VALUES (?, ?, 150, ?, ?)",
            (username, hash_password(password), code, now_str()),
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()

        if invite_code:
            inviter = conn.execute(
                "SELECT id FROM users WHERE invite_code = ? AND id != ?",
                (invite_code, new_id),
            ).fetchone()
            if inviter:
                conn.execute("UPDATE users SET invited_by = ? WHERE id = ?", (inviter["id"], new_id))
                conn.commit()
                conn.close()
                add_balance(inviter["id"], 100, f"邀请好友({username})")
                add_balance(new_id, 50, "受邀奖励")
                return {"code": 200, "msg": "注册成功！邀请奖励已发放"}

        conn.close()
        return {"code": 200, "msg": "注册成功！"}
    except sqlite3.IntegrityError:
        conn.close()
        return {"code": 400, "msg": "用户名已存在"}


@app.post("/login")
async def login(user: UserAuth):
    username = user.username.strip()
    conn = get_db()
    row = conn.execute("SELECT id, password FROM users WHERE username = ?", (username,)).fetchone()
    if not row or not verify_password(user.password, row["password"]):
        conn.close()
        return {"code": 401, "msg": "认证失败"}

    maybe_upgrade_password(conn, int(row["id"]), user.password, row["password"])
    conn.close()
    access_token, expires_at = create_session(int(row["id"]))
    return {
        "code": 200,
        "user_id": int(row["id"]),
        "access_token": access_token,
        "expires_at": expires_at,
    }


@app.post("/logout")
async def logout(request: Request):
    token = get_bearer_token(request)
    revoke_token(token)
    return {"code": 200, "msg": "已退出登录"}


# ===========================================
# User routes
# ===========================================
@app.get("/user/info/{user_id}")
async def get_user_info(user_id: int, request: Request):
    enforce_self(request, user_id)
    conn = get_db()
    row = conn.execute(
        "SELECT username, balance, last_sign_date, nickname, invite_code, sign_streak, vip_level, vip_until FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    if not row:
        return {"code": 404}
    membership = build_membership_payload(int(row["vip_level"] or 0), row["vip_until"] or "")
    return {
        "code": 200,
        "username": row["username"],
        "balance": int(row["balance"]),
        "has_signed_today": row["last_sign_date"] == today_str(),
        "nickname": row["nickname"] or "",
        "invite_code": row["invite_code"] or "",
        "sign_streak": int(row["sign_streak"] or 0),
        **membership,
    }


@app.post("/user/sign/{user_id}")
async def daily_sign(user_id: int, request: Request):
    enforce_self(request, user_id)
    conn = get_db()
    row = conn.execute("SELECT last_sign_date, sign_streak FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        return {"code": 404, "msg": "用户不存在"}
    if row["last_sign_date"] == today_str():
        conn.close()
        return {"code": 400, "msg": "今天已经签到过了"}

    old_streak = int(row["sign_streak"] or 0)
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime(DATE_FMT)
    new_streak = (old_streak + 1) if row["last_sign_date"] == yesterday else 1
    bonus = min(50 + (new_streak - 1) * 5, 100)
    conn.execute(
        "UPDATE users SET last_sign_date = ?, sign_streak = ? WHERE id = ?",
        (today_str(), new_streak, user_id),
    )
    conn.commit()
    conn.close()
    add_balance(user_id, bonus, f"连续签到第{new_streak}天")
    return {"code": 200, "msg": f"连签第{new_streak}天！算力 +{bonus}", "streak": new_streak, "bonus": bonus}


@app.get("/user/balance/{user_id}")
async def get_balance(user_id: int, request: Request):
    enforce_self(request, user_id)
    return {"code": 200, "balance": get_user_balance(user_id)}


@app.get("/user/balance_logs/{user_id}")
async def get_balance_logs(user_id: int, request: Request):
    enforce_self(request, user_id)
    conn = get_db()
    rows = conn.execute(
        "SELECT amount, reason, created_at FROM balance_logs WHERE user_id = ? ORDER BY id DESC LIMIT 50",
        (user_id,),
    ).fetchall()
    conn.close()
    return {
        "code": 200,
        "data": [{"amount": int(item["amount"]), "reason": item["reason"], "created_at": item["created_at"]} for item in rows],
    }


@app.post("/membership/redeem/{user_id}")
async def redeem_membership(user_id: int, request: Request, payload: MembershipRedeemRequest):
    enforce_self(request, user_id)
    code = payload.code.strip().upper()
    if not code:
        return {"code": 400, "msg": "请输入兑换码"}

    plan = MEMBERSHIP_CODE_MAP.get(code)
    if not plan:
        return {"code": 400, "msg": "兑换码无效"}

    conn = get_db()
    used = conn.execute("SELECT user_id FROM membership_redemptions WHERE code = ?", (code,)).fetchone()
    conn.close()
    if used:
        return {"code": 400, "msg": "兑换码已使用"}

    membership = activate_membership(
        user_id=user_id,
        level=int(plan["level"]),
        days=int(plan["days"]),
        source="redeem_code",
        plan_label=str(plan["label"]),
        code=code,
    )
    return {
        "code": 200,
        "msg": f"{membership['plan_label']}已开通，有效期至 {membership['vip_until']}",
        **membership,
    }


@app.get("/billing/google-play/products")
async def get_google_play_products():
    return {
        "code": 200,
        "package_name": GOOGLE_PLAY_PACKAGE_NAME,
        "products": [
            {"product_id": product_id, "vip_level": int(config["level"]), "label": str(config["label"])}
            for product_id, config in GOOGLE_PLAY_SUBSCRIPTION_MAP.items()
        ],
    }


@app.post("/billing/google-play/subscription/verify/{user_id}")
async def verify_google_play_subscription(user_id: int, request: Request, payload: GooglePlayVerifyRequest):
    enforce_self(request, user_id)
    result = sync_google_subscription_purchase(
        user_id=user_id,
        purchase_token=payload.purchase_token,
        package_name=payload.package_name,
        product_id_hint=payload.product_id,
        source="google_play_verify",
    )
    return {"code": 200, "msg": "Google Play 订阅校验成功", **result}


@app.post("/billing/google-play/subscription/sync/{user_id}")
async def sync_google_play_subscription(user_id: int, request: Request, payload: GooglePlaySyncRequest):
    enforce_self(request, user_id)
    result = sync_google_subscription_purchase(
        user_id=user_id,
        purchase_token=payload.purchase_token,
        package_name=payload.package_name,
        source="google_play_sync",
    )
    return {"code": 200, "msg": "Google Play 订阅已同步", **result}


@app.get("/billing/google-play/subscriptions/{user_id}")
async def list_google_play_subscriptions(user_id: int, request: Request):
    enforce_self(request, user_id)
    conn = get_db()
    rows = conn.execute(
        """
        SELECT product_id, base_plan_id, purchase_token, latest_order_id, subscription_state,
               acknowledgement_state, auto_renew_enabled, expiry_time, last_synced_at
        FROM google_play_subscriptions
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return {
        "code": 200,
        "data": [
            {
                "product_id": row["product_id"],
                "base_plan_id": row["base_plan_id"] or "",
                "purchase_token": row["purchase_token"],
                "latest_order_id": row["latest_order_id"] or "",
                "subscription_state": row["subscription_state"] or "",
                "acknowledgement_state": row["acknowledgement_state"] or "",
                "auto_renew_enabled": bool(row["auto_renew_enabled"]),
                "expiry_time": row["expiry_time"] or "",
                "last_synced_at": row["last_synced_at"] or "",
            }
            for row in rows
        ],
    }


@app.post("/billing/google-play/rtdn")
async def handle_google_play_rtdn(request: Request):
    verify_google_play_rtdn_request(request)
    payload = await request.json()
    message = payload.get("message") if isinstance(payload, dict) else None
    if isinstance(message, dict) and message.get("data"):
        try:
            decoded = b64decode(message["data"]).decode("utf-8")
            payload = json.loads(decoded)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"RTDN data 解析失败：{exc}") from exc

    subscription_notice = payload.get("subscriptionNotification") or {}
    purchase_token = subscription_notice.get("purchaseToken", "")
    subscription_id = subscription_notice.get("subscriptionId", "")
    notification_type = int(subscription_notice.get("notificationType", 0) or 0)
    package_name = payload.get("packageName", "") or GOOGLE_PLAY_PACKAGE_NAME

    save_google_play_notification(package_name, purchase_token, subscription_id, notification_type, payload)

    owner_user_id = get_google_play_subscription_owner(purchase_token) if purchase_token else None
    if owner_user_id:
        sync_google_subscription_purchase(
            user_id=owner_user_id,
            purchase_token=purchase_token,
            package_name=package_name,
            product_id_hint=subscription_id,
            source="google_play_rtdn",
        )
    return {"code": 200, "msg": "RTDN 已接收", "known_purchase": bool(owner_user_id)}


@app.post("/user/update_profile/{user_id}")
async def update_profile(user_id: int, request: Request, data: ProfileUpdate):
    enforce_self(request, user_id)
    nickname = data.nickname.strip()[:20]
    conn = get_db()
    conn.execute("UPDATE users SET nickname = ? WHERE id = ?", (nickname, user_id))
    conn.commit()
    conn.close()
    return {"code": 200, "msg": "更新成功"}


@app.delete("/user/account/{user_id}")
async def delete_account(user_id: int, request: Request):
    enforce_self(request, user_id)
    token = get_bearer_token(request)
    conn = get_db()
    conn.execute("DELETE FROM ai_reports WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM balance_logs WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    revoke_token(token)
    return {"code": 200, "msg": "账号及相关数据已删除"}


# ===========================================
# Conversations
# ===========================================
@app.post("/conversation/create/{user_id}")
async def create_conversation(user_id: int, request: Request):
    enforce_self(request, user_id)
    conn = get_db()
    conn.execute(
        "INSERT INTO conversations (user_id, title, created_at) VALUES (?, ?, ?)",
        (user_id, "新对话", datetime.utcnow().strftime("%Y-%m-%d %H:%M")),
    )
    conv_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.close()
    return {"code": 200, "conversation_id": conv_id}


@app.get("/conversations/{user_id}")
async def get_conversations(user_id: int, request: Request):
    enforce_self(request, user_id)
    conn = get_db()
    rows = conn.execute(
        "SELECT id, title, created_at, pinned FROM conversations WHERE user_id = ? ORDER BY pinned DESC, id DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return {
        "code": 200,
        "data": [
            {"id": int(item["id"]), "title": item["title"], "created_at": item["created_at"], "pinned": int(item["pinned"] or 0)}
            for item in rows
        ],
    }


@app.put("/conversation/pin/{conv_id}")
async def toggle_pin(conv_id: int, request: Request):
    user_id = require_user(request)
    ensure_conversation_owner(conv_id, user_id)
    conn = get_db()
    row = conn.execute("SELECT pinned FROM conversations WHERE id = ?", (conv_id,)).fetchone()
    new_val = 0 if (row and row["pinned"]) else 1
    membership = get_user_membership(user_id)
    if new_val == 1:
        pinned_total = int(
            conn.execute("SELECT COUNT(*) AS total FROM conversations WHERE user_id = ? AND pinned = 1", (user_id,)).fetchone()["total"]
        )
        if pinned_total >= membership["pin_limit"]:
            conn.close()
            return {
                "code": 400,
                "msg": f"当前最多可置顶 {membership['pin_limit']} 个会话，开通会员可提升到 {VIP_PIN_LIMIT} 个。",
            }
    conn.execute("UPDATE conversations SET pinned = ? WHERE id = ?", (new_val, conv_id))
    conn.commit()
    conn.close()
    return {"code": 200, "pinned": new_val}


@app.delete("/conversation/{conv_id}")
async def delete_conversation(conv_id: int, request: Request):
    user_id = require_user(request)
    ensure_conversation_owner(conv_id, user_id)
    conn = get_db()
    conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
    conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
    conn.commit()
    conn.close()
    return {"code": 200, "msg": "已删除"}


# ===========================================
# History
# ===========================================
@app.get("/history/{user_id}")
async def get_history(user_id: int, request: Request, conversation_id: int = 0, limit: int = 50, offset: int = 0):
    enforce_self(request, user_id)
    if conversation_id:
        ensure_conversation_owner(conversation_id, user_id)

    conn = get_db()
    total = conn.execute(
        "SELECT COUNT(*) AS total FROM messages WHERE user_id = ? AND conversation_id = ?",
        (user_id, conversation_id),
    ).fetchone()["total"]

    if offset == 0 and total > limit:
        rows = list(reversed(conn.execute(
            "SELECT role, content, image FROM messages WHERE user_id = ? AND conversation_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, conversation_id, limit),
        ).fetchall()))
    else:
        rows = conn.execute(
            "SELECT role, content, image FROM messages WHERE user_id = ? AND conversation_id = ? ORDER BY id ASC LIMIT ? OFFSET ?",
            (user_id, conversation_id, limit, offset),
        ).fetchall()
    conn.close()

    return {
        "code": 200,
        "data": [{"role": normalize_chat_role(item["role"]), "content": item["content"], "image": item["image"]} for item in rows],
        "total": int(total),
    }


@app.get("/history/export/{user_id}")
async def export_history(user_id: int, request: Request, conversation_id: int = 0):
    enforce_self(request, user_id)
    membership = get_user_membership(user_id)
    if not membership["can_export_history"]:
        return {"code": 403, "msg": "导出功能为会员专属权益"}
    if conversation_id:
        ensure_conversation_owner(conversation_id, user_id)

    conn = get_db()
    conversations = conn.execute(
        "SELECT id, title, created_at, pinned FROM conversations WHERE user_id = ? ORDER BY pinned DESC, id DESC",
        (user_id,),
    ).fetchall()

    exported = []
    for item in conversations:
        conv_id = int(item["id"])
        if conversation_id and conv_id != conversation_id:
            continue
        messages = conn.execute(
            "SELECT role, content, image FROM messages WHERE user_id = ? AND conversation_id = ? ORDER BY id ASC",
            (user_id, conv_id),
        ).fetchall()
        exported.append(
            {
                "conversation_id": conv_id,
                "title": item["title"] or "新对话",
                "created_at": item["created_at"] or "",
                "pinned": int(item["pinned"] or 0),
                "messages": [
                    {
                        "role": normalize_chat_role(message["role"]),
                        "content": message["content"] or "",
                        "image": message["image"] or "",
                    }
                    for message in messages
                ],
            }
        )
    conn.close()

    return {
        "code": 200,
        "exported_at": now_str(),
        "conversation_count": len(exported),
        "data": exported,
    }


@app.delete("/clear/{user_id}")
async def clear_chat(user_id: int, request: Request, conversation_id: int = 0):
    enforce_self(request, user_id)
    if conversation_id:
        ensure_conversation_owner(conversation_id, user_id)
    conn = get_db()
    conn.execute("DELETE FROM messages WHERE user_id = ? AND conversation_id = ?", (user_id, conversation_id))
    conn.commit()
    conn.close()
    return {"code": 200, "msg": "已清空"}


# ===========================================
# Moderation
# ===========================================
BLOCKED_KEYWORDS = ["裸聊", "儿童色情", "炸弹制作", "自杀指南", "枪支交易"]


def is_blocked_prompt(message: str) -> bool:
    lowered = (message or "").lower()
    return any(item.lower() in lowered for item in BLOCKED_KEYWORDS)


@app.post("/ai/report")
async def report_ai_output(payload: AIReportRequest, request: Request):
    enforce_self(request, payload.user_id)
    if payload.conversation_id:
        ensure_conversation_owner(payload.conversation_id, payload.user_id)
    reason = payload.reason.strip()[:50]
    if not reason:
        return {"code": 400, "msg": "请提供举报原因"}
    conn = get_db()
    conn.execute(
        "INSERT INTO ai_reports (user_id, conversation_id, reason, message_content, created_at) VALUES (?, ?, ?, ?, ?)",
        (payload.user_id, payload.conversation_id, reason, payload.message_content[:4000], now_str()),
    )
    conn.commit()
    conn.close()
    return {"code": 200, "msg": "已提交举报，我们会尽快处理"}


# ===========================================
# AI Tool Definitions
# ===========================================
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "draw_image",
            "description": "Generate a static image based on prompt description.",
            "parameters": {"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for real-time information.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_video",
            "description": "Generate a silent video clip based on prompt description.",
            "parameters": {
                "type": "object",
                "properties": {"prompt": {"type": "string", "description": "Detailed video description"}},
                "required": ["prompt"],
            },
        },
    },
]

VIDEO_KEYWORDS = ["视频", "动态", "动画", "video", "影片", "短片", "clip"]


def detect_video_intent(message: str) -> bool:
    return any(keyword in (message or "").lower() for keyword in VIDEO_KEYWORDS)


# ===========================================
# Chat
# ===========================================
@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    authed_user_id = enforce_self(request, req.user_id)
    if req.conversation_id:
        ensure_conversation_owner(req.conversation_id, authed_user_id)

    if check_rate_limit(authed_user_id):
        async def limited():
            yield "请求过于频繁，请稍后再试。"
        return StreamingResponse(limited(), media_type="text/plain")

    user_message = (req.message or "").strip() or "请处理请求"
    if is_blocked_prompt(user_message):
        async def blocked():
            yield "该请求包含高风险内容，当前版本不支持处理。"
        return StreamingResponse(blocked(), media_type="text/plain")

    if not deduct_balance_if_enough(authed_user_id, 1, "AI对话"):
        async def no_balance():
            yield "余额不足，请签到或充值后继续使用。"
        return StreamingResponse(no_balance(), media_type="text/plain")

    conn = get_db()
    conn.execute(
        "INSERT INTO messages (user_id, role, content, image, conversation_id) VALUES (?, ?, ?, ?, ?)",
        (authed_user_id, "user", user_message, req.image_base64, req.conversation_id),
    )
    conn.commit()
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE user_id = ? AND conversation_id = ? ORDER BY id ASC",
        (authed_user_id, req.conversation_id),
    ).fetchall()
    conn.close()

    formatted = [{"role": normalize_chat_role(item["role"]), "content": item["content"]} for item in rows]
    sys_prompt = """你是 AI Assistant，拥有调用外部工具的能力。
规则：
1. 用户要求图片/画 → 调用 draw_image
2. 用户要求视频/动画 → 调用 generate_video
3. 用户要搜索实时信息 → 调用 web_search
4. 明显违法、色情、自残、暴力风险内容要拒绝
5. 回复结尾带 @@@问题1|问题2|问题3@@@ 作为推荐追问"""
    formatted.insert(0, {"role": "system", "content": sys_prompt})
    user_wants_video = detect_video_intent(user_message)

    def generate_stream():
        base_cost_refunded = False
        current_balance = get_user_balance(authed_user_id)
        full_response = ""

        def refund_base_once():
            nonlocal base_cost_refunded
            if not base_cost_refunded:
                refund_balance(authed_user_id, 1, "AI对话失败返还")
                base_cost_refunded = True

        try:
            if req.image_base64:
                img_data = req.image_base64 if req.image_base64.startswith("data:image") else f"data:image/jpeg;base64,{req.image_base64}"
                vl_msgs = formatted[:-1]
                vl_msgs.append({
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": img_data}},
                        {"type": "text", "text": user_message},
                    ],
                })
                resp = requests.post(
                    normalize_qwen_api_url(QWEN_API_URL),
                    headers={"Authorization": f"Bearer {QWEN_API_KEY}"},
                    json={"model": resolve_qwen_vision_model(QWEN_MODEL_NAME), "messages": vl_msgs, "stream": True},
                    timeout=120,
                )
                if resp.status_code >= 400:
                    refund_base_once()
                    yield f"Qwen 请求失败：HTTP {resp.status_code} {resp.text}"
                    return
                for line in resp.iter_lines():
                    if not line:
                        continue
                    s = line.decode("utf-8")
                    if s.startswith("data: ") and "[DONE]" not in s:
                        chunk = json.loads(s[6:])["choices"][0]["delta"].get("content", "")
                        if chunk:
                            full_response += chunk
                            yield chunk
            else:
                use_model = req.model
                api_url, api_key, model_name, provider_label = resolve_text_model_config(use_model)

                for loop_i in range(5):
                    body = {"model": model_name, "messages": formatted, "tools": AGENT_TOOLS, "stream": True}
                    if loop_i == 0 and user_wants_video:
                        body["tool_choice"] = {"type": "function", "function": {"name": "generate_video"}}

                    resp = requests.post(
                        api_url,
                        headers={"Authorization": f"Bearer {api_key}"},
                        json=body,
                        timeout=120,
                    )
                    if resp.status_code >= 400:
                        refund_base_once()
                        yield f"{provider_label} 请求失败：HTTP {resp.status_code} {resp.text}"
                        return

                    tool_calls = []
                    is_tool_call = False

                    for line in resp.iter_lines():
                        if not line:
                            continue
                        s = line.decode("utf-8")
                        if not s.startswith("data: ") or "[DONE]" in s:
                            continue
                        data = json.loads(s[6:])
                        delta = data["choices"][0]["delta"]
                        if "tool_calls" in delta and delta["tool_calls"]:
                            is_tool_call = True
                            for tc in delta["tool_calls"]:
                                idx = tc["index"]
                                while len(tool_calls) <= idx:
                                    tool_calls.append({"name": "", "arguments": ""})
                                if "function" in tc:
                                    if "name" in tc["function"]:
                                        tool_calls[idx]["name"] += tc["function"]["name"]
                                    if "arguments" in tc["function"]:
                                        tool_calls[idx]["arguments"] += tc["function"]["arguments"]
                        elif "content" in delta and not is_tool_call:
                            chunk = delta.get("content", "")
                            if chunk:
                                full_response += chunk
                                yield chunk

                    if not is_tool_call or not tool_calls:
                        break

                    func_name = tool_calls[0]["name"]
                    try:
                        args = json.loads(tool_calls[0]["arguments"] or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    observation = ""

                    if func_name == "web_search":
                        query = args.get("query", "")
                        yield f"\n\n> 🔍 搜索中：「{query}」...\n\n"
                        try:
                            import dashscope
                            res = dashscope.Generation.call(
                                model="qwen-max",
                                messages=[{"role": "user", "content": f"搜索并总结：{query}"}],
                                result_format="message",
                                api_key=QWEN_API_KEY,
                                enable_search=True,
                            )
                            observation = res.output.choices[0].message.content
                        except Exception as exc:
                            observation = f"搜索失败: {exc}"

                    elif func_name == "draw_image":
                        prompt = args.get("prompt", "")
                        if not deduct_balance_if_enough(authed_user_id, 10, "AI绘画"):
                            yield "\n\n余额不足：绘画需要 10 点算力。\n"
                            break
                        try:
                            from dashscope import ImageSynthesis
                            yield f"\n\n> 🎨 生成图片中：「{prompt[:30]}...」\n\n"
                            task = ImageSynthesis.call(
                                model="wanx-v1",
                                prompt=prompt,
                                n=1,
                                size="1024*1024",
                                api_key=QWEN_API_KEY,
                            )
                            if task.status_code == 200:
                                url = task.output.results[0].url
                                tag = f"[IMAGE:{url}]"
                                full_response += tag
                                yield f"{tag}\n\n"
                                observation = f"图片已生成：{url}"
                            else:
                                refund_balance(authed_user_id, 10, "AI绘画失败返还")
                                yield f"\n\n图片生成失败：{task.message}\n"
                                observation = f"失败：{task.message}"
                        except Exception as exc:
                            refund_balance(authed_user_id, 10, "AI绘画失败返还")
                            yield f"\n\n绘画异常：{exc}\n"
                            observation = f"失败: {exc}"

                    elif func_name == "generate_video":
                        prompt = args.get("prompt", "")
                        if not deduct_balance_if_enough(authed_user_id, 50, "AI视频"):
                            yield "\n\n余额不足：视频需要 50 点算力。\n"
                            break
                        try:
                            from dashscope import VideoSynthesis
                            yield f"\n\n> 🎬 生成视频中：「{prompt[:30]}...」\n\n"
                            task = VideoSynthesis.call(
                                model="wanx2.1-t2v-turbo",
                                prompt=prompt,
                                api_key=QWEN_API_KEY,
                            )
                            if task.status_code == 200 and task.output and task.output.task_id:
                                task_id = task.output.task_id
                                yield "> 任务已提交，生成中...\n\n"
                                for _ in range(60):
                                    time.sleep(5)
                                    status = VideoSynthesis.fetch(task_id, api_key=QWEN_API_KEY)
                                    task_status = status.output.task_status if status.output else "UNKNOWN"
                                    if task_status == "SUCCEEDED":
                                        video_url = status.output.video_url
                                        tag = f"[VIDEO:{video_url}]"
                                        full_response += tag
                                        yield f"{tag}\n\n当前版本生成的是无声视频，如需配音或背景音乐，需要后续单独处理。\n\n"
                                        observation = f"视频已生成（当前为无声视频）：{video_url}"
                                        break
                                    if task_status in ("FAILED", "UNKNOWN"):
                                        refund_balance(authed_user_id, 50, "AI视频失败返还")
                                        yield "\n\n视频生成失败。\n"
                                        observation = "视频生成失败"
                                        break
                                else:
                                    refund_balance(authed_user_id, 50, "AI视频超时返还")
                                    yield "\n\n视频生成超时。\n"
                                    observation = "超时"
                            else:
                                refund_balance(authed_user_id, 50, "AI视频失败返还")
                                yield f"\n\n视频任务提交失败：{task.message}\n"
                                observation = f"失败：{task.message}"
                        except Exception as exc:
                            refund_balance(authed_user_id, 50, "AI视频失败返还")
                            yield f"\n\n视频异常：{exc}\n"
                            observation = f"失败: {exc}"

                    formatted.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{
                            "id": "call_0",
                            "type": "function",
                            "function": {"name": func_name, "arguments": json.dumps(args, ensure_ascii=False)},
                        }],
                    })
                    formatted.append({"role": "tool", "tool_call_id": "call_0", "content": observation})

        except requests.RequestException as exc:
            refund_base_once()
            yield f"网络请求失败：{exc}"
            return
        except Exception as exc:
            refund_base_once()
            yield f"服务处理异常：{exc}"
            return
        finally:
            if full_response:
                conn2 = get_db()
                conn2.execute(
                    "INSERT INTO messages (user_id, role, content, conversation_id) VALUES (?, ?, ?, ?)",
                    (authed_user_id, "assistant", full_response, req.conversation_id),
                )
                conn2.execute(
                    "UPDATE conversations SET title = ? WHERE id = ? AND title = '新对话'",
                    (user_message[:20], req.conversation_id),
                )
                conn2.commit()
                conn2.close()

    return StreamingResponse(generate_stream(), media_type="text/plain")


# ===========================================
# Entry point
# ===========================================
if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    print(f"Server starting at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
