Feature: Zi API
  The Tink API should support upserting and reading character proficiency records in the dev environment.

  Scenario: Upsert and read zi records
    Given the Tink dev API is reachable
    When I upsert zi records
    Then the zi response contains the upserted characters
    And the zi list includes the upserted characters

  Scenario: Written characters can be listed and invalid input is rejected
    Given the Tink dev API is reachable
    When I list the written zi records
    Then the written zi list contains distinct single characters
    And an invalid written zi record is rejected
