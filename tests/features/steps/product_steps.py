from behave import given, when, then
from app.eshop import Product, ShoppingCart, Order

@given('A product with name {name}, price "{price}", and availability "{availability}"')
def create_product_for_cart(context, name, price, availability):
    context.product = Product(name=name, price=float(price), available_amount=int(availability))

@when('I check availability for "{amount}" items')
def check_availability(context, amount):
    context.availability_check = context.product.is_available(int(amount))

@when('I create a product with name "{name}", price "{price}", and availability "{availability}"')
def create_product_with_invalid_price(context, name, price, availability):
    try:
        context.product = Product(name=name, price=float(price), available_amount=int(availability))
        context.product_created = True
    except ValueError:
        context.product_created = False

@when('I create a product with None values')
def create_invalid_product(context):
    try:
        context.product = Product(None, None, None)
        context.product_created = True
    except TypeError:
        context.product_created = False

@when('I buy "{amount}" items')
def buy_product(context, amount):
    try:
        context.product.buy(int(amount))
        context.buy_success = True
    except ValueError:
        context.buy_success = False

@then('The product is available')
def product_available(context):
    assert context.availability_check == True

@then('The product is unavailable')
def product_unavailable(context):
    assert context.availability_check == False

@then('The product creation has to fail')
def product_creation_fail(context):
    assert context.product_created == False

@then('The product availability has to be "{new_amount}"')
def check_new_availability(context, new_amount):
    assert context.product.available_amount == int(new_amount)

@then('The product purchase has to fail')
def purchase_failed(context):
    assert context.buy_success is False