"""
handlers/product_handlers.py - عرض المنتجات والشراء
──────────────────────────────────────────────────────
"""

import logging
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database.queries import (
    get_active_products, get_product, get_user,
    create_order, update_user_points, update_product_stock,
)
from utils.keyboards import (
    products_nav_keyboard, product_detail_keyboard,
    buy_confirm_keyboard, back_to_menu_keyboard,
)
from config import STORE_CURRENCY, POINTS_PER_PURCHASE

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════
#            عرض منتج واحد (بالصفحة)
# ══════════════════════════════════════════════════════

async def show_product_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    """عرض منتج واحد مع أزرار التنقل"""
    query = update.callback_query

    products = await get_active_products()

    if not products:
        await query.edit_message_text(
            "😔 لا توجد منتجات متاحة حالياً.\nعد لاحقاً!",
            reply_markup=back_to_menu_keyboard(),
        )
        return

    # التأكد أن الصفحة ضمن الحدود
    page = max(0, min(page, len(products) - 1))
    product = products[page]

    caption = (
        f"🛍️ *{product['name']}*\n\n"
        f"📝 {product.get('description', 'لا يوجد وصف')}\n\n"
        f"💵 السعر: *{product['price']} {STORE_CURRENCY}*\n"
        f"📦 المخزون: {'✅ متوفر' if product['stock'] > 0 else '❌ نفذ'}"
    )

    keyboard = products_nav_keyboard(page, len(products), product["id"])

    try:
        if product.get("photo_id"):
            # رسالة مع صورة
            try:
                await query.edit_message_media(
                    media=InputMediaPhoto(
                        media=product["photo_id"],
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN,
                    ),
                    reply_markup=keyboard,
                )
            except Exception:
                await query.edit_message_caption(
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard,
                )
        else:
            await query.edit_message_text(
                text=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
            )
    except Exception as e:
        logger.warning(f"show_product_page error: {e}")
        # إرسال رسالة جديدة كبديل
        if product.get("photo_id"):
            await query.message.reply_photo(
                photo=product["photo_id"],
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
            )
        else:
            await query.message.reply_text(
                text=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
            )


# ══════════════════════════════════════════════════════
#            Callback: الصفحة التالية/السابقة
# ══════════════════════════════════════════════════════

async def cb_product_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التنقل بين المنتجات"""
    query = update.callback_query
    await query.answer()

    page = int(query.data.split(":")[1])
    await show_product_page(update, context, page)


# ══════════════════════════════════════════════════════
#            Callback: تفاصيل المنتج
# ══════════════════════════════════════════════════════

async def cb_product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض تفاصيل منتج كاملة"""
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split(":")[1])
    product = await get_product(product_id)

    if not product:
        await query.answer("❌ المنتج غير موجود!", show_alert=True)
        return

    # حفظ الصفحة الحالية للرجوع إليها
    products = await get_active_products()
    current_page = next((i for i, p in enumerate(products) if p["id"] == product_id), 0)

    text = (
        f"🛍️ *{product['name']}*\n"
        f"{'─' * 25}\n\n"
        f"📝 *الوصف:*\n{product.get('description', 'لا يوجد وصف')}\n\n"
        f"💵 *السعر:* `{product['price']} {STORE_CURRENCY}`\n"
        f"📦 *المخزون:* {'✅ متوفر' if product['stock'] > 0 else '❌ نفذ المخزون'}\n"
        f"🎯 *نقاط الشراء:* +{POINTS_PER_PURCHASE} نقطة"
    )

    keyboard = product_detail_keyboard(product_id, current_page, product["stock"] > 0)

    try:
        await query.edit_message_text(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
        )
    except Exception:
        await query.message.reply_text(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
        )


# ══════════════════════════════════════════════════════
#            Callback: الضغط على "شراء"
# ══════════════════════════════════════════════════════

async def cb_buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض تأكيد الشراء"""
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split(":")[1])
    product = await get_product(product_id)

    if not product or product["stock"] <= 0:
        await query.answer("❌ هذا المنتج غير متوفر!", show_alert=True)
        return

    text = (
        f"🛒 *تأكيد الشراء*\n\n"
        f"📦 المنتج: *{product['name']}*\n"
        f"💵 السعر: *{product['price']} {STORE_CURRENCY}*\n"
        f"🎯 نقاط مكتسبة: +{POINTS_PER_PURCHASE}\n\n"
        f"هل تريد تأكيد الشراء؟"
    )

    await query.edit_message_text(
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=buy_confirm_keyboard(product_id),
    )


# ══════════════════════════════════════════════════════
#            Callback: تأكيد الشراء
# ══════════════════════════════════════════════════════

async def cb_buy_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنفيذ عملية الشراء الفعلية"""
    query = update.callback_query
    await query.answer("⏳ جاري المعالجة...")

    product_id = int(query.data.split(":")[1])
    user_id = query.from_user.id

    # جلب المنتج
    product = await get_product(product_id)
    if not product or product["stock"] <= 0:
        await query.edit_message_text(
            "❌ عذراً، نفذ المنتج قبل إتمام طلبك!",
            reply_markup=back_to_menu_keyboard(),
        )
        return

    # إنشاء الطلب
    order = await create_order(
        user_id=user_id,
        product_id=product_id,
        quantity=1,
        total_price=float(product["price"]),
    )

    if not order:
        await query.edit_message_text(
            "❌ حدث خطأ في إتمام الطلب، حاول مرة أخرى.",
            reply_markup=back_to_menu_keyboard(),
        )
        return

    # تحديث المخزون
    await update_product_stock(product_id, -1)

    # إضافة النقاط
    new_points = await update_user_points(user_id, POINTS_PER_PURCHASE)

    # رسالة النجاح
    success_text = (
        f"✅ *تم الشراء بنجاح!*\n\n"
        f"📦 المنتج: *{product['name']}*\n"
        f"💵 المبلغ: *{product['price']} {STORE_CURRENCY}*\n"
        f"🎯 نقاط مضافة: *+{POINTS_PER_PURCHASE}*\n"
        f"⭐ رصيدك الجديد: *{new_points} نقطة*\n\n"
        f"🙏 شكراً لتسوقك معنا!"
    )

    await query.edit_message_text(
        text=success_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_to_menu_keyboard(),
    )

    logger.info(f"✅ طلب جديد - المستخدم: {user_id} | المنتج: {product['name']}")


# ══════════════════════════════════════════════════════
#            Callback: إلغاء الشراء
# ══════════════════════════════════════════════════════

async def cb_buy_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء عملية الشراء"""
    query = update.callback_query
    await query.answer("تم الإلغاء ✋")

    await query.edit_message_text(
        "❌ *تم إلغاء الطلب*\n\nيمكنك العودة للتسوق في أي وقت!",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_to_menu_keyboard(),
    )
