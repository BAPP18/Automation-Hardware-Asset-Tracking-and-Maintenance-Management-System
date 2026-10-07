import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    APP_ENV = os.environ.get("APP_ENV", "development").lower()

    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        if APP_ENV == "production":
            raise RuntimeError("SECRET_KEY must be configured in production.")
        # A random development key avoids committing a reusable secret. Sessions
        # intentionally become invalid after a local process restart unless the
        # developer provides SECRET_KEY explicitly.
        SECRET_KEY = secrets.token_urlsafe(48)
    elif APP_ENV == "production" and len(SECRET_KEY) < 32:
        raise RuntimeError("SECRET_KEY must contain at least 32 characters in production.")

    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = (
        database_url
        or "sqlite:///" + os.path.join(BASE_DIR, "database", "asset.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
    EXPORT_FOLDER = os.environ.get("EXPORT_FOLDER", os.path.join(BASE_DIR, "exports"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 50 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "xlsx", "txt"}

    # Demo accounts are always opt-in. Production refuses to boot with demo
    # seeding enabled, even if an environment variable is set accidentally.
    SEED_DEMO_DATA = _as_bool(os.environ.get("SEED_DEMO_DATA"), default=False)
    if APP_ENV == "production" and SEED_DEMO_DATA:
        raise RuntimeError("SEED_DEMO_DATA must be disabled in production.")

    DEMO_ADMIN_PASSWORD = os.environ.get("DEMO_ADMIN_PASSWORD")
    DEMO_ENGINEER_PASSWORD = os.environ.get("DEMO_ENGINEER_PASSWORD")

    LOGIN_MAX_ATTEMPTS = int(os.environ.get("LOGIN_MAX_ATTEMPTS", 5))
    LOGIN_WINDOW_SECONDS = int(os.environ.get("LOGIN_WINDOW_SECONDS", 10 * 60))
    LOGIN_LOCKOUT_SECONDS = int(os.environ.get("LOGIN_LOCKOUT_SECONDS", 15 * 60))
    LOGIN_IP_MAX_ATTEMPTS = int(os.environ.get("LOGIN_IP_MAX_ATTEMPTS", 25))

    MAX_IMPORT_FILE_SIZE = int(
        os.environ.get("MAX_IMPORT_FILE_SIZE", 5 * 1024 * 1024)
    )
    MAX_IMPORT_ROWS = int(os.environ.get("MAX_IMPORT_ROWS", 5000))

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _as_bool(
        os.environ.get("SESSION_COOKIE_SECURE"),
        default=APP_ENV == "production",
    )
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE

    PERMANENT_SESSION_LIFETIME = 8 * 60 * 60
