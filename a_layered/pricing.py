class DiscountPolicy:
    def discount_for(self, subtotal: float) -> float:
        return round(subtotal * 0.10, 2) if subtotal >= 3000 else 0.0
