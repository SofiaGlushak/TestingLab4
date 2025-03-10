import unittest
from app.eshop import Product, ShoppingCart, Order
from unittest.mock import MagicMock


class TestCalculator(unittest.TestCase):

    def setUp(self):
        self.product = Product(name='Test', price=100, available_amount=21)
        self.cart = ShoppingCart()

    def tearDown(self):
        self.cart.remove_product(self.product)

    def test_mock_add_product(self):
        self.product.is_available = MagicMock()
        self.cart.add_product(self.product, 12345)
        self.product.is_available.assert_called_with(12345)
        self.product.is_available.reset_mock()

    def test_add_available_amount(self):
        self.cart.add_product(self.product, 11)
        self.assertEqual(self.cart.contains_product(self.product), True, 'Продукт успішно доданий до корзини')

    def test_add_non_available_amount(self):
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 22)
        self.assertEqual(self.cart.contains_product(self.product), False, 'Продукт не доданий до корзини')

    def test_create_product_negative_price(self):
        with self.assertRaises(ValueError):
            Product(name="Test", price=-10, available_amount=10)

    def test_create_product_zero_price(self):
        with self.assertRaises(ValueError):
            Product(name="Test", price=0, available_amount=10)

    def test_create_product_non_numeric_price(self):
        with self.assertRaises(TypeError):
            Product(name="Test", price="One hundred", available_amount=10)

    def test_create_product_short_name(self):
        with self.assertRaises(ValueError):
            Product(name="T", price=50, available_amount=10)

    def test_product_buy(self):
        self.product.buy(10)
        self.assertEqual(self.product.available_amount, 11, "Кількість товару має зменшитися на 5")

    def test_product_buy_insufficient_stock(self):
        with self.assertRaises(ValueError):
            self.product.buy(22)

    def test_cart_total_calculation(self):
        self.cart.add_product(self.product, 5)
        total = self.cart.calculate_total()
        self.assertEqual(total, 500, "Загальна вартість кошика має бути правильно підрахована")

    def test_remove_product_from_cart(self):
        self.cart.add_product(self.product, 3)
        self.cart.remove_product(self.product)
        self.assertFalse(self.cart.contains_product(self.product), "Продукт повинен бути видалений з кошика")


if __name__ == '__main__':
    unittest.main()
