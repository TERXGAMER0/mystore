"""
handlers/user_handlers.py - معالجات المستخدم العادي
──────────────────────────────────────────────────────
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database.queries import upsert_user, get_user, get_setting
from utils.keyboards import main_menu_keyboard, back_to_menu_keyboard
from config import STORE_NAME

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════
#                  /start
# ══════════════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /start - التسجيل وإظهار القائمة"""
    user = update.effective_user

    # تسجيل أو تحديث المستخدم في Supabase
    await upsert_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    # جلب رسالة الترحيب من الإعدادات
    welcome_msg = await get_setting("welcome_message")
    if not welcome_msg:
        welcome_msg = f"👋 أهلاً *{user.first_name}* في {STORE_NAME}!\nاختر من القائمة أدناه 👇"

    # تخصيص الرسالة باسم المستخدم
    welcome_msg = welcome_msg.replace("{name}", user.first_name or "صديقي")
    welcome_msg = welcome_msg.replace("{store}", STORE_NAME)

    await update.message.reply_text(
        text=welcome_msg,
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN,
    )


# ══════════════════════════════════════════════════════
#                  /help
# ══════════════════════════════════════════════════════

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /help"""
    text = (
        "📖 *دليل الاستخدام*\n\n"
        "🛒 *تصفح المنتجات* - شاهد كل المنتجات المتاحة\n"
        "💰 *رصيد نقاطي* - اعرف رصيدك الحالي من النقاط\n"
        "ℹ️ *عن المتجر* - معلومات عن المتجر\n\n"
        "🎯 *نظام النقاط:* تحصل على نقاط مع كل عملية شراء!\n\n"
        "📞 للتواصل: راجع صفحة المتجر"
    )
    await update.message.reply_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_to_menu_keyboard()
    )


# ══════════════════════════════════════════════════════
#                  /points
# ══════════════════════════════════════════════════════

async def cmd_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /points - عرض الرصيد"""
    user_data = await get_user(update.effective_user.id)
    points = user_data["points"] if user_data else 0

    await update.message.reply_text(
        f"💰 *رصيدك الحالي:* `{points}` نقطة",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_to_menu_keyboard(),
    )


# ══════════════════════════════════════════════════════
#               CALLBACK - رجوع للقائمة
# ══════════════════════════════════════════════════════

async def cb_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الرجوع للقائمة الرئيسية"""
    query = update.callback_query
    await query.answer()

    welcome_msg = await get_setting("welcome_message")
    if not welcome_msg:
        welcome_msg = f"👋 مرحباً بك في {STORE_NAME}!\nاختر من القائمة أدناه 👇"

    try:
        await query.edit_message_text(
            text=welcome_msg,
            reply_markup=main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception:
        # إذا كانت الرسالة الأصلية تحتوي صورة، أرسل رسالة جديدة
        await query.message.reply_text(
            text=welcome_msg,
            reply_markup=main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN,
        )


# ══════════════════════════════════════════════════════
#               CALLBACK - نقاطي
# ══════════════════════════════════════════════════════

async def cb_my_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض رصيد النقاط"""
    query = update.callback_query
    await query.answer()

    user_data = await get_user(query.from_user.id)
    points = user_data["points"] if user_data else 0

    text = (
        f"💰 *رصيدك من النقاط*\n\n"
        f"👤 المستخدم: {query.from_user.first_name}\n"
        f"⭐ النقاط: `{points}` نقطة\n\n"
        f"🎯 اشتر منتجات لتحصل على المزيد من النقاط!"
    )
    await query.edit_message_text(
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_to_menu_keyboard(),
    )


# ══════════════════════════════════════════════════════
#               CALLBACK - عن المتجر
# ══════════════════════════════════════════════════════

async def cb_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معلومات عن المتجر"""
    query = update.callback_query
    await query.answer()

    about_msg = await get_setting("about_message")
    if not about_msg:
        about_msg = f"🏪 *{STORE_NAME}*\nنقدم أفضل المنتجات بأسهل الطرق!"

    await query.edit_message_text(
        text=about_msg,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_to_menu_keyboard(),
    )


# ══════════════════════════════════════════════════════
#               CALLBACK - تصفح المنتجات
# ══════════════════════════════════════════════════════

async def cb_browse_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء تصفح المنتجات - يحول للـ product_handlers"""
    from handlers.product_handlers import show_product_page
    query = update.callback_query
    await query.answer()
    await show_product_page(update, context, page=0)
