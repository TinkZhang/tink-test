Feature: Story API
  The Tink API should support creating, listing, reading, and deleting stories in the dev environment.

  Scenario: Create, list, read, and delete a story
    Given the Tink dev API is reachable
    When I create a story
    Then the story create response contains the created story
    And the story list includes the created story
    And I can read the created story
    When I delete the created story
    Then reading the deleted story returns not found
