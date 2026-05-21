Feature: Android weight mock
  The Android app should support flexible weight UI scenarios through a local mock API.

  @android @mock @smoke
  Scenario: Capture empty weight control visual baseline
    Given the weight mock API uses the empty history fixture
    When I open the Android weight screen
    Then the Android weight control shows no current weight visual baseline

  @android @mock
  Scenario: Capture latest weight control visual baseline
    Given the weight mock API uses the latest weight fixture
    When I open the Android weight screen
    Then the Android weight control shows latest weight 140.8 on 2026-05-20 visual baseline

  @android @mock
  Scenario: Capture empty weight trend visual baseline
    Given the weight mock API uses the empty history fixture
    When I open the Android weight screen
    Then the Android month trend is empty visual baseline
    When I select the Android all-time weight trend
    Then the Android all-time trend is empty visual baseline

  @android @mock
  Scenario: Capture populated weight trend visual baseline
    Given the weight mock API uses the fixed trend fixture
    When I open the Android weight screen
    Then the Android month trend has data visual baseline
    When I select the Android all-time weight trend
    Then the Android all-time trend has data visual baseline

  @android @mock
  Scenario: Capture empty weight history visual baseline
    Given the weight mock API uses the empty history fixture
    When I open the Android weight screen
    And I open the Android weight history
    Then the Android weight history is empty

  @android @mock
  Scenario: Capture populated weight history visual baseline
    Given the weight mock API uses the populated history fixture
    When I open the Android weight screen
    And I open the Android weight history
    Then the Android weight history shows mocked weight 70.2
    And the Android weight history shows mocked weight 70.8

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
