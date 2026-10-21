from . import app

def customer_report(order_app, customer_id):
    rows = order_app.conn.execute(
        "SELECT id, subtotal, discount, total FROM orders WHERE customer_id = ? ORDER BY id",
        (customer_id,)
    ).fetchall()
    return "\n".join(
        f"Order {row[0]}: subtotal={app.money(row[1])}, discount={app.money(row[2])}, total={app.money(row[3])}"
        for row in rows
    )
