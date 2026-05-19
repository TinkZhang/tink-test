Feature: Android weight E2E
  The Android app should show and update weight records through the deployed dev API.

  @android @e2e @smoke
  Scenario: View an API-created weight in Android history
    Given the Tink dev API is reachable
    And the API has a unique weight record for Android
    When I open the Android weight screen
    And I open the Android weight history
    Then the Android weight history shows the API-created weight

  @android @e2e
  Scenario: Add a weight through Android and verify it through the API
    Given the Tink dev API is reachable
    And the API has a seed weight record for Android
    When I open the Android weight screen
    And I add a weight record through Android
    Then the API includes the Android-created weight
    When I open the Android weight history
    Then the Android weight history shows the Android-created weight
