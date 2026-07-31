Feature: Android time E2E
  The Android app should show time entries and labels through the deployed dev API.

  @android @e2e @smoke
  Scenario: View an API-created time entry on Android
    Given the Tink dev API is reachable
    And the API has a unique time entry for Android
    When I open the Android time screen
    Then the Android time screen shows the API-created time entry

  @android @e2e
  Scenario: Add and delete a time label through Android
    Given the Tink dev API is reachable
    When I open the Android time screen
    And I add a unique Android time label
    Then the Android time label manager shows the created label
    When I delete the Android-created time label
    Then the Android time label manager no longer shows the created label
