from .domain import Order, OrderLine
from .pricing import DiscountPolicy

class OrderService:
    def __init__(self, repository, notifier, policy=None):
        self.repo = repository
        self.notifier = notifier
        self.policy = policy or DiscountPolicy()

    def place_order(self, customer_id: int, items: list[tuple[int, int]]):
        if not items:
            raise ValueError("An order must contain at least one item")

        customer = self.repo.get_customer(customer_id)
        lines = []
        subtotal = 0.0

        for product_id, quantity in items:
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            product = self.repo.get_product(product_id)
            if product.stock < quantity:
                raise ValueError(f"Insufficient stock for product {product_id}")
            line_total = round(float(product.price) * quantity, 2)
            subtotal += line_total
            lines.append(OrderLine(product_id, quantity, line_total))

        subtotal = round(subtotal, 2)
        discount = self.policy.discount_for(subtotal)
        total = round(subtotal - discount, 2)
        order = Order(customer_id, lines, subtotal, discount, total)

        self.repo.conn.execute("BEGIN")
        try:
            for line in lines:
                self.repo.reduce_stock(line.product_id, line.quantity)
            order.id = self.repo.save_order(order)
            self.repo.conn.commit()
        except Exception:
            self.repo.conn.rollback()
            raise

        self.notifier.notify(customer, order)
        return f"Order {order.id} confirmed. Total: {order.total:.2f}"

    def customer_report(self, customer_id: int):
        rows = self.repo.orders_for_customer(customer_id)
        return "\n".join(
            f"Order {row[0]}: subtotal={row[1]:.2f}, discount={row[2]:.2f}, total={row[3]:.2f}"
            for row in rows
        )
