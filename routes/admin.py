from functools import wraps

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for

from services.store import admin_orders, update_order_status


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def require_admin(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            if request.path.startswith("/admin/api/"):
                return jsonify({"error": "请先登录管理员账号"}), 401
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == current_app.config["ADMIN_USERNAME"] and password == current_app.config["ADMIN_PASSWORD"]:
            session.clear()
            session["admin_authenticated"] = True
            return redirect(url_for("admin.dashboard"))
        error = "账号或密码不正确"
    return render_template("admin_login.html", error=error)


@admin_bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


@admin_bp.get("/")
@require_admin
def dashboard():
    return render_template("admin.html")


@admin_bp.get("/api/orders")
@require_admin
def get_orders():
    orders = admin_orders(current_app.config["DATABASE"])
    paid_total = sum(order["total"] for order in orders if order["status"] != "cancelled")
    return jsonify({"orders": orders, "summary": {"count": len(orders), "paid_total": paid_total}})


@admin_bp.patch("/api/orders/<int:order_id>/status")
@require_admin
def patch_status(order_id):
    try:
        order = update_order_status(current_app.config["DATABASE"], order_id, (request.get_json(silent=True) or {}).get("status"))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    if not order:
        return jsonify({"error": "订单不存在"}), 404
    return jsonify({"order": order})

