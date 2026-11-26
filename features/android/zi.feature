Feature: Android Chinese character records

  Scenario: Reading and writing cards open separate flows
    Given the Android Zi app is using the local mock API
    When I open the Zi dashboard
    Then the Zi reading and writing cards open their own lists
    And the Zi plus icons open the reading dialog and handwriting board

  Scenario: The written character list loads from the development API
    Given the Android Zi app is using the deployed development API
    When I open the Zi dashboard
    Then the written character list matches the development API
