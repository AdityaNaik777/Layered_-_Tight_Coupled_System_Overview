class EmailNotifier:
    def __init__(self):
        self.outbox = []

    def notify(self, customer, order):
        self.outbox.append(
            f"Email to {customer.email}: order {order.id} total {order.total:.2f}"
        )
