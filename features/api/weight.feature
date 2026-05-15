Feature: Weight API
  The Tink API should support recording and removing weight entries in the dev environment.

  Scenario: Create, list, and delete a weight record
    Given the Tink dev API is reachable
    When I create a weight record
    Then the weight create response contains the created weight
    And the weight list includes the created weight
    When I delete the created weight record
    Then the weight list does not include the created weight
