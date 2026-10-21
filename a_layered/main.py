import sqlite3
from .repository_sqlite import SqliteRepository
from .notifier_email import EmailNotifier
from .service import OrderService
from .presentation import OrderController

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

def create_app():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?)",
        [(i, f"Customer {i}", f"customer{i}@example.com", f"900000{i:04d}") for i in range(1, 201)]
    )
    conn.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?)",
        [(i, f"Product {i}", float(50 + (i * 37) % 450), 10**9) for i in range(1, 51)]
    )
    conn.commit()
    repo = SqliteRepository(conn)
    notifier = EmailNotifier()
    return OrderController(OrderService(repo, notifier)), conn, notifier
