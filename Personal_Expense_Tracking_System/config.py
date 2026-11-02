"""Application configuration.

Settings are read from environment variables. For local use, put them in a
file called ".env" next to this file (copy ".env.example" and edit it).
"""
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", encoding="utf-8")


def _int_env(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


class Config:
    """Application configuration; MySQL remains the default local backend."""

    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or (
        None if os.environ.get("VERCEL") else secrets.token_hex(32))
    CSRF_ENABLED = True
    CURRENCY_SYMBOL = os.environ.get("CURRENCY_SYMBOL", "\u20b9")
    PUBLIC_DEMO = os.environ.get(
        "PUBLIC_DEMO", "true" if os.environ.get("VERCEL") else ""
    ).lower() in ("1", "true", "yes")

    DB_BACKEND = os.environ.get(
        "DB_BACKEND",
        "postgres" if os.environ.get("DATABASE_URL") else "mysql")
    DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = _int_env("DB_PORT", 3306)
    DB_USER = os.environ.get("DB_USER", "")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")  # None when not set
    DB_NAME = os.environ.get("DB_NAME", "expense_tracker")
    SQLITE_PATH = None  # only used by the automated tests


def config_as_dict():
    """Return the Config class as a plain dictionary (used by scripts)."""
    return {k: getattr(Config, k) for k in dir(Config) if k.isupper()}


def config_problems_for_startup(cfg):
    """Problems to print when the server starts (the app still starts)."""
    from db import config_problems
    if cfg.get("DB_BACKEND") == "sqlite":
        return []
    return config_problems(cfg)
