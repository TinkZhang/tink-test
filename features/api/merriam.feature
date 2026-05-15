Feature: Merriam API
  The Tink API should expose Merriam study statistics in the dev environment.

  Scenario: Read Merriam statistics
    Given the Tink dev API is reachable
    When I request Merriam statistics
    Then the Merriam statistics response has week stats
