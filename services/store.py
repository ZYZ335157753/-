import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


MENU = [
    {"id": "osmanthus-oolong", "name": "桂花乌龙奶茶", "category": "人气轻乳", "price": 16, "description": "金桂蜜香与焙火乌龙，柔和回甘。", "badge": "招牌"},
    {"id": "white-peach-jasmine", "name": "白桃茉莉轻乳", "category": "人气轻乳", "price": 18, "description": "清甜白桃，收束于茉莉茶香。", "badge": "清新"},
    {"id": "coconut-matcha", "name": "生椰抹茶云顶", "category": "云顶特调", "price": 20, "description": "浓郁抹茶与鲜椰乳，绵密不腻。", "badge": "限定"},
    {"id": "mango-pomelo", "name": "山野杨枝甘露", "category": "果茶", "price": 22, "description": "芒果、西柚与西米，明亮饱满。", "badge": "果香"},
    {"id": "rose-grape", "name": "玫瑰青提冰茶", "category": "果茶", "price": 19, "description": "青提清爽，点缀一缕玫瑰。", "badge": "低糖推荐"},
    {"id": "black-sugar", "name": "黑糖波波厚乳", "category": "醇厚奶茶", "price": 17, "description": "现熬黑糖珍珠，醇香厚乳。", "badge": "经典"},
]


def connection(database):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_database(database: Path):
    with connection(database) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
                price INTEGER NOT NULL, description TEXT NOT NULL, badge TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_no TEXT UNIQUE NOT NULL, customer_name TEXT NOT NULL,
                phone TEXT, items_json TEXT NOT NULL, total INTEGER NOT NULL,
                payment_method TEXT NOT NULL, payment_status TEXT NOT NULL,
                status TEXT NOT NULL, created_at TEXT NOT NULL
            );
            """
        )
        for product in MENU:
            conn.execute(
                """INSERT OR IGNORE INTO products (id, name, category, price, description, badge)
                   VALUES (:id, :name, :category, :price, :description, :badge)""",
                product,
            )


def menu(database):
    with connection(database) as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM products ORDER BY rowid")]


def create_order(database, payload):
    customer_name = str(payload.get("customer_name", "到店顾客")).strip()[:40] or "到店顾客"
    phone = str(payload.get("phone", "")).strip()[:30]
    requested_items = payload.get("items", [])
    if not isinstance(requested_items, list) or not requested_items:
        raise ValueError("请至少选择一杯饮品")

    product_map = {product["id"]: product for product in menu(database)}
    items, total = [], 0
    for requested in requested_items:
        product_id = requested.get("product_id") if isinstance(requested, dict) else None
        quantity = requested.get("quantity", 1) if isinstance(requested, dict) else 1
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 0
        if product_id not in product_map or not 1 <= quantity <= 20:
            raise ValueError("订单中包含无效商品或数量")
        product = product_map[product_id]
        item = {"product_id": product_id, "name": product["name"], "unit_price": product["price"], "quantity": quantity, "subtotal": product["price"] * quantity}
        items.append(item)
        total += item["subtotal"]

    order_no = f"YQ{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
    created_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    order = {
        "order_no": order_no, "customer_name": customer_name, "phone": phone,
        "items": items, "total": total, "payment_method": "mock_qr",
        "payment_status": "paid", "status": "preparing", "created_at": created_at,
    }
    with connection(database) as conn:
        cursor = conn.execute(
            """INSERT INTO orders (order_no, customer_name, phone, items_json, total, payment_method, payment_status, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (order_no, customer_name, phone, json.dumps(items, ensure_ascii=False), total,
             order["payment_method"], order["payment_status"], order["status"], created_at),
        )
        order["id"] = cursor.lastrowid
    return order


def order_by_no(database, order_no):
    with connection(database) as conn:
        row = conn.execute("SELECT * FROM orders WHERE order_no = ?", (order_no,)).fetchone()
    return serialize_order(row) if row else None


def serialize_order(row):
    data = dict(row)
    data["items"] = json.loads(data.pop("items_json"))
    return data


def admin_orders(database):
    with connection(database) as conn:
        rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    return [serialize_order(row) for row in rows]


def update_order_status(database, order_id, status):
    allowed = {"preparing", "ready", "completed", "cancelled"}
    if status not in allowed:
        raise ValueError("不支持的订单状态")
    with connection(database) as conn:
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    return serialize_order(row) if row else None

