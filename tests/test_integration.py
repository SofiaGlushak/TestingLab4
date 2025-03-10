import uuid
import pytest
import random
import boto3
from datetime import datetime, timedelta, timezone
from app.eshop import Product, ShoppingCart, Order
from services import ShippingService
from services.repository import ShippingRepository
from services.publisher import ShippingPublisher
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_QUEUE


@pytest.mark.parametrize("order_id, shipping_id", [
    ("order_1", "shipping_1"),
    ("order_i2hur2937r9", "shipping_1!!!!"),
    (8662354, 123456),
    (str(uuid.uuid4()), str(uuid.uuid4()))
])
def test_place_order_with_mocked_repo(mocker, order_id, shipping_id):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    mock_repo.create_shipping.return_value = shipping_id

    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )

    order = Order(cart, shipping_service, order_id)
    due_date = datetime.now(timezone.utc) + timedelta(seconds=3)
    actual_shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=due_date
    )

    assert actual_shipping_id == shipping_id, "Actual shipping id must be equal to mock return value"

    mock_repo.create_shipping.assert_called_with
    (ShippingService.list_available_shipping_type()[0],
     ["Product"], order_id, shipping_service.SHIPPING_CREATED, due_date)
    mock_publisher.send_new_shipping.assert_called_with(shipping_id)


def test_place_order_with_unavailable_shipping_type_fails(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(),
                                       ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )
    order = Order(cart, shipping_service)
    shipping_id = None

    with pytest.raises(ValueError) as excinfo:
        shipping_id = order.place_order(
            "Новий тип доставки",
            due_date=datetime.now(timezone.utc) + timedelta(seconds=3)
        )
    assert shipping_id is None, "Shipping id must not be assigned"
    assert "Shipping type is not available" in str(excinfo.value)


def test_when_place_order_then_shipping_in_queue(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(),
                                       ShippingPublisher())
    cart = ShoppingCart()

    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )

    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION
    )
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )

    messages = response.get("Messages", [])
    assert len(messages) == 1, "Expected 1 SQS message"

    body = messages[0]["Body"]
    assert shipping_id == body


@pytest.fixture
def shipping_service():
    return ShippingService(ShippingRepository(), ShippingPublisher())


@pytest.fixture
def cart():
    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )
    return cart


# 1. Тест створення замовлення з коректними даними
def test_place_order_valid(cart, shipping_service):
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )
    assert shipping_id is not None


# 2. Тест створення замовлення з недоступним типом доставки
def test_place_order_invalid_shipping_type(cart, shipping_service):
    order = Order(cart, shipping_service)
    with pytest.raises(ValueError):
        order.place_order("Неіснуючий тип")


# 3. Тест створення замовлення із застарілим due_date
def test_place_order_past_due_date(cart, shipping_service):
    order = Order(cart, shipping_service)
    with pytest.raises(ValueError):
        order.place_order(
            ShippingService.list_available_shipping_type()[0],
            due_date=datetime.now(timezone.utc) - timedelta(minutes=1)
        )


# 4. Тест перевірки статусу доставки
def test_check_shipping_status(cart, shipping_service):
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )
    assert shipping_service.check_status(shipping_id) == ShippingService.SHIPPING_IN_PROGRESS


# 5. Тест додавання нового замовлення в чергу
def test_shipping_added_to_queue(cart, shipping_service):
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )
    sqs_client = boto3.client("sqs", endpoint_url=AWS_ENDPOINT_URL,
                              region_name=AWS_REGION)
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    response = sqs_client.receive_message(QueueUrl=queue_url,
                                          MaxNumberOfMessages=1,
                                          WaitTimeSeconds=10)
    assert response.get("Messages") is not None


# 6. Тест процесу доставки
def test_process_shipping(cart, shipping_service):
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )
    shipping_service.process_shipping(shipping_id)
    assert shipping_service.check_status(shipping_id) == ShippingService.SHIPPING_COMPLETED


# 7. Тест отримання замовлення по ID
def test_get_shipping(cart, shipping_service):
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )
    shipping = shipping_service.repository.get_shipping(shipping_id)
    assert shipping is not None


# 8. Тест оновлення статусу доставки
def test_update_shipping_status(cart, shipping_service):
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )
    shipping_service.repository.update_shipping_status(shipping_id,ShippingService.SHIPPING_COMPLETED)
    assert shipping_service.check_status(shipping_id) == ShippingService.SHIPPING_COMPLETED


# 9. Тест створення таблиці у DynamoDB
def test_dynamodb_table_exists(dynamo_resource):
    client = boto3.client("dynamodb", endpoint_url=AWS_ENDPOINT_URL,
                          region_name=AWS_REGION)
    response = client.list_tables()
    assert "ShippingTable" in response["TableNames"]


# 10. Тест створення черги у SQS
def test_sqs_queue_exists():
    client = boto3.client("sqs", endpoint_url=AWS_ENDPOINT_URL,
                          region_name=AWS_REGION)
    response = client.list_queues()
    assert any("ShippingQueue" in url for url in response.get("QueueUrls", []))


# 11. Тест спроби отримати неіснуюче замовлення
def test_get_nonexistent_shipping(shipping_service):
    shipping = shipping_service.repository.get_shipping("nonexistent_id")
    assert shipping is None


# 12. Тест відправки повідомлення в чергу
def test_send_message_to_queue():
    publisher = ShippingPublisher()
    message_id = publisher.send_new_shipping("test_shipping_id")
    assert message_id is not None


# 13. Тест отримання повідомлення з черги
def test_receive_message_from_queue():
    publisher = ShippingPublisher()
    publisher.send_new_shipping("test_shipping_id")
    messages = publisher.poll_shipping()
    assert "test_shipping_id" in messages
