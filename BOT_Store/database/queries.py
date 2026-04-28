"""
database/queries.py - كل استعلامات قاعدة البيانات في مكان واحد
────────────────────────────────────────────────────────────────
"""

import logging
from typing import Optional, List, Dict, Any
from .db import get_db

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════
#                     USERS
# ══════════════════════════════════════════════════════

async def upsert_user(telegram_id: int, username: str = None,
                      first_name: str = None, last_name: str = None) -> Dict:
    """إضافة مستخدم جديد أو تحديث بياناته إذا كان موجوداً"""
    try:
        db = get_db()
        data = {
            "telegram_id": telegram_id,
            "username":    username or "",
            "first_name":  first_name or "",
            "last_name":   last_name or "",
        }
        result = db.table("users").upsert(data, on_conflict="telegram_id").execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        logger.error(f"upsert_user error: {e}")
        return {}


async def get_user(telegram_id: int) -> Optional[Dict]:
    """جلب بيانات مستخدم بالمعرف"""
    try:
        db = get_db()
        result = db.table("users").select("*").eq("telegram_id", telegram_id).single().execute()
        return result.data
    except Exception:
        return None


async def get_all_users() -> List[Dict]:
    """جلب كل المستخدمين (للإذاعة)"""
    try:
        db = get_db()
        result = db.table("users").select("telegram_id, first_name").eq("is_banned", False).execute()
        return result.data or []
    except Exception as e:
        logger.error(f"get_all_users error: {e}")
        return []


async def get_users_count() -> int:
    """عدد المستخدمين الكلي"""
    try:
        db = get_db()
        result = db.table("users").select("id", count="exact").execute()
        return result.count or 0
    except Exception:
        return 0


async def update_user_points(telegram_id: int, points_delta: int) -> int:
    """زيادة أو نقصان نقاط مستخدم، يُرجع الرصيد الجديد"""
    try:
        db = get_db()
        user = await get_user(telegram_id)
        if not user:
            return 0
        new_points = max(0, user["points"] + points_delta)
        db.table("users").update({"points": new_points}).eq("telegram_id", telegram_id).execute()
        return new_points
    except Exception as e:
        logger.error(f"update_user_points error: {e}")
        return 0


# ══════════════════════════════════════════════════════
#                    PRODUCTS
# ══════════════════════════════════════════════════════

async def get_active_products() -> List[Dict]:
    """جلب كل المنتجات النشطة"""
    try:
        db = get_db()
        result = db.table("products").select("*").eq("is_active", True).order("id").execute()
        return result.data or []
    except Exception as e:
        logger.error(f"get_active_products error: {e}")
        return []


async def get_product(product_id: int) -> Optional[Dict]:
    """جلب منتج بالمعرف"""
    try:
        db = get_db()
        result = db.table("products").select("*").eq("id", product_id).single().execute()
        return result.data
    except Exception:
        return None


async def add_product(name: str, description: str, price: float,
                      stock: int, photo_id: str = None) -> Optional[Dict]:
    """إضافة منتج جديد"""
    try:
        db = get_db()
        data = {
            "name": name, "description": description,
            "price": price, "stock": stock, "photo_id": photo_id,
        }
        result = db.table("products").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"add_product error: {e}")
        return None


async def delete_product(product_id: int) -> bool:
    """حذف منتج (soft delete - تعطيل فقط)"""
    try:
        db = get_db()
        db.table("products").update({"is_active": False}).eq("id", product_id).execute()
        return True
    except Exception as e:
        logger.error(f"delete_product error: {e}")
        return False


async def update_product_stock(product_id: int, delta: int) -> bool:
    """تحديث المخزون"""
    try:
        db = get_db()
        product = await get_product(product_id)
        if not product:
            return False
        new_stock = max(0, product["stock"] + delta)
        db.table("products").update({"stock": new_stock}).eq("id", product_id).execute()
        return True
    except Exception as e:
        logger.error(f"update_product_stock error: {e}")
        return False


async def get_products_count() -> int:
    """عدد المنتجات النشطة"""
    try:
        db = get_db()
        result = db.table("products").select("id", count="exact").eq("is_active", True).execute()
        return result.count or 0
    except Exception:
        return 0


# ══════════════════════════════════════════════════════
#                     ORDERS
# ══════════════════════════════════════════════════════

async def create_order(user_id: int, product_id: int,
                       quantity: int, total_price: float) -> Optional[Dict]:
    """إنشاء طلب جديد"""
    try:
        db = get_db()
        data = {
            "user_id": user_id, "product_id": product_id,
            "quantity": quantity, "total_price": total_price, "status": "confirmed",
        }
        result = db.table("orders").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"create_order error: {e}")
        return None


async def get_recent_orders(limit: int = 10) -> List[Dict]:
    """جلب آخر الطلبات للأدمن"""
    try:
        db = get_db()
        result = (db.table("orders")
                    .select("*, users(first_name,username), products(name)")
                    .order("created_at", desc=True)
                    .limit(limit)
                    .execute())
        return result.data or []
    except Exception as e:
        logger.error(f"get_recent_orders error: {e}")
        return []


async def get_orders_count() -> int:
    """عدد الطلبات الكلي"""
    try:
        db = get_db()
        result = db.table("orders").select("id", count="exact").execute()
        return result.count or 0
    except Exception:
        return 0


# ══════════════════════════════════════════════════════
#                  BOT SETTINGS
# ══════════════════════════════════════════════════════

async def get_setting(key: str) -> str:
    """جلب إعداد من قاعدة البيانات"""
    try:
        db = get_db()
        result = db.table("bot_settings").select("value").eq("key", key).single().execute()
        return result.data["value"] if result.data else ""
    except Exception:
        return ""


async def set_setting(key: str, value: str) -> bool:
    """تعديل أو إضافة إعداد"""
    try:
        db = get_db()
        db.table("bot_settings").upsert({"key": key, "value": value}).execute()
        return True
    except Exception as e:
        logger.error(f"set_setting error: {e}")
        return False
