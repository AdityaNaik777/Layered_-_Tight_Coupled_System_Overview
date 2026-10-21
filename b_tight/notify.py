from . import app

def send_email(order_app, customer, order_id, total):
    # This module imports app and calls back to a helper in app.py.
    order_app.outbox.append(
        f"Email to {customer[2]}: order {order_id} total {app.money(total)}"
    )
