Feature: Connect file hub
  The Android and Mac apps use the same files and shared text endpoints.

  Scenario: Resume an upload and exchange text between two clients
    Given the Connect development hub is available
    When the first client completes a multi-chunk file upload and shares text
    Then the second client can download the same bytes and read the text
    And deleting the file removes it from the shared list
