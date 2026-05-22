Feature: Android haircut E2E
  The Android app should show haircut records through the deployed dev API.

  @android @e2e @smoke
  Scenario: Add a haircut record through Android
    Given the Tink dev API is reachable
    When I open the Android haircut screen
    And I add a unique Android haircut record
    Then the haircut API contains the Android-created haircut record
    And the Android haircut screen shows the Android-created haircut record
