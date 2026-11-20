Feature: Connect on Android

  Scenario: Confirm clearing the shared hub
    Given a mock Connect hub with a file and shared text
    When I open Connect in the Android drawer
    Then Connect shows the mocked file
    When I confirm Delete all content
    Then Connect shows an empty hub

  Scenario: Open Connect against the development API
    Given the Connect development API is available for Android
    When I open Connect in the Android drawer
    Then Connect shows the loaded file hub
