class OrderController:
    def __init__(self, service):
        self.service = service

    def place_order(self, customer_id, items):
        return self.service.place_order(customer_id, items)

    def customer_report(self, customer_id):
        return self.service.customer_report(customer_id)
