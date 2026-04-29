import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

from enums.currency import Currency
from enums.runtime_environment import RuntimeEnvironment
from utils.utils import get_sslipio_external_url, start_ngrok, hash_password


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_admin_ids(value: str | None) -> list[int]:
    if not value:
        return []
    return [int(admin_id.strip()) for admin_id in value.split(",") if admin_id.strip()]


def _normalize_webhook_path(value: str | None) -> str:
    raw_path = (value or "/webhook").strip() or "/webhook"
    return raw_path if raw_path.startswith("/") else f"/{raw_path}"


def _build_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            return database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        if database_url.startswith("postgresql://"):
            return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return database_url

    user = quote_plus(os.environ.get("POSTGRES_USER", "postgres"))
    password = quote_plus(os.environ.get("POSTGRES_PASSWORD", ""))
    host = os.environ.get("DB_HOST", "localhost")
    port = int(os.environ.get("DB_PORT", "5432"))
    database = os.environ.get("POSTGRES_DB", "aiogram-shop-bot")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"


load_dotenv(".env", override=False)
load_dotenv(".env.bot.dev", override=False)

RUNTIME_ENVIRONMENT = RuntimeEnvironment(
    os.environ.get("RUNTIME_ENVIRONMENT", RuntimeEnvironment.PROD.value).upper()
)

WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST") or os.environ.get("RENDER_EXTERNAL_URL")
if not WEBHOOK_HOST:
    if RUNTIME_ENVIRONMENT == RuntimeEnvironment.DEV:
        WEBHOOK_HOST = start_ngrok()
    else:
        WEBHOOK_HOST = get_sslipio_external_url()

WEBHOOK_HOST = WEBHOOK_HOST.rstrip("/")
WEBHOOK_PATH = _normalize_webhook_path(os.environ.get("WEBHOOK_PATH"))
WEBAPP_HOST = os.environ.get("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.environ.get("PORT") or os.environ.get("WEBAPP_PORT", "5000"))
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

TOKEN = os.environ.get("TOKEN")
ADMIN_ID_LIST = _parse_admin_ids(os.environ.get("ADMIN_ID_LIST"))
SUPPORT_LINK = os.environ.get("SUPPORT_LINK")

# POSTGRESQL
DB_USER = os.environ.get("POSTGRES_USER", "postgres")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("POSTGRES_DB", "aiogram-shop-bot")
DATABASE_URL = _build_database_url()
SQL_ECHO = _parse_bool(os.environ.get("SQL_ECHO"), default=False)

PAGE_ENTRIES = int(os.environ.get("PAGE_ENTRIES", "8"))
MULTIBOT = _parse_bool(os.environ.get("MULTIBOT"), default=False)
CURRENCY = Currency(os.environ.get("CURRENCY", "USD"))
KRYPTO_EXPRESS_API_KEY = os.environ.get("KRYPTO_EXPRESS_API_KEY")
KRYPTO_EXPRESS_API_URL = os.environ.get("KRYPTO_EXPRESS_API_URL")
KRYPTO_EXPRESS_API_SECRET = os.environ.get("KRYPTO_EXPRESS_API_SECRET")
WEBHOOK_SECRET_TOKEN = os.environ.get("WEBHOOK_SECRET_TOKEN")

REDIS_URL = os.environ.get("REDIS_URL")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
TELEGRAM_PROXY_URL = os.environ.get("TELEGRAM_PROXY_URL")

# VARIABLES FOR CRYPTO FORWARDING
CRYPTO_FORWARDING_MODE = _parse_bool(os.environ.get("CRYPTO_FORWARDING_MODE"), default=False)
BTC_FORWARDING_ADDRESS = os.environ.get("BTC_FORWARDING_ADDRESS")
LTC_FORWARDING_ADDRESS = os.environ.get("LTC_FORWARDING_ADDRESS")
ETH_FORWARDING_ADDRESS = os.environ.get("ETH_FORWARDING_ADDRESS")
SOL_FORWARDING_ADDRESS = os.environ.get("SOL_FORWARDING_ADDRESS")
BNB_FORWARDING_ADDRESS = os.environ.get("BNB_FORWARDING_ADDRESS")
DOGE_FORWARDING_ADDRESS = os.environ.get("DOGE_FORWARDING_ADDRESS")

# VARIABLES FOR THE REFERRAL SYSTEM
MIN_REFERRER_TOTAL_DEPOSIT = int(os.environ.get("MIN_REFERRER_TOTAL_DEPOSIT", "500"))
REFERRAL_BONUS_PERCENT = float(os.environ.get("REFERRAL_BONUS_PERCENT", "5"))
REFERRAL_BONUS_DEPOSIT_LIMIT = int(os.environ.get("REFERRAL_BONUS_DEPOSIT_LIMIT", "3"))
REFERRER_BONUS_PERCENT = float(os.environ.get("REFERRER_BONUS_PERCENT", "3"))
REFERRER_BONUS_DEPOSIT_LIMIT = int(os.environ.get("REFERRER_BONUS_DEPOSIT_LIMIT", "5"))
REFERRAL_BONUS_CAP_PERCENT = float(os.environ.get("REFERRAL_BONUS_CAP_PERCENT", "7"))
REFERRER_BONUS_CAP_PERCENT = float(os.environ.get("REFERRER_BONUS_CAP_PERCENT", "7"))
TOTAL_BONUS_CAP_PERCENT = float(os.environ.get("TOTAL_BONUS_CAP_PERCENT", "12"))

# SQLADMIN
SQLADMIN_RAW_PASSWORD = os.environ.get("SQLADMIN_RAW_PASSWORD")
SQLADMIN_HASHED_PASSWORD = hash_password(SQLADMIN_RAW_PASSWORD) if SQLADMIN_RAW_PASSWORD else None
JWT_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "30"))
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or WEBHOOK_SECRET_TOKEN or "change-me"
