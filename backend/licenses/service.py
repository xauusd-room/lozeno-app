import sqlite3,uuid
from datetime import datetime

def generate_license_key(product_id):
    return f"LZ-{product_id}-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:8].upper()}"

def create_license_for_order(order,db_path):
    conn=sqlite3.connect(db_path)
    conn.row_factory=sqlite3.Row

    existing=conn.execute(
        "SELECT * FROM licenses WHERE order_no=?",
        (order["order_no"],)
    ).fetchone()

    if existing:
        conn.close()
        return dict(existing)

    license_key=generate_license_key(order["product_id"])
    created_at=datetime.now().isoformat(timespec="seconds")

    conn.execute(
        """
        INSERT INTO licenses(
            license_key,
            order_no,
            product_id,
            product_name,
            license_type,
            status,
            account,
            created_at,
            expires_at
        )
        VALUES(?,?,?,?,?,?,?,?,?)
        """,
        (
            license_key,
            order["order_no"],
            order["product_id"],
            order["product_name"],
            "single_account",
            "active",
            None,
            created_at,
            None
        )
    )

    conn.commit()

    row=conn.execute(
        "SELECT * FROM licenses WHERE order_no=?",
        (order["order_no"],)
    ).fetchone()

    conn.close()

    return dict(row)