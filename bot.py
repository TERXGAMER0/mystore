"""
bot.py - نقطة البداية لبوت المتجر
====================================================
كل خطوة مرقّمة في اللوق لتعرف بالضبط أين يتوقف
====================================================
"""

# ── [1] أول رسالة تظهر في اللوق ──────────────────────
print("=" * 55)
print("  Bot is starting...")
print("  BOT STORE - بوت المتجر بدأ التشغيل")
print("=" * 55)

import sys
import logging

# ── [2] إعداد اللوق على stdout (مطلوب على Render) ────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)
logger.info("[2] ✅ Logging جاهز")

# ── [3] استيراد python-telegram-bot ───────────────────
logger.info("[3] 📦 استيراد python-telegram-bot...")
try:
    from telegram.ext import (
        Application,
        CommandHandler,
        CallbackQueryHandler,
        MessageHandler,
        ConversationHandler,
        filters,
    )
    logger.info("[3] ✅ python-telegram-bot جاهز")
except ImportError as e:
    logger.error(f"[3] ❌ فشل: {e} - شغّل: pip install python-telegram-bot==21.6")
    sys.exit(1)

# ── [4] تحميل config والتحقق من المتغيرات ────────────
logger.info("[4] ⚙️  تحميل config.py...")
try:
    from config import BOT_TOKEN, ADMIN_ID
    logger.info("[4] ✅ config.py محمّل")
except SystemExit:
    # config.py طبع الخطأ وطلب الخروج - متغيرات بيئية ناقصة
    sys.exit(1)
except Exception as e:
    logger.error(f"[4] ❌ خطأ في config.py: {e}")
    sys.exit(1)

# ── [5] استيراد الـ Handlers ──────────────────────────
logger.info("[5] 📂 استيراد الـ handlers...")
try:
    from handlers import user_handlers, admin_handlers, product_handlers
    logger.info("[5] ✅ handlers جاهزة")
except Exception as e:
    logger.error(f"[5] ❌ خطأ في handlers: {e}")
    sys.exit(1)

# ── [6] الاتصال بـ Supabase ───────────────────────────
logger.info("[6] 🗄️  الاتصال بـ Supabase...")
try:
    from database.db import init_db
    init_db()
    logger.info("[6] ✅ Supabase جاهز")
except Exception as e:
    logger.error(f"[6] ❌ فشل Supabase: {e}")
    logger.error("    تأكد من SUPABASE_URL و SUPABASE_KEY وأن الجداول مُنشأة")
    sys.exit(1)

# ── States للـ ConversationHandler ────────────────────
(
    WAITING_BROADCAST_MSG,
    WAITING_PRODUCT_NAME,
    WAITING_PRODUCT_DESC,
    WAITING_PRODUCT_PRICE,
    WAITING_PRODUCT_PHOTO,
    WAITING_PRODUCT_STOCK,
    WAITING_DELETE_PRODUCT_ID,
    WAITING_WELCOME_MSG,
    WAITING_ADD_POINTS_USER,
    WAITING_ADD_POINTS_AMOUNT,
) = range(10)


