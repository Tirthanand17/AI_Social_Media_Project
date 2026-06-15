from pathlib import Path
import base64
import hashlib
import hmac
import json
import os
import time
from typing import Optional

import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

USERS = ROOT / "data" / "raw" / "10_users_data.csv"

# Demo login is kept only for local prototype runs.
# For production, set DEMO_LOGIN_ENABLED=false and configure role passwords/hashes in .env.
DEMO_ROLE_PASSWORDS = {"admin": "admin123", "editor": "editor123", "viewer": "viewer123"}
ROLE_ENV_PREFIX = {"admin": "ADMIN", "editor": "EDITOR", "viewer": "VIEWER"}


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def load_users():
    return pd.read_csv(USERS)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _app_secret() -> str:
    secret = os.getenv("APP_SECRET", "").strip()
    if not secret or secret == "demo_secret_change_later":
        # Keeps local tests working, but production should always set a strong APP_SECRET.
        return "local_demo_secret_change_before_deploying"
    return secret


def make_password_hash(password: str, salt: Optional[str] = None) -> dict:
    """Helper for generating PBKDF2 password hashes for .env values."""
    if not salt:
        salt = _b64url_encode(os.urandom(16))
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return {"salt": salt, "hash": _b64url_encode(digest)}


def _verify_hashed_password(password: str, salt: str, expected_hash: str) -> bool:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return hmac.compare_digest(_b64url_encode(digest), expected_hash)


def _verify_role_password(role: str, password: str) -> bool:
    role_key = str(role).lower().strip()
    env_prefix = ROLE_ENV_PREFIX.get(role_key)
    if not env_prefix:
        return False

    hash_value = os.getenv(f"{env_prefix}_PASSWORD_HASH", "").strip()
    salt_value = os.getenv(f"{env_prefix}_PASSWORD_SALT", "").strip()
    if hash_value and salt_value:
        return _verify_hashed_password(password, salt_value, hash_value)

    # Plain .env passwords are acceptable for a prototype/private deployment.
    # Prefer *_PASSWORD_HASH + *_PASSWORD_SALT for production.
    env_password = os.getenv(f"{env_prefix}_PASSWORD", "").strip()
    if env_password:
        return hmac.compare_digest(password, env_password)

    if _env_bool("DEMO_LOGIN_ENABLED", True):
        return hmac.compare_digest(password, DEMO_ROLE_PASSWORDS.get(role_key, ""))

    return False


def create_token(payload: dict, expires_in_seconds: int = 60 * 60 * 8) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    secure_payload = dict(payload)
    secure_payload.update({"iat": now, "exp": now + expires_in_seconds})

    encoded_header = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = _b64url_encode(json.dumps(secure_payload, separators=(",", ":")).encode())
    signing_input = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(_app_secret().encode(), signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_b64url_encode(signature)}"


def login(username, password):
    df = load_users()
    row = df[df["username"].astype(str) == username]
    if row.empty:
        return {"success": False, "message": "Invalid username"}

    user = row.iloc[0].to_dict()
    if not _verify_role_password(str(user["role"]), password):
        return {"success": False, "message": "Invalid password"}

    payload = {
        "username": user["username"],
        "role": user["role"],
        "brand_name": user["brand_name"],
    }
    token = create_token(payload)
    return {
        "success": True,
        "token": token,
        "token_type": "Bearer",
        "expires_in_seconds": 60 * 60 * 8,
        "user": payload,
    }


def decode_token(token):
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
        signing_input = f"{encoded_header}.{encoded_payload}".encode()
        expected_signature = hmac.new(_app_secret().encode(), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url_encode(expected_signature), encoded_signature):
            return None

        payload = json.loads(_b64url_decode(encoded_payload).decode())
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


if __name__ == "__main__":
    print(login("admin_techcreate", "admin123"))
