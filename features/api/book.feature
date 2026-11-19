Feature: Book API
  The Tink API should support the book lifecycle and book notes in the dev environment.

  Scenario: Create, update, read, finish, annotate, and delete a book
    Given the Tink dev API is reachable
    When I create a wishlist book
    Then the wishlist contains the created book
    When I update the created book
    Then reading the book shows the update
    When I start reading the created book
    Then the reading list contains the created book
    When I add a note to the created book
    Then I can read and update the created note
    When I mark the created book as done
    Then the done list contains the created book
    When I delete the created book
    Then reading the deleted book returns not found
