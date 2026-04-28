"""
config.py - إعدادات البوت
─────────────────────────────────────────────────────────
محلياً   → يقرأ من ملف .env إذا وُجد
على Render → يقرأ من Environment Variables مباشرة
لا تضع التوكن في الكود أبداً!
─────────────────────────────────────────────────────────
"""

import os
import sys

# ─── تحميل .env محلياً فقط ────────────────────────────
# على Render لا يوجد ملف .env وهذا طبيعي تماماً
# python-dotenv ذكية: إذا لم تجد الملف تكمل بصمت بدون خطأ
try:
    from dotenv import load_dotenv
    loaded = load_dotenv(override=False, verbose=False)
    if loaded:
        print("📁 config: تم تحميل ملف .env المحلي")
    else:
        print("☁️  config: Render mode - سيُقرأ من Environment Variables")
except ImportError:
    # python-dotenv غير مثبت - لا مشكلة على Render
    print("☁️  config: python-dotenv غير موجود - Render mode")

# ════════════════════════════════════════════════════════
#   قراءة المتغيرات البيئية
# ════════════════════════════════════════════════════════

BOT_TOKEN: str    = os.getenv("BOT_TOKEN", "")
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

# ADMIN_ID محمي من خطأ التحويل
try:
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
except ValueError:
    print("⚠️  ADMIN_ID ليس رقماً صحيحاً - سيُعيَّن 0")
    ADMIN_ID = 0

# ─── إعدادات المتجر (اختيارية - لها قيم افتراضية) ───
STORE_NAME          = os.getenv("STORE_NAME", "🏪 متجري")
STORE_CURRENCY      = os.getenv("STORE_CURRENCY", "ريال")
try:
    POINTS_PER_PURCHASE = int(os.getenv("POINTS_PER_PURCHASE", "10"))
except ValueError:
    POINTS_PER_PURCHASE = 10

# ════════════════════════════════════════════════════════
#   فحص المتغيرات الأساسية مع رسائل واضحة في اللوق
# ════════════════════════════════════════════════════════

print("🔍 config: فحص المتغيرات البيئية...")
print(f"   BOT_TOKEN   : {'✅ موجود (' + str(len(BOT_TOKEN)) + ' chars)' if BOT_TOKEN    else '❌ مفقود'}")
print(f"   ADMIN_ID    : {'✅ ' + str(ADMIN_ID)               if ADMIN_ID    else '❌ مفقود أو صفر'}")
print(f"   SUPABASE_URL: {'✅ موجود'                           if SUPABASE_URL else '❌ مفقود'}")
print(f"   SUPABASE_KEY: {'✅ موجود'                           if SUPABASE_KEY else '❌ مفقود'}")

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
    print("\n" + "=" * 55)
    print(f"❌ FATAL: المتغيرات التالية مفقودة: {', '.join(_errors)}")
    print("   على Render: Dashboard > Environment > Add Variable")
    print("   محلياً    : أضفها في ملف .env")
    print("=" * 55 + "\n")
    sys.exit(1)

print("✅ config: كل المتغيرات البيئية جاهزة\n")
