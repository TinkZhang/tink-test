Feature: Haircut API
  The Tink API should support recording and removing haircut entries in the dev environment.

  Scenario: Create, list, and delete a haircut record
    Given the Tink dev API is reachable
    When I create a haircut record
    Then the haircut create response contains the created haircut
    And the haircut list includes the created haircut
    When I delete the created haircut record
    Then the haircut list does not include the created haircut
