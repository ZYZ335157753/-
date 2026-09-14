from pathlib import Path

from app import create_app


def test_menu_and_order(tmp_path: Path):
    app = create_app({"TESTING": True, "DATABASE": tmp_path / "test.db", "SECRET_KEY": "test"})
    client = app.test_client()
    menu = client.get("/api/v1/menu").get_json()["products"]
    assert len(menu) >= 6
    order = client.post("/api/v1/orders", json={"customer_name": "测试顾客", "items": [{"product_id": menu[0]["id"], "quantity": 2}]} )
    assert order.status_code == 201
    order_no = order.get_json()["order"]["order_no"]
    found = client.get(f"/api/v1/orders/{order_no}")
    assert found.status_code == 200
    assert found.get_json()["order"]["total"] == menu[0]["price"] * 2


def test_rejects_unknown_product(tmp_path: Path):
    app = create_app({"TESTING": True, "DATABASE": tmp_path / "test.db", "SECRET_KEY": "test"})
    response = app.test_client().post("/api/v1/orders", json={"items": [{"product_id": "missing", "quantity": 1}]})
    assert response.status_code == 400

