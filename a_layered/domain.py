from dataclasses import dataclass

@dataclass
class Customer:
    id: int
    name: str
    email: str
    phone: str

@dataclass
class Product:
    id: int
    name: str
    price: float
    stock: int

@dataclass
class OrderLine:
    product_id: int
    quantity: int
    line_total: float

@dataclass
class Order:
    customer_id: int
    lines: list[OrderLine]
    subtotal: float
    discount: float
    total: float
    id: int | None = None
