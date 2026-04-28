"""
database/db.py - الاتصال بـ Supabase وتهيئة الجداول
─────────────────────────────────────────────────────
يستخدم supabase-py للتواصل مع Supabase (PostgreSQL)
"""

import logging
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

# ─── Supabase Client (Singleton) ──────────────────────
_supabase: Client = None


def get_db() -> Client:
    """إرجاع اتصال Supabase (ينشئه مرة واحدة فقط)"""
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase


# ─── SQL لإنشاء الجداول ───────────────────────────────
# شغّل هذا SQL في Supabase > SQL Editor مرة واحدة فقط
SETUP_SQL = """
-- ══════════════════════════════════════════════
--  BOT STORE - Database Setup SQL
--  شغّل هذا في Supabase > SQL Editor
-- ══════════════════════════════════════════════

-- جدول المستخدمين
CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username    TEXT,
    first_name  TEXT,
    last_name   TEXT,
    points      INTEGER DEFAULT 0,
    is_banned   BOOLEAN DEFAULT FALSE,
    joined_at   TIMESTAMPTZ DEFAULT NOW()
);

-- جدول المنتجات
CREATE TABLE IF NOT EXISTS products (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT,
    price       NUMERIC(10,2) NOT NULL,
    stock       INTEGER DEFAULT 0,
    photo_id    TEXT,              -- file_id من تيليجرام
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- جدول الطلبات
CREATE TABLE IF NOT EXISTS orders (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT REFERENCES users(telegram_id),
    product_id  BIGINT REFERENCES products(id),
    quantity    INTEGER DEFAULT 1,
    total_price NUMERIC(10,2),
    status      TEXT DEFAULT 'pending',   -- pending / confirmed / cancelled
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- جدول إعدادات البوت
CREATE TABLE IF NOT EXISTS bot_settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- إدراج الإعدادات الافتراضية
INSERT INTO bot_settings (key, value) VALUES
    ('welcome_message', '👋 أهلاً بك في متجرنا!\nاختر من القائمة أدناه 👇'),
    ('about_message',   '🏪 متجرنا الإلكتروني\nنقدم أفضل المنتجات بأسهل الطرق!')
ON CONFLICT (key) DO NOTHING;
"""


def init_db():
    """
    تهيئة قاعدة البيانات - تحقق من الاتصال
    (الجداول تُنشأ يدوياً عبر SQL Editor في Supabase)
    """
    try:
        db = get_db()
        # اختبار بسيط للاتصال
        result = db.table("bot_settings").select("key").limit(1).execute()
        logger.info("✅ الاتصال بـ Supabase ناجح")
        logger.info(f"   جدول bot_settings يحتوي على {len(result.data)} سجل")
    except Exception as e:
        logger.error(f"❌ فشل الاتصال بـ Supabase: {e}")
        logger.error("💡 تأكد أنك شغّلت SETUP_SQL في Supabase > SQL Editor")
        raise
