from flask import Blueprint, current_app, jsonify, request, render_template

from services.store import create_order, menu, order_by_no


api_bp = Blueprint("api", __name__)


@api_bp.get("/")
def index():
    return render_template("index.html")


@api_bp.get("/api/v1/menu")
def get_menu():
    return jsonify({"store": "云栖茶事", "currency": "CNY", "products": menu(current_app.config["DATABASE"])})


@api_bp.post("/api/v1/orders")
def post_order():
    try:
        order = create_order(current_app.config["DATABASE"], request.get_json(silent=True) or {})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({"message": "订单已支付，正在制作", "order": order}), 201


@api_bp.get("/api/v1/orders/<order_no>")
def get_order(order_no):
    order = order_by_no(current_app.config["DATABASE"], order_no)
    if not order:
        return jsonify({"error": "未找到该订单"}), 404
    return jsonify({"order": order})


@api_bp.post("/api/v1/payments/mock")
def mock_payment():
    """Payment adapter placeholder. Replace this route with WeChat/Alipay provider callbacks."""
    return jsonify({"provider": "mock", "status": "paid", "message": "开发环境模拟支付成功"})

