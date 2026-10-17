from datetime import datetime, timedelta
import sqlite3
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from payments import get_payment_provider
from licenses.service import create_license_for_order
from database import DB_PATH, get_db

ORDER_EXPIRE_MINUTES = 1
SUPPORTED_PAYMENT_METHODS = {"wechat", "alipay", "usdt"}
SUPPORTED_ORDER_STATUSES = {"pending", "paid", "cancelled", "expired"}

app = FastAPI(title="LOZENO Backend", version="1.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

def parse_datetime(value):
    try: return datetime.fromisoformat(value) if value else None
    except (TypeError, ValueError): return None

def init_db():
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_no TEXT UNIQUE NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'USD',
                payment_method TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                expires_at TEXT,
                paid_at TEXT
            )
            """
        )
        order_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(orders)").fetchall()
        }
        if "expires_at" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN expires_at TEXT")
        if "paid_at" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN paid_at TEXT")
        conn.execute(
            """
            UPDATE orders
            SET expires_at = datetime(created_at, ?)
            WHERE expires_at IS NULL OR expires_at = ''
            """,
            (f"+{ORDER_EXPIRE_MINUTES} minutes",),
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT UNIQUE NOT NULL,
                order_no TEXT UNIQUE NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                license_type TEXT NOT NULL DEFAULT 'single_account',
                status TEXT NOT NULL DEFAULT 'active',
                account TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

init_db()

class CreateOrder(BaseModel):
    product_id: int = Field(gt=0)
    product_name: str = Field(min_length=1, max_length=200)
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=1, max_length=10)
    payment_method: str

class PaymentUpdate(BaseModel): status: str
class LicenseBind(BaseModel): account: str = Field(min_length=1, max_length=100)
class LicenseVerify(BaseModel):
    license_key: str = Field(min_length=1, max_length=200)
    product_id: int = Field(gt=0)
    account: str = Field(min_length=1, max_length=100)
    platform: str = "MT5"
    broker: str = ""

def generate_order_no(): return f"LZ{datetime.now():%Y%m%d%H%M%S}{uuid.uuid4().hex[:8].upper()}"

def check_expired(conn, order):
    if not order or order["status"] != "pending":
        return order
    expires_at = parse_datetime(order["expires_at"])
    if expires_at and expires_at <= datetime.now():
        conn.execute(
            "UPDATE orders SET status='expired' WHERE order_no=? AND status='pending'",
            (order["order_no"],),
        )
        conn.commit()
        return conn.execute(
            "SELECT * FROM orders WHERE order_no=?", (order["order_no"],)
        ).fetchone()
    return order

def get_license_expiry_error(conn, row, license_key):
    if not row["expires_at"]:
        return None
    expires_at = parse_datetime(row["expires_at"])
    if expires_at and expires_at <= datetime.now():
        conn.execute(
            "UPDATE licenses SET status='expired' WHERE license_key=? AND status='active'",
            (license_key,),
        )
        conn.commit()
        return "授权已过期"
    return None

@app.get("/")
def root(): return {"name": "LOZENO Backend", "status": "running", "version": app.version}

@app.get("/api/health")
def health(): return {"status": "ok", "database": str(DB_PATH)}

@app.post("/api/orders")
def create_order(order: CreateOrder):
    product_name = order.product_name.strip()
    currency = order.currency.strip().upper()
    payment_method = order.payment_method.strip().lower()
    if not product_name:
        raise HTTPException(status_code=400, detail="产品名称不能为空")
    if payment_method not in SUPPORTED_PAYMENT_METHODS:
        raise HTTPException(status_code=400, detail="不支持的支付方式")
    try:
        provider = get_payment_provider(payment_method)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    now = datetime.now()
    order_no = generate_order_no()
    created_at = now.isoformat(timespec="seconds")
    expires_at = (now + timedelta(minutes=ORDER_EXPIRE_MINUTES)).isoformat(timespec="seconds")

    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO orders (
                order_no, product_id, product_name, amount, currency,
                payment_method, status, created_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
            """,
            (
                order_no, order.product_id, product_name, order.amount,
                currency, payment_method, created_at, expires_at,
            ),
        )
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail="创建订单失败") from exc
    finally:
        conn.close()

    try:
        payment = provider.create_payment(order_no, order.amount, product_name)
    except Exception as exc:
        conn = get_db()
        try:
            conn.execute(
                "UPDATE orders SET status='cancelled' WHERE order_no=? AND status='pending'",
                (order_no,),
            )
            conn.commit()
        finally:
            conn.close()
        raise HTTPException(status_code=502, detail="创建支付信息失败，请重新下单") from exc

    return {
        "success": True,
        "order": {
            "order_no": order_no,
            "product_id": order.product_id,
            "product_name": product_name,
            "amount": order.amount,
            "currency": currency,
            "payment_method": payment_method,
            "status": "pending",
            "created_at": created_at,
            "expires_at": expires_at,
            "payment": payment,
        },
    }

@app.get("/api/orders/{order_no}")
def get_order(order_no: str):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM orders WHERE order_no=?", (order_no,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="订单不存在")
        row = check_expired(conn, row)
        return {"success": True, "order": dict(row)}
    finally:
        conn.close()

