Feature: Android haircut mock
  The Android app should support flexible haircut UI scenarios through a local mock API.

  @android @mock @smoke
  Scenario: Capture empty haircut history visual baseline
    Given the haircut mock API uses the empty haircut fixture
    When I open the Android haircut screen
    Then the Android haircut history is empty

  @android @mock
  Scenario: Capture haircut history visual baseline
    Given the haircut mock API uses the haircut history fixture
    When I open the Android haircut screen
    Then the Android haircut screen shows multiple mocked haircut records
