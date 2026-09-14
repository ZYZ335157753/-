# 云栖茶事 · 奶茶点单与收款演示

一个可在 VS Code 中运行的 Python/Flask 小程序：顾客可浏览菜单、加入购物袋、以**模拟支付**完成下单、查询订单；管理员可登录后台查看订单并更新制作状态。视觉素材为本项目生成并随仓库交付。

> 当前收款为本地演示接口，**不会发起真实支付或真实扣款**。接入微信支付、支付宝等前，请按其商户平台要求完成证书、签名、回调验签与金额校验。

## 本地启动

在 VS Code 终端执行（Windows PowerShell）：

```powershell
cd "C:\Users\33515\Documents\ChatGPT\codex test01\milk-tea-ordering"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

打开 `http://127.0.0.1:5000`。运行测试：`pytest -q`。

## 管理员账号（演示用）

- 地址：`http://127.0.0.1:5000/admin/`
- 账号：`admin`
- 密码：`Tea2026!`

部署前复制 `.env.example` 为 `.env`，并为 `SECRET_KEY`、`ADMIN_USERNAME`、`ADMIN_PASSWORD` 设置安全值。生产环境应改用数据库中的密码哈希、HTTPS 和登录限流。

## 可复用接口

| 目的 | 方法与地址 |
| --- | --- |
| 获取茶单 | `GET /api/v1/menu` |
| 创建订单（模拟已支付） | `POST /api/v1/orders` |
| 查询订单 | `GET /api/v1/orders/{order_no}` |
| 支付适配占位 | `POST /api/v1/payments/mock` |
| 管理订单 | `GET /admin/api/orders` |
| 改订单状态 | `PATCH /admin/api/orders/{id}/status` |

创建订单示例：

```json
{
  "customer_name": "林小姐",
  "phone": "13800000000",
  "items": [{"product_id": "osmanthus-oolong", "quantity": 2}]
}
```

## 对接微信小程序或其他前端

小程序/其他平台只需调用 `/api/v1/menu` 和 `/api/v1/orders`；将前端基址配置为部署域名。在生产实现中，建议保留 `services/store.py` 的订单逻辑，将 `POST /api/v1/payments/mock` 替换为独立支付适配器：创建预支付单 → 前端调起支付 → 支付回调验签 → 在服务端更新订单支付状态。不要相信客户端传入的价格。

`CORS_ORIGINS` 支持用逗号配置允许访问接口的前端域名；本地默认 `*` 仅为开发便利。

