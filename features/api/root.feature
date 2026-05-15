Feature: Root API
  The Tink API should expose a health-style root endpoint.

  Scenario: Read the root endpoint
    When I request the root endpoint
    Then the root response says hello world
