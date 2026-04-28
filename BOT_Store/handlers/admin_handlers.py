"""
handlers/admin_handlers.py - لوحة تحكم الأدمن الكاملة
──────────────────────────────────────────────────────
يتضمن: الإذاعة، إدارة المنتجات، الإعدادات، الإحصائيات
"""

import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from database.queries import (
    get_users_count, get_products_count, get_orders_count,
    get_all_users, add_product, delete_product, get_product,
    get_setting, set_setting, get_recent_orders, update_user_points, get_user,
)
from utils.keyboards import admin_panel_keyboard, back_to_menu_keyboard, cancel_keyboard
from config import ADMIN_ID, STORE_NAME

logger = logging.getLogger(__name__)

# States (تطابق التعريف في bot.py)
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


# ══════════════════════════════════════════════════════
#               التحقق من الأدمن
# ══════════════════════════════════════════════════════

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ══════════════════════════════════════════════════════
#               /admin - فتح لوحة التحكم
# ══════════════════════════════════════════════════════

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /admin - فتح لوحة التحكم"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ ليس لديك صلاحية للوصول!")
        return

    await update.message.reply_text(
        f"👑 *لوحة التحكم - {STORE_NAME}*\n\nاختر العملية:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=admin_panel_keyboard(),
    )


async def cb_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⛔ ليس لديك صلاحية!", show_alert=True)
        return
    await query.answer()
    await query.edit_message_text(
        f"👑 *لوحة التحكم - {STORE_NAME}*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=admin_panel_keyboard(),
    )


# ══════════════════════════════════════════════════════
#               الإحصائيات
# ══════════════════════════════════════════════════════

async def cb_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⛔", show_alert=True)
        return
    await query.answer("⏳ جاري جلب الإحصائيات...")

    users   = await get_users_count()
    products = await get_products_count()
    orders  = await get_orders_count()

    text = (
        f"📊 *إحصائيات المتجر*\n"
        f"{'─' * 25}\n\n"
        f"👥 المستخدمون: `{users}`\n"
        f"📦 المنتجات: `{products}`\n"
        f"🛒 الطلبات: `{orders}`\n"
    )

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ رجوع للوحة", callback_data="admin_panel")]])
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


# ══════════════════════════════════════════════════════
#               آخر الطلبات
# ══════════════════════════════════════════════════════

async def cb_admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⛔", show_alert=True)
        return
    await query.answer()

    orders = await get_recent_orders(limit=8)
    if not orders:
        text = "📋 لا توجد طلبات حتى الآن."
    else:
        lines = ["📋 *آخر الطلبات:*\n"]
        for o in orders:
            user_name  = o.get("users", {}).get("first_name", "؟") if o.get("users") else "؟"
            prod_name  = o.get("products", {}).get("name", "؟") if o.get("products") else "؟"
            lines.append(f"• {user_name} ← {prod_name} ({o['total_price']})")
        text = "\n".join(lines)

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ رجوع للوحة", callback_data="admin_panel")]])
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


# ══════════════════════════════════════════════════════
#               الإذاعة (Broadcast)
# ══════════════════════════════════════════════════════

async def admin_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⛔", show_alert=True)
        return ConversationHandler.END
    await query.answer()
    await query.edit_message_text(
        "📢 *الإذاعة*\n\nأرسل الرسالة التي تريد إذاعتها لجميع المستخدمين.\n"
        "يمكنك إرسال نص أو صورة مع تعليق.\n\n"
        "أو أرسل /cancel للإلغاء.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=cancel_keyboard(),
    )
    return WAITING_BROADCAST_MSG