def main():
    """تجميع البوت وتشغيله بوضع Long Polling"""

    # ── [7] بناء Application ──────────────────────────
    logger.info("[7] 🔨 بناء Application...")
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        logger.info("[7] ✅ Application جاهز")
    except Exception as e:
        logger.error(f"[7] ❌ خطأ في BOT_TOKEN: {e}")
        sys.exit(1)

    # ── [8] تسجيل الـ Handlers ────────────────────────
    logger.info("[8] 📋 تسجيل الـ handlers...")

    admin_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_handlers.admin_broadcast_start,   pattern="^admin_broadcast$"),
            CallbackQueryHandler(admin_handlers.admin_add_product_start, pattern="^admin_add_product$"),
            CallbackQueryHandler(admin_handlers.admin_del_product_start, pattern="^admin_del_product$"),
            CallbackQueryHandler(admin_handlers.admin_welcome_start,     pattern="^admin_edit_welcome$"),
            CallbackQueryHandler(admin_handlers.admin_add_points_start,  pattern="^admin_add_points$"),
        ],
        states={
            WAITING_BROADCAST_MSG:     [MessageHandler(filters.ALL & ~filters.COMMAND,  admin_handlers.admin_broadcast_send)],
            WAITING_PRODUCT_NAME:      [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_product_name)],
            WAITING_PRODUCT_DESC:      [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_product_desc)],
            WAITING_PRODUCT_PRICE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_product_price)],
            WAITING_PRODUCT_STOCK:     [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_product_stock)],
            WAITING_PRODUCT_PHOTO:     [MessageHandler(filters.PHOTO | filters.TEXT,    admin_handlers.admin_product_photo)],
            WAITING_DELETE_PRODUCT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_del_product_confirm)],
            WAITING_WELCOME_MSG:       [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_welcome_save)],
            WAITING_ADD_POINTS_USER:   [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_points_user)],
            WAITING_ADD_POINTS_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_points_amount)],
        },
        fallbacks=[CommandHandler("cancel", admin_handlers.admin_cancel)],
        per_message=False,
    )

    # أوامر المستخدم
    app.add_handler(CommandHandler("start",  user_handlers.cmd_start))
    app.add_handler(CommandHandler("help",   user_handlers.cmd_help))
    app.add_handler(CommandHandler("points", user_handlers.cmd_points))
    app.add_handler(CommandHandler("admin",  admin_handlers.cmd_admin))

    # Admin conversation (قبل callbacks العامة)
    app.add_handler(admin_conv)

    # Callbacks المستخدم
    app.add_handler(CallbackQueryHandler(user_handlers.cb_main_menu,       pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(user_handlers.cb_about,           pattern="^about$"))
    app.add_handler(CallbackQueryHandler(user_handlers.cb_my_points,       pattern="^my_points$"))
    app.add_handler(CallbackQueryHandler(user_handlers.cb_browse_products, pattern="^browse_products$"))
    app.add_handler(CallbackQueryHandler(product_handlers.cb_product_page,    pattern=r"^product_page:\d+$"))
    app.add_handler(CallbackQueryHandler(product_handlers.cb_product_detail,  pattern=r"^product_detail:\d+$"))
    app.add_handler(CallbackQueryHandler(product_handlers.cb_buy_product,     pattern=r"^buy:\d+$"))
    app.add_handler(CallbackQueryHandler(product_handlers.cb_buy_confirm,     pattern=r"^buy_confirm:\d+$"))
    app.add_handler(CallbackQueryHandler(product_handlers.cb_buy_cancel,      pattern="^buy_cancel$"))

    # Callbacks الأدمن
    app.add_handler(CallbackQueryHandler(admin_handlers.cb_admin_panel,  pattern="^admin_panel$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.cb_admin_stats,  pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.cb_admin_orders, pattern="^admin_orders$"))

    # معالج الأخطاء العام
    app.add_error_handler(error_handler)

    logger.info("[8] ✅ كل الـ handlers مسجلة")

    # ── [9] تشغيل Long Polling ────────────────────────
    logger.info("[9] 🚀 Long Polling يبدأ الآن...")
    logger.info(f"    Admin ID : {ADMIN_ID}")
    logger.info("    Ctrl+C   : للإيقاف")

        app.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True
    )


async def error_handler(update, context):
    """معالج الأخطاء - يمنع إيقاف البوت عند أي خطأ"""
    logger.error(f"❌ خطأ: {context.error}", exc_info=True)
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ حدث خطأ مؤقت، يرجى المحاولة مرة أخرى."
            )
    except Exception:
        pass



if __name__ == '__main__':
    import asyncio
    try:
        # محاولة التشغيل العادي
        main()
    except RuntimeError as e:
        # إذا حصل خطأ الـ Event Loop في بايثون 3.14
        if "no current event loop" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            main()
        else:
            raise e

