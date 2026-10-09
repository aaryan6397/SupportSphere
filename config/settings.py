import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    APP_ENV = os.getenv("APP_ENV", "development").lower()
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-secret-key-change-later"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///supportsphere.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    UPLOAD_FOLDER = BASE_DIR / "uploads"

    ALLOWED_FILE_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "pdf",
        "doc",
        "docx"
    }

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    CSRF_PROTECTION_ENABLED = True
    PASSWORD_RESET_MAX_AGE = 30 * 60
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "true").lower() == "true"
    LOGIN_RATE_LIMIT = 5
    PASSWORD_RESET_RATE_LIMIT = 3
    RATE_LIMIT_WINDOW_SECONDS = 15 * 60

    @classmethod
    def validate(cls):
        if cls.APP_ENV == "production" and cls.SECRET_KEY == "development-secret-key-change-later":
            raise RuntimeError("SECRET_KEY must be set to a strong value when APP_ENV=production.")
        if cls.APP_ENV == "production" and not cls.SESSION_COOKIE_SECURE:
            raise RuntimeError("SESSION_COOKIE_SECURE must be true when APP_ENV=production.")


class TestingConfig(Config):
    TESTING = True
    CSRF_PROTECTION_ENABLED = False