@app.patch("/api/orders/{order_no}/status")
def update_order_status(order_no: str, payment: PaymentUpdate):
    """本接口仅用于本地开发测试模拟支付；上线前必须替换为已验签的支付回调。"""
    if payment.status not in SUPPORTED_ORDER_STATUSES:
        raise HTTPException(status_code=400, detail="无效的订单状态")

    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM orders WHERE order_no=?", (order_no,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="订单不存在")
        row = check_expired(conn, row)
        if row["status"] == "expired" and payment.status == "paid":
            raise HTTPException(status_code=400, detail="订单已过期，无法支付")
        if row["status"] == "paid" and payment.status != "paid":
            raise HTTPException(status_code=400, detail="订单已经支付，不能修改状态")
        if row["status"] == "cancelled" and payment.status == "paid":
            raise HTTPException(status_code=400, detail="订单已结束，不能标记为已支付")

        paid_at = row["paid_at"]
        if payment.status == "paid" and not paid_at:
            paid_at = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            "UPDATE orders SET status=?, paid_at=? WHERE order_no=?",
            (payment.status, paid_at, order_no),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM orders WHERE order_no=?", (order_no,)
        ).fetchone()
    finally:
        conn.close()

    license_data = None
    if payment.status == "paid":
        license_data = create_license_for_order(row, str(DB_PATH))
    return {"success": True, "order": dict(row), "license": license_data}

@app.get("/api/orders")
def list_orders():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
        return {"success": True, "orders": [dict(row) for row in rows]}
    finally:
        conn.close()

@app.get("/api/licenses/{license_key}")
def get_license(license_key: str):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM licenses WHERE license_key=?", (license_key,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="授权码不存在")
        return {"success": True, "license": dict(row)}
    finally:
        conn.close()

@app.get("/api/orders/{order_no}/license")
def get_order_license(order_no: str):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM licenses WHERE order_no=?", (order_no,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="该订单暂无授权")
        return {"success": True, "license": dict(row)}
    finally:
        conn.close()

@app.post("/api/licenses/{license_key}/bind")
def bind_license(license_key: str, data: LicenseBind):
    account = data.account.strip()
    if not account:
        raise HTTPException(status_code=400, detail="MT5账户不能为空")

    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT * FROM licenses WHERE license_key=?", (license_key.strip(),)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="授权码不存在")
        if row["status"] != "active":
            raise HTTPException(status_code=400, detail="授权不可用")
        expiry_error = get_license_expiry_error(conn, row, license_key.strip())
        if expiry_error:
            raise HTTPException(status_code=400, detail=expiry_error)
        if row["account"] and row["account"] != account:
            raise HTTPException(status_code=409, detail="授权码已绑定其他MT5账户")
        if not row["account"]:
            conn.execute(
                "UPDATE licenses SET account=? WHERE license_key=? AND account IS NULL",
                (account, license_key.strip()),
            )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM licenses WHERE license_key=?", (license_key.strip(),)
        ).fetchone()
        return {"success": True, "message": "授权绑定成功", "license": dict(row)}
    except HTTPException:
        conn.rollback()
        raise
    except sqlite3.Error as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail="绑定授权时数据库操作失败") from exc
    finally:
        conn.close()

@app.post("/api/licenses/verify")
def verify_license(data: LicenseVerify):
    license_key = data.license_key.strip()
    account = data.account.strip()
    platform = data.platform.strip().upper()
    if not license_key:
        return {"authorized": False, "reason": "授权码不能为空"}
    if not account:
        return {"authorized": False, "reason": "MT5账户不能为空"}
    if platform != "MT5":
        return {"authorized": False, "reason": "当前仅支持MT5平台"}

    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT * FROM licenses WHERE license_key=?", (license_key,)
        ).fetchone()
        if not row:
            conn.rollback()
            return {"authorized": False, "reason": "授权码不存在"}
        if row["product_id"] != data.product_id:
            conn.rollback()
            return {"authorized": False, "reason": "授权产品不匹配"}
        if row["status"] != "active":
            conn.rollback()
            return {"authorized": False, "reason": f"授权状态无效: {row['status']}"}
        expiry_error = get_license_expiry_error(conn, row, license_key)
        if expiry_error:
            conn.rollback()
            return {"authorized": False, "reason": expiry_error}
        if row["account"] and row["account"] != account:
            conn.rollback()
            return {"authorized": False, "reason": "授权码已绑定其他MT5账户"}
        if not row["account"]:
            conn.execute(
                "UPDATE licenses SET account=? WHERE license_key=? AND account IS NULL",
                (account, license_key),
            )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM licenses WHERE license_key=?", (license_key,)
        ).fetchone()
        if row["account"] != account:
            return {"authorized": False, "reason": "授权码已绑定其他MT5账户"}
        return {"authorized": True, "message": "授权验证成功", "license": dict(row)}
    except sqlite3.Error as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail="授权验证时数据库操作失败") from exc
    finally:
        conn.close()

from auth.router import router as auth_router
app.include_router(auth_router)
