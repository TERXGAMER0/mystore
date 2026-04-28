"""
database/db.py - الاتصال بـ Supabase
──────────────────────────────────────
"""

import logging
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

_supabase: Client = None


def get_db() -> Client:
    """إرجاع Supabase client (singleton)"""
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase


def init_db():
    """
    التحقق من الاتصال بـ Supabase.
    يرمي Exception إذا فشل - bot.py يلتقطها ويوقف بشكل نظيف.
    """
    db = get_db()

    # اختبار بسيط: اقرأ صف واحد من bot_settings
    try:
        result = db.table("bot_settings").select("key").limit(1).execute()
        logger.info(f"✅ Supabase متصل - bot_settings: {len(result.data)} سجل")
    except Exception as e:
        error_msg = str(e)
        if "relation" in error_msg and "does not exist" in error_msg:
            # الجداول غير موجودة - رسالة واضحة
            raise RuntimeError(
                "❌ جداول قاعدة البيانات غير موجودة!\n"
                "   الحل: افتح Supabase > SQL Editor وشغّل ملف setup.sql"
            ) from e
        elif "Invalid API key" in error_msg or "401" in error_msg:
            raise RuntimeError(
                "❌ SUPABASE_KEY غير صحيح!\n"
                "   الحل: تحقق من قيمة SUPABASE_KEY في Environment Variables"
            ) from e
        else:
            raise RuntimeError(f"❌ فشل الاتصال بـ Supabase: {error_msg}") from e


# ── SQL لإنشاء الجداول (شغّله مرة واحدة في Supabase > SQL Editor) ──────
SETUP_SQL = """
-- شغّل هذا في: Supabase > SQL Editor > New query

CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL   PRIMARY KEY,
    telegram_id BIGINT      UNIQUE NOT NULL,
    username    TEXT,
    first_name  TEXT,
    last_name   TEXT,
    points      INTEGER     DEFAULT 0 NOT NULL,
    is_banned   BOOLEAN     DEFAULT FALSE,
    joined_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id          BIGSERIAL      PRIMARY KEY,
    name        TEXT           NOT NULL,
    description TEXT,
    price       NUMERIC(10,2)  NOT NULL CHECK (price >= 0),
    stock       INTEGER        DEFAULT 0 CHECK (stock >= 0),
    photo_id    TEXT,
    is_active   BOOLEAN        DEFAULT TRUE,
    created_at  TIMESTAMPTZ    DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
    id          BIGSERIAL      PRIMARY KEY,
    user_id     BIGINT         REFERENCES users(telegram_id) ON DELETE SET NULL,
    product_id  BIGINT         REFERENCES products(id)       ON DELETE SET NULL,
    quantity    INTEGER        DEFAULT 1 CHECK (quantity > 0),
    total_price NUMERIC(10,2)  NOT NULL,
    status      TEXT           DEFAULT 'pending'
                               CHECK (status IN ('pending','confirmed','cancelled','refunded')),
    notes       TEXT,
    created_at  TIMESTAMPTZ    DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bot_settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO bot_settings (key, value) VALUES
    ('welcome_message', '👋 أهلاً {name}!
اختر من القائمة أدناه 👇'),
    ('about_message',   '🏪 متجرنا الإلكتروني
نقدم أفضل المنتجات بأسهل الطرق!'),
    ('maintenance_mode','false')
ON CONFLICT (key) DO NOTHING;
"""