async def admin_broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال الإذاعة لكل المستخدمين"""
    if not is_admin(update.effective_user.id):
        return ConversationHandler.END

    users = await get_all_users()
    total = len(users)
    success = 0
    failed  = 0

    status_msg = await update.message.reply_text(f"📡 جاري الإذاعة لـ {total} مستخدم...")

    for user in users:
        try:
            if update.message.photo:
                # إذاعة صورة
                await context.bot.send_photo(
                    chat_id=user["telegram_id"],
                    photo=update.message.photo[-1].file_id,
                    caption=update.message.caption or "",
                )
            else:
                # إذاعة نص
                await context.bot.send_message(
                    chat_id=user["telegram_id"],
                    text=update.message.text,
                    parse_mode=ParseMode.MARKDOWN,
                )
            success += 1
        except Exception:
            failed += 1

        # تحديث كل 20 مستخدم
        if (success + failed) % 20 == 0:
            try:
                await status_msg.edit_text(
                    f"📡 جاري... {success + failed}/{total}\n"
                    f"✅ نجح: {success} | ❌ فشل: {failed}"
                )
            except Exception:
                pass
        await asyncio.sleep(0.05)  # منع الـ Rate Limit

    await status_msg.edit_text(
        f"✅ *انتهت الإذاعة!*\n\n"
        f"✅ وصلت: {success}\n❌ فشلت: {failed}\n📊 الإجمالي: {total}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=admin_panel_keyboard(),
    )
    return ConversationHandler.END


# ══════════════════════════════════════════════════════
#               إضافة منتج
# ══════════════════════════════════════════════════════

async def admin_add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⛔", show_alert=True)
        return ConversationHandler.END
    await query.answer()
    context.user_data["new_product"] = {}
    await query.edit_message_text(
        "➕ *إضافة منتج جديد*\n\nأرسل *اسم المنتج:*\n\nأو /cancel للإلغاء",
        parse_mode=ParseMode.MARKDOWN,
    )
    return WAITING_PRODUCT_NAME


async def admin_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_product"]["name"] = update.message.text.strip()
    await update.message.reply_text("📝 الآن أرسل *وصف المنتج:*", parse_mode=ParseMode.MARKDOWN)
    return WAITING_PRODUCT_DESC


async def admin_product_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_product"]["description"] = update.message.text.strip()
    await update.message.reply_text("💵 أرسل *سعر المنتج* (أرقام فقط):", parse_mode=ParseMode.MARKDOWN)
    return WAITING_PRODUCT_PRICE


async def admin_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text.strip())
        context.user_data["new_product"]["price"] = price
        await update.message.reply_text("📦 أرسل *الكمية المتوفرة* (عدد صحيح):", parse_mode=ParseMode.MARKDOWN)
        return WAITING_PRODUCT_STOCK
    except ValueError:
        await update.message.reply_text("❌ السعر يجب أن يكون رقماً. حاول مرة أخرى:")
        return WAITING_PRODUCT_PRICE


async def admin_product_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        stock = int(update.message.text.strip())
        context.user_data["new_product"]["stock"] = stock
        await update.message.reply_text(
            "📷 أرسل *صورة المنتج*، أو أرسل `skip` لتخطي الصورة:",
            parse_mode=ParseMode.MARKDOWN,
        )
        return WAITING_PRODUCT_PHOTO
    except ValueError:
        await update.message.reply_text("❌ الكمية يجب أن تكون عدداً صحيحاً:")
        return WAITING_PRODUCT_STOCK


async def admin_product_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استقبال صورة المنتج أو تخطيها"""
    photo_id = None
    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
    elif update.message.text and update.message.text.lower() == "skip":
        photo_id = None
    else:
        await update.message.reply_text("❌ أرسل صورة أو اكتب `skip`:")
        return WAITING_PRODUCT_PHOTO

    pd = context.user_data.get("new_product", {})
    product = await add_product(
        name=pd["name"], description=pd["description"],
        price=pd["price"], stock=pd["stock"], photo_id=photo_id,
    )

    if product:
        await update.message.reply_text(
            f"✅ *تم إضافة المنتج بنجاح!*\n\n"
            f"📦 الاسم: {product['name']}\n"
            f"💵 السعر: {product['price']}\n"
            f"📊 الكمية: {product['stock']}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=admin_panel_keyboard(),
        )
    else:
        await update.message.reply_text("❌ فشل إضافة المنتج!", reply_markup=admin_panel_keyboard())

    context.user_data.pop("new_product", None)
    return ConversationHandler.END


# ══════════════════════════════════════════════════════
#               حذف منتج
# ══════════════════════════════════════════════════════

async def admin_del_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⛔", show_alert=True)
        return ConversationHandler.END
    await query.answer()
    await query.edit_message_text(
        "🗑️ *حذف منتج*\n\nأرسل *معرّف (ID) المنتج* الذي تريد حذفه:\n\n"
        "يمكنك الحصول على الـ ID من قائمة المنتجات.\n\nأو /cancel للإلغاء",
        parse_mode=ParseMode.MARKDOWN,
    )
    return WAITING_DELETE_PRODUCT_ID


