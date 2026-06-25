"""
Simple JSON-file user store.
Replace with SQLAlchemy + PostgreSQL when scaling to multiple users.
"""

import json
import os
from pathlib import Path
from typing import Optional

from api.core.security import hash_password

_STORE_PATH = Path(__file__).parent / "users.json"


def _load() -> dict:
    if not _STORE_PATH.exists():
        return {}
    with open(_STORE_PATH) as f:
        return json.load(f)


def _save(data: dict) -> None:
    with open(_STORE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_user(username: str) -> Optional[dict]:
    return _load().get(username)


def create_user(username: str, password: str, role: str = "user") -> dict:
    db = _load()
    if username in db:
        raise ValueError(f"User '{username}' already exists.")
    user = {
        "username": username,
        "hashed_password": hash_password(password),
        "role": role,
        "is_active": True,
    }
    db[username] = user
    _save(db)
    return user


def list_users() -> list[dict]:
    return list(_load().values())


def bootstrap_admin() -> None:
    """Create the default admin on first run. Called explicitly from main.py lifespan."""
    admin_user = os.getenv("ADMIN_USERNAME", "admin")
    admin_pass = os.getenv("ADMIN_PASSWORD", "changeme123")
    if not get_user(admin_user):
        create_user(admin_user, admin_pass, role="admin")
        print(f"[bootstrap] Created default admin user: '{admin_user}'")
