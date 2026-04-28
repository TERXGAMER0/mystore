"""
╔══════════════════════════════════════════════════════╗
║           BOT STORE - بوت المتجر الاحترافي           ║
║          Telegram Store Bot - Python + Supabase       ║
╚══════════════════════════════════════════════════════╝

المطلوب قبل التشغيل:
1. ضع التوكن وبيانات Supabase في ملف .env
2. شغّل: pip install -r requirements.txt
3. شغّل: python bot.py
"""

import logging
import asyncio
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from config import BOT_TOKEN, ADMIN_ID
from handlers import user_handlers, admin_handlers, product_handlers
from database.db import init_db

# ─── إعداد اللوق ───────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ─── States للـ ConversationHandler ───────────────────
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
    """نقطة البداية - تشغيل البوت"""

    # ── تهيئة قاعدة البيانات ──
    logger.info("🔧 جاري تهيئة قاعدة البيانات...")
    init_db()
    logger.info("✅ قاعدة البيانات جاهزة")

    # ── بناء التطبيق ──
    app = Application.builder().token(BOT_TOKEN).build()

    # ════════════════════════════════════════
    #         ADMIN CONVERSATION
    # ════════════════════════════════════════
    admin_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_handlers.admin_broadcast_start,   pattern="^admin_broadcast$"),
            CallbackQueryHandler(admin_handlers.admin_add_product_start, pattern="^admin_add_product$"),
            CallbackQueryHandler(admin_handlers.admin_del_product_start, pattern="^admin_del_product$"),
            CallbackQueryHandler(admin_handlers.admin_welcome_start,     pattern="^admin_edit_welcome$"),
            CallbackQueryHandler(admin_handlers.admin_add_points_start,  pattern="^admin_add_points$"),
        ],
        states={
            WAITING_BROADCAST_MSG:    [MessageHandler(filters.ALL & ~filters.COMMAND, admin_handlers.admin_broadcast_send)],
            WAITING_PRODUCT_NAME:     [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_product_name)],
            WAITING_PRODUCT_DESC:     [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_product_desc)],
            WAITING_PRODUCT_PRICE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_product_price)],
            WAITING_PRODUCT_STOCK:    [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_product_stock)],
            WAITING_PRODUCT_PHOTO:    [MessageHandler(filters.PHOTO | filters.TEXT,    admin_handlers.admin_product_photo)],
            WAITING_DELETE_PRODUCT_ID:[MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_del_product_confirm)],
            WAITING_WELCOME_MSG:      [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_welcome_save)],
            WAITING_ADD_POINTS_USER:  [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_points_user)],
            WAITING_ADD_POINTS_AMOUNT:[MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.admin_points_amount)],
        },
        fallbacks=[CommandHandler("cancel", admin_handlers.admin_cancel)],
        per_message=False,
    )

    # ════════════════════════════════════════
    #         HANDLERS REGISTRATION
    # ════════════════════════════════════════

    # ── أوامر عامة ──
    app.add_handler(CommandHandler("start",  user_handlers.cmd_start))
    app.add_handler(CommandHandler("help",   user_handlers.cmd_help))
    app.add_handler(CommandHandler("points", user_handlers.cmd_points))
    app.add_handler(CommandHandler("admin",  admin_handlers.cmd_admin))

    # ── Admin Conversation (يجب قبل الـ general callbacks) ──
    app.add_handler(admin_conv)

    # ── Inline Callbacks عامة ──
    app.add_handler(CallbackQueryHandler(user_handlers.cb_main_menu,      pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(user_handlers.cb_about,          pattern="^about$"))
    app.add_handler(CallbackQueryHandler(user_handlers.cb_my_points,      pattern="^my_points$"))
    app.add_handler(CallbackQueryHandler(user_handlers.cb_browse_products,pattern="^browse_products$"))
    app.add_handler(CallbackQueryHandler(product_handlers.cb_product_page, pattern=r"^product_page:\d+$"))
    app.add_handler(CallbackQueryHandler(product_handlers.cb_product_detail,pattern=r"^product_detail:\d+$"))
    app.add_handler(CallbackQueryHandler(product_handlers.cb_buy_product,  pattern=r"^buy:\d+$"))
    app.add_handler(CallbackQueryHandler(product_handlers.cb_buy_confirm,  pattern=r"^buy_confirm:\d+$"))
    app.add_handler(CallbackQueryHandler(product_handlers.cb_buy_cancel,   pattern="^buy_cancel$"))

    # ── Admin Callbacks ──
    app.add_handler(CallbackQueryHandler(admin_handlers.cb_admin_panel,   pattern="^admin_panel$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.cb_admin_stats,   pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.cb_admin_orders,  pattern="^admin_orders$"))

    # ── Error Handler ──
    app.add_error_handler(error_handler)

    # ════════════════════════════════════════
    #         START POLLING
    # ════════════════════════════════════════
    logger.info(f"🚀 البوت يعمل الآن! Admin ID: {ADMIN_ID}")
    logger.info("📡 وضع التشغيل: Polling")
    logger.info("⛔ اضغط Ctrl+C للإيقاف")

    app.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
    )


async def error_handler(update, context):
    """معالج الأخطاء العام - يمنع توقف البوت"""
    logger.error(f"❌ خطأ: {context.error}", exc_info=True)
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ حدث خطأ مؤقت، يرجى المحاولة مرة أخرى."
            )
    except Exception:
        pass


if __name__ == "__main__":
    main()
