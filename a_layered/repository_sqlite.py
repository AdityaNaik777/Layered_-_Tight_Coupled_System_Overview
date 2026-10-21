import sqlite3
from .domain import Order, Customer, Product

class SqliteRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def get_customer(self, customer_id: int):
        row = self.conn.execute(
            "SELECT id, name, email, phone FROM customers WHERE id = ?",
            (customer_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"Customer {customer_id} does not exist")
        return Customer(*row)

    def get_product(self, product_id: int):
        row = self.conn.execute(
            "SELECT id, name, price, stock FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"Product {product_id} does not exist")
        return Product(*row)

    def reduce_stock(self, product_id: int, quantity: int):
        self.conn.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity, product_id)
        )

    def save_order(self, order: Order) -> int:
        cur = self.conn.execute(
            "INSERT INTO orders(customer_id, subtotal, discount, total) VALUES (?, ?, ?, ?)",
            (order.customer_id, order.subtotal, order.discount, order.total)
        )
        order_id = int(cur.lastrowid)
        for line in order.lines:
            self.conn.execute(
                "INSERT INTO order_lines(order_id, product_id, quantity, line_total) VALUES (?, ?, ?, ?)",
                (order_id, line.product_id, line.quantity, line.line_total)
            )
        return order_id

    def orders_for_customer(self, customer_id: int):
        return self.conn.execute(
            "SELECT id, subtotal, discount, total FROM orders WHERE customer_id = ? ORDER BY id",
            (customer_id,)
        ).fetchall()
