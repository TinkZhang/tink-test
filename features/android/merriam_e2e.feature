Feature: Android M-W Builder E2E
  The Android app should render M-W Builder statistics from the deployed dev API.

  @android @e2e @smoke
  Scenario: View M-W Builder progress from dev API
    Given the Tink dev API is reachable
    And the dev API has Merriam statistics
    When I open the Android M-W Builder screen
    Then the Android M-W Builder screen shows the dev API latest root
    And the Android M-W Builder content is visible
