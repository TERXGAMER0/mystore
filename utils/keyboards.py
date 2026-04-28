"""
utils/keyboards.py - كل لوحات المفاتيح (Inline Keyboards)
──────────────────────────────────────────────────────────
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """القائمة الرئيسية للمستخدم"""
    buttons = [
        [InlineKeyboardButton("🛒 تصفح المنتجات", callback_data="browse_products")],
        [
            InlineKeyboardButton("💰 رصيد نقاطي",  callback_data="my_points"),
            InlineKeyboardButton("ℹ️ عن المتجر",    callback_data="about"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def products_nav_keyboard(current_page: int, total: int, product_id: int) -> InlineKeyboardMarkup:
    """أزرار التنقل بين المنتجات"""
    nav_row = []

    if current_page > 0:
        nav_row.append(InlineKeyboardButton("◀️ السابق", callback_data=f"product_page:{current_page - 1}"))

    nav_row.append(InlineKeyboardButton(f"📌 {current_page + 1}/{total}", callback_data="noop"))

    if current_page < total - 1:
        nav_row.append(InlineKeyboardButton("التالي ▶️", callback_data=f"product_page:{current_page + 1}"))

    buttons = [
        nav_row,
        [InlineKeyboardButton("🔍 تفاصيل المنتج", callback_data=f"product_detail:{product_id}")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)


def product_detail_keyboard(product_id: int, current_page: int, in_stock: bool) -> InlineKeyboardMarkup:
    """أزرار صفحة تفاصيل المنتج"""
    buttons = []
    if in_stock:
        buttons.append([InlineKeyboardButton("🛒 شراء الآن", callback_data=f"buy:{product_id}")])
    else:
        buttons.append([InlineKeyboardButton("❌ غير متوفر", callback_data="noop")])

    buttons.append([InlineKeyboardButton("◀️ رجوع للمنتجات", callback_data=f"product_page:{current_page}")])
    buttons.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def buy_confirm_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """تأكيد الشراء"""
    buttons = [
        [
            InlineKeyboardButton("✅ تأكيد الشراء",  callback_data=f"buy_confirm:{product_id}"),
            InlineKeyboardButton("❌ إلغاء",         callback_data="buy_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """زر الرجوع للقائمة فقط"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
    ])


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """لوحة تحكم الأدمن"""
    buttons = [
        [
            InlineKeyboardButton("📊 الإحصائيات",    callback_data="admin_stats"),
            InlineKeyboardButton("📋 آخر الطلبات",   callback_data="admin_orders"),
        ],
        [InlineKeyboardButton("📢 إذاعة رسالة",      callback_data="admin_broadcast")],
        [
            InlineKeyboardButton("➕ إضافة منتج",    callback_data="admin_add_product"),
            InlineKeyboardButton("🗑️ حذف منتج",     callback_data="admin_del_product"),
        ],
        [InlineKeyboardButton("✏️ تعديل رسالة الترحيب", callback_data="admin_edit_welcome")],
        [InlineKeyboardButton("🎯 إضافة نقاط لمستخدم",  callback_data="admin_add_points")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية",    callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)


def cancel_keyboard() -> InlineKeyboardMarkup:
    """زر إلغاء العملية الحالية"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ إلغاء", callback_data="main_menu")]
    ])
