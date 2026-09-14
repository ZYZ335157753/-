import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-before-production")
    DATABASE = BASE_DIR / "instance" / "yunqi_tea.db"
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Tea2026!")
    CORS_ORIGINS = [item.strip() for item in os.getenv("CORS_ORIGINS", "*").split(",")]
    JSON_AS_ASCII = False

