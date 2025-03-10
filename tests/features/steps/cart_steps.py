from behave import given, when, then
from app.eshop import Product, ShoppingCart, Order

@given('An empty shopping cart')
def empty_cart(context):
    context.cart = ShoppingCart()

@when('I add product to the cart in amount "{product_amount}"')
def add_product(context, product_amount):
    try:
        context.cart.add_product(context.product, int(product_amount))
        context.add_successfully = True
    except ValueError:
        context.add_successfully = False

@when("I remove the product from the cart")
def remove_product(context):
    context.cart.remove_product(context.product)

@when('I submit the order')
def submit_order(context):
    try:
        context.cart.submit_cart_order()
        context.order_success = True
    except ValueError:
        context.order_success = False

@then("Product is added to the cart successfully")
def add_successful(context):
    assert context.add_successfully == True

@then("Product is not added to cart successfully")
def add_failed(context):
    assert context.add_successfully == False

@then('The total price has to be "{total_price}"')
def check_cart_total(context, total_price):
    assert context.cart.calculate_total() == float(total_price)

@then('The order is not submitted successfully')
def submit_failed(context):
    assert context.order_success == False

@then('The order is submitted successfully')
def submit_successful(context):
    assert context.order_success == True
