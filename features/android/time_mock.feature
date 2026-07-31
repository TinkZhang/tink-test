Feature: Android time mock
  The Android app should support flexible time UI scenarios through a local mock API.

  @android @mock @smoke
  Scenario: Capture empty time dashboard visual baseline
    Given the time mock API uses the empty time fixture
    When I open the Android time screen
    Then the Android time dashboard is empty

  @android @mock
  Scenario: Capture mixed time dashboard visual baseline
    Given the time mock API uses the mixed time fixture
    When I open the Android time screen
    Then the Android time dashboard shows multiple mocked time entries
    And the Android time statistics show multiple mocked types
