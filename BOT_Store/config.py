"""
config.py - إعدادات البوت
─────────────────────────────────────────────────────────
محلياً   → يقرأ من ملف .env
على Render → يقرأ من Environment Variables في لوحة التحكم
لا تضع التوكن مباشرة في الكود أبداً!
─────────────────────────────────────────────────────────
"""

import os
import sys
from dotenv import load_dotenv

# ─── تحميل البيئة ─────────────────────────────────────
# محلياً  : يحمّل ملف .env إذا وُجد
# على Render: لا يوجد .env - المتغيرات محقونة مباشرة في البيئة
# override=False: إذا كان المتغير موجوداً في البيئة الفعلية، لا تُعيد تعريفه
load_dotenv(override=False)

# ─── توكن البوت ───────────────────────────────────────
# من @BotFather | على Render: Environment Variables > BOT_TOKEN
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# ─── معرف الأدمن ──────────────────────────────────────
# معرفك الرقمي من @userinfobot | على Render: ADMIN_ID
ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))

# ─── Supabase ─────────────────────────────────────────
# من Supabase > Settings > API
# على Render: SUPABASE_URL و SUPABASE_KEY
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")  # anon/public key

# ─── إعدادات المتجر (اختيارية) ───────────────────────
STORE_NAME          = os.getenv("STORE_NAME", "🏪 متجري")
STORE_CURRENCY      = os.getenv("STORE_CURRENCY", "ريال")
POINTS_PER_PURCHASE = int(os.getenv("POINTS_PER_PURCHASE", "10"))

# ─── التحقق من الإعدادات الأساسية ────────────────────
# يوقف البوت مبكراً برسالة واضحة بدل خطأ غامض لاحقاً
_errors = []

if not BOT_TOKEN:
    _errors.append("BOT_TOKEN")
if not SUPABASE_URL:
    _errors.append("SUPABASE_URL")
if not SUPABASE_KEY:
    _errors.append("SUPABASE_KEY")
if ADMIN_ID == 0:
    _errors.append("ADMIN_ID")

if _errors:
    print(f"❌ متغيرات البيئة التالية مفقودة: {', '.join(_errors)}")
    print("   محلياً: أضفها في ملف .env")
    print("   على Render: أضفها في Dashboard > Environment Variables")
    sys.exit(1)