async def admin_del_product_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        product_id = int(update.message.text.strip())
        product = await get_product(product_id)
        if not product:
            await update.message.reply_text("❌ المنتج غير موجود!")
            return WAITING_DELETE_PRODUCT_ID

        success = await delete_product(product_id)
        if success:
            await update.message.reply_text(
                f"✅ تم حذف المنتج: *{product['name']}*",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=admin_panel_keyboard(),
            )
        else:
            await update.message.reply_text("❌ فشل حذف المنتج!", reply_markup=admin_panel_keyboard())
    except ValueError:
        await update.message.reply_text("❌ أرسل رقم صحيح (ID):")
        return WAITING_DELETE_PRODUCT_ID

    return ConversationHandler.END


# ══════════════════════════════════════════════════════
#               تعديل رسالة الترحيب
# ══════════════════════════════════════════════════════

async def admin_welcome_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⛔", show_alert=True)
        return ConversationHandler.END
    await query.answer()

    current = await get_setting("welcome_message")
    await query.edit_message_text(
        f"✏️ *تعديل رسالة الترحيب*\n\n"
        f"الرسالة الحالية:\n`{current}`\n\n"
        f"يمكنك استخدام {{name}} ليُستبدل باسم المستخدم.\n\n"
        f"أرسل الرسالة الجديدة أو /cancel للإلغاء:",
        parse_mode=ParseMode.MARKDOWN,
    )
    return WAITING_WELCOME_MSG


async def admin_welcome_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_msg = update.message.text.strip()
    success = await set_setting("welcome_message", new_msg)
    if success:
        await update.message.reply_text(
            f"✅ تم تحديث رسالة الترحيب!\n\nمعاينة:\n{new_msg}",
            reply_markup=admin_panel_keyboard(),
        )
    else:
        await update.message.reply_text("❌ فشل التحديث!", reply_markup=admin_panel_keyboard())
    return ConversationHandler.END


# ══════════════════════════════════════════════════════
#               إضافة نقاط لمستخدم
# ══════════════════════════════════════════════════════

async def admin_add_points_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⛔", show_alert=True)
        return ConversationHandler.END
    await query.answer()
    await query.edit_message_text(
        "🎯 *إضافة نقاط لمستخدم*\n\nأرسل *معرّف المستخدم (Telegram ID):*\n\nأو /cancel للإلغاء",
        parse_mode=ParseMode.MARKDOWN,
    )
    return WAITING_ADD_POINTS_USER


async def admin_points_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = int(update.message.text.strip())
        user = await get_user(user_id)
        if not user:
            await update.message.reply_text("❌ المستخدم غير موجود في قاعدة البيانات!")
            return WAITING_ADD_POINTS_USER
        context.user_data["points_target_id"] = user_id
        context.user_data["points_target_name"] = user.get("first_name", str(user_id))
        await update.message.reply_text(
            f"👤 المستخدم: *{user.get('first_name', user_id)}*\n"
            f"💰 رصيده الحالي: `{user['points']}` نقطة\n\n"
            f"أرسل عدد النقاط المراد إضافتها (سالبة للخصم):",
            parse_mode=ParseMode.MARKDOWN,
        )
        return WAITING_ADD_POINTS_AMOUNT
    except ValueError:
        await update.message.reply_text("❌ أرسل رقم صحيح (Telegram ID):")
        return WAITING_ADD_POINTS_USER


async def admin_points_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text.strip())
        target_id   = context.user_data["points_target_id"]
        target_name = context.user_data["points_target_name"]

        new_points = await update_user_points(target_id, amount)
        sign = "+" if amount >= 0 else ""
        await update.message.reply_text(
            f"✅ *تم تعديل النقاط!*\n\n"
            f"👤 المستخدم: {target_name}\n"
            f"📊 التغيير: `{sign}{amount}` نقطة\n"
            f"💰 الرصيد الجديد: `{new_points}` نقطة",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=admin_panel_keyboard(),
        )
    except (ValueError, KeyError):
        await update.message.reply_text("❌ حدث خطأ، حاول مرة أخرى:")
        return WAITING_ADD_POINTS_AMOUNT

    return ConversationHandler.END


# ══════════════════════════════════════════════════════
#               إلغاء أي عملية
# ══════════════════════════════════════════════════════

async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء أي ConversationHandler جار"""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ تم الإلغاء.",
        reply_markup=admin_panel_keyboard() if is_admin(update.effective_user.id) else back_to_menu_keyboard(),
    )
    return ConversationHandler.END
