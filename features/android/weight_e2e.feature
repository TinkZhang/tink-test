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
  Scenario: Add and delete a weight through Android without changing dev state
    Given the Tink dev API is reachable
    And the API has a temporary baseline weight 139.8 for Android
    When I open the Android weight screen
    Then the Android current weight is 139.8
    And Android shows the weight as recorded today
    When I adjust Android weight to 140.0 and add it
    Then the Android current weight is 140.0
    And Android shows the weight as recorded today
    Then the API includes the Android-created weight
    When I open the Android weight history
    And I delete the Android-created weight from history
    And I return to the Android weight screen
    Then the Android current weight returns to 139.8
