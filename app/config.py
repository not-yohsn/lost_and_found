import os
import ssl

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "lost_and_found")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Re-check connections before using them — important for serverless DBs
    # like TiDB Cloud that may close idle connections.
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Enable TLS to the DB (required by TiDB Cloud, PlanetScale, Aiven, etc.).
    # Set DB_SSL=1 in the environment.
    if os.getenv("DB_SSL", "0") == "1":
        _ca_path = os.getenv("DB_SSL_CA") or ssl.get_default_verify_paths().cafile
        SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {"ssl": {"ca": _ca_path}}

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "app/static/uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 3 * 1024 * 1024))

    # Mail (optional). Leave MAIL_SERVER blank to disable outbound email —
    # in-app notifications still work.
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "1") == "1"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER", "Lost & Found <noreply@lostandfound.local>"
    )
