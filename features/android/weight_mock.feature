Feature: Android weight mock
  The Android app should support flexible weight UI scenarios through a local mock API.

  @android @mock @smoke
  Scenario: Show empty weight history from mock data
    Given the weight mock API uses the empty history fixture
    When I open the Android weight screen
    And I open the Android weight history
    Then the Android weight history is empty

  @android @mock
  Scenario: Delete a mocked weight record from Android history
    Given the weight mock API uses the populated history fixture
    When I open the Android weight screen
    And I open the Android weight history
    Then the Android weight history shows mocked weight 70.2
    When I delete mocked weight id 401 from Android
    Then the Android weight history no longer shows mocked weight 70.2

  @android @mock
  Scenario: Show an API failure from the mock server
    Given the weight mock API returns an error
    When I open the Android weight screen
    Then Android shows the API failure message
