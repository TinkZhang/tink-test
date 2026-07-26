Feature: Time API
  The Tink API should support creating, updating, listing, summarizing, and deleting time entries in the dev environment.

  Scenario: Create, update, list, summarize, and delete a time entry
    Given the Tink dev API is reachable
    When I create a time entry
    Then the time create response contains the created time entry
    And the time list includes the created time entry
    When I update the created time entry
    Then the time list shows the updated time entry
    And the time statistics endpoint returns type durations
    When I delete the created time entry
    Then the time list does not include the created time entry

  Scenario: Create a DiaryLoom all-day time event excluded from statistics
    Given the Tink dev API is reachable
    When I create a DiaryLoom all-day time entry
    Then the DiaryLoom time create response is all-day and excluded from statistics
    And the time list includes the created time entry
    And the time statistics endpoint excludes the DiaryLoom entry
    When I delete the created time entry
    Then the time list does not include the created time entry
