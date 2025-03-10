Feature: Product
  We want to test that product functionality works correctly

  Scenario: Successful product availability check
    Given A product with name "Test1", price "100", and availability "10"
    When I check availability for "5" items
    Then The product is available

  Scenario: Failed product availability check
    Given A product with name "Test1", price "100", and availability "10"
    When I check availability for "15" items
    Then The product is unavailable

  Scenario: Create a product with negative price
    When I create a product with name "Test1", price "-100", and availability "10"
    Then The product creation has to fail

  Scenario: Create a product with price equals 0
    When I create a product with name "Test1", price "0", and availability "10"
    Then The product creation has to fail

  Scenario: Create a product with a name length of less than 3 characters
    When I create a product with name "T", price "100", and availability "10"
    Then The product creation has to fail

  Scenario: Create a product with a non-numeric price
    When I create a product with name "T", price "one hundred", and availability "10"
    Then The product creation has to fail

  Scenario: Creating a product with None values
    When I create a product with None values
    Then The product creation has to fail

  Scenario: Successful buy a product
    Given A product with name "Test3", price "500", and availability "20"
    When I buy "10" items
    Then The product availability has to be "10"

  Scenario: Failed buy a product
    Given A product with name "Test3", price "500", and availability "5"
    When I buy "10" items
    Then The product purchase has to fail