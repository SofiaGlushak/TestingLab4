"""E-shop module for managing orders and shipping."""

import uuid
from typing import Dict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from services import ShippingService


class Product:
    """Represents a product in the shop with name, price, and availability."""
    available_amount: int
    name: str
    price: float

    def __init__(self, name, price, available_amount):
        if not isinstance(name, str) or not isinstance(price, (int, float)) or not isinstance(available_amount, int):
            raise TypeError("Invalid data types for product attributes")
        if price <= 0:
            raise ValueError("Price must be more than zero")
        if available_amount < 0:
            raise ValueError("Availability must be non-negative")
        if len(name) < 3:
            raise ValueError("The name length must be greater than 0")
        self.name = name
        self.price = price
        self.available_amount = available_amount

    def is_available(self, requested_amount):
        """Checks if the requested amount of the product is available."""
        return self.available_amount >= requested_amount

    def buy(self, requested_amount):
        """Reduces the available stock when a purchase is made."""
        if not isinstance(requested_amount, int) or requested_amount <= 0:
            raise ValueError("Invalid amount to buy")
        if not self.is_available(requested_amount):
            raise ValueError("Not enough stock available")
        self.available_amount -= requested_amount

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class ShoppingCart:
    """Represents a shopping cart that holds selected products."""
    products: Dict[Product, int]

    def __init__(self):
        self.products = {}

    def contains_product(self, product):
        """Checks if a product is in the cart."""
        return product in self.products

    def calculate_total(self):
        """Calculates the total cost of all products in the cart."""
        return sum([p.price * count for p, count in self.products.items()])

    def add_product(self, product: Product, amount: int):
        """Adds a product to the shopping cart."""
        if not product.is_available(amount):
            raise ValueError(f"Product {product} has only {product.available_amount} items")
        self.products[product] = amount

    def remove_product(self, product):
        """Removes a product from the shopping cart."""
        if product in self.products:
            del self.products[product]

    def submit_cart_order(self):
        """Finalizes the shopping cart and prepares the order."""
        product_ids = []
        for product, count in self.products.items():
            product.buy(count)
            product_ids.append(str(product))
        self.products.clear()

        return product_ids


@dataclass
class Order:
    """Represents a customer order."""
    cart: ShoppingCart
    shipping_service: ShippingService
    order_id: str = str(uuid.uuid4())

    def place_order(self, shipping_type, due_date: datetime = None):
        """Places an order and schedules shipping."""
        if not due_date:
            due_date = datetime.now(timezone.utc) + timedelta(seconds=3)
        product_ids = self.cart.submit_cart_order()
        print(due_date)
        return self.shipping_service.create_shipping(shipping_type,
                                                     product_ids,
                                                     self.order_id,
                                                     due_date)


@dataclass()
class Shipment:
    """Represents a shipment that tracks the shipping status of an order."""
    shipping_id: str
    shipping_service: ShippingService

    def check_shipping_status(self):
        """Checks the status of the shipment."""
        return self.shipping_service.check_status(self.shipping_id)
