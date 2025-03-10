Feature:Shopping cart
  We want to test that shopping cart functionality works correctly

  Scenario: Successful add product to cart
    Given A product with name "Test1", price "100", and availability "10"
    And An empty shopping cart
    When I add product to the cart in amount "2"
    Then Product is added to the cart successfully

  Scenario: Failed add product to cart
    Given A product with name "Test1", price "100", and availability "1"
    And An empty shopping cart
    When I add product to the cart in amount "2"
    Then Product is not added to cart successfully

  Scenario: Successful removing product from cart
    Given A product with name "Test2", price "200", and availability "10"
    And An empty shopping cart
    When I add product to the cart in amount "1"
    And I remove the product from the cart
    Then The cart has to be empty

  Scenario: Calculating total price
    Given An empty shopping cart
    And A product with name "Test2", price "200", and availability "10"
    When I add product to the cart in amount "3"
    Then The total price has to be "600"

  Scenario: Submit an empty cart
    Given An empty shopping cart
    When I submit the order
    Then The order is not submitted successfully

  Scenario: Successful submit a cart
    Given An empty shopping cart
    And A product with name "Test2", price "200", and availability "10"
    When I add product to the cart in amount "3"
    And I submit the order
    Then The order is submitted successfully