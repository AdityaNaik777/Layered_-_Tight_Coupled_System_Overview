import sqlite3
from . import notify, reports

SCHEMA = """
CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT);
CREATE TABLE products(id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER);
CREATE TABLE orders(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER REFERENCES customers(id),
  subtotal REAL, discount REAL, total REAL
);
CREATE TABLE order_lines(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER REFERENCES orders(id),
  product_id INTEGER REFERENCES products(id),
  quantity INTEGER, line_total REAL
);
"""

def money(value):
    return f"{value:.2f}"

class OrderApp:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(SCHEMA)
        self.conn.executemany(
            "INSERT INTO customers VALUES (?, ?, ?, ?)",
            [(i, f"Customer {i}", f"customer{i}@example.com", f"900000{i:04d}") for i in range(1, 201)]
        )
        self.conn.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?)",
            [(i, f"Product {i}", float(50 + (i * 37) % 450), 10**9) for i in range(1, 51)]
        )
        self.conn.commit()
        self.outbox = []

    def place_order(self, customer_id, items):
        if not items:
            raise ValueError("An order must contain at least one item")
        customer = self.conn.execute(
            "SELECT id, name, email, phone FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
        if customer is None:
            raise ValueError(f"Customer {customer_id} does not exist")

        subtotal = 0.0
        checked = []
        for product_id, quantity in items:
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            product = self.conn.execute(
                "SELECT id, name, price, stock FROM products WHERE id = ?", (product_id,)
            ).fetchone()
            if product is None:
                raise ValueError(f"Product {product_id} does not exist")
            if product[3] < quantity:
                raise ValueError(f"Insufficient stock for product {product_id}")
            line_total = round(float(product[2]) * quantity, 2)
            subtotal += line_total
            checked.append((product_id, quantity, line_total))

        subtotal = round(subtotal, 2)
        discount = round(subtotal * 0.10, 2) if subtotal >= 3000 else 0.0
        total = round(subtotal - discount, 2)

        self.conn.execute("BEGIN")
        try:
            for product_id, quantity, line_total in checked:
                self.conn.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id)
                )
            cur = self.conn.execute(
                "INSERT INTO orders(customer_id, subtotal, discount, total) VALUES (?, ?, ?, ?)",
                (customer_id, subtotal, discount, total)
            )
            order_id = int(cur.lastrowid)
            for product_id, quantity, line_total in checked:
                self.conn.execute(
                    "INSERT INTO order_lines(order_id, product_id, quantity, line_total) VALUES (?, ?, ?, ?)",
                    (order_id, product_id, quantity, line_total)
                )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

        notify.send_email(self, customer, order_id, total)
        return f"Order {order_id} confirmed. Total: {money(total)}"

    def customer_report(self, customer_id):
        return reports.customer_report(self, customer_id)
