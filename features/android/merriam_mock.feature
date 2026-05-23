Feature: Android M-W Builder mock
  The Android app should support M-W Builder UI scenarios through a local mock API.

  @android @mock @smoke
  Scenario: Capture M-W Builder progress visual baseline
    Given the Merriam mock API uses the progress fixture
    When I open the Android M-W Builder screen
    Then the Android M-W Builder screen shows the mocked latest root
    And the Android M-W Builder content is visible

  @android @mock
  Scenario: Complete the next M-W root through Android
    Given the Merriam mock API uses the progress fixture
    When I open the Android M-W Builder screen
    And I complete Merriam root 11 from Android
    Then the Merriam mock API receives root 11
