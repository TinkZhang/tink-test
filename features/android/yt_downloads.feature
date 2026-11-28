Feature: YouTube downloads stored on Android
  Scenario: Reject a non-YouTube source
    Given I open the Android YT screen
    When I request an audio download from another website
    Then YT asks for a valid YouTube video link

  Scenario: Choose audio or video without a backend
    Given I open the Android YT screen
    When I select video mode in YT
    Then YT offers an MP4 video download
    When I select audio mode in YT
    Then YT offers an M4A audio download

  Scenario: Download the supplied YouTube video as audio and video
    Given I open the Android YT screen
    When I download the supplied YouTube link as audio
    Then the YouTube audio file is stored on Android
    And I can play the downloaded audio inside YT and change speed
    And I can label the individual audio and browse its group
    When I download the supplied YouTube link as video
    Then the YouTube video file is stored on Android
    And I can play the downloaded video inside Tink

  Scenario: Reject an invalid playlist title filter
    Given I open the Android YT screen
    When I enter a playlist with an invalid title regex
    Then YT explains the title regex is invalid

  Scenario: Choose audio or video for a subscription
    Given I open the Android YT screen
    When I choose video download format for a playlist
    Then the playlist form keeps Video selected

  Scenario: Choose a one-time full playlist import
    Given I open the Android YT screen
    When I choose to download the whole playlist once
    Then the playlist form hides recurring schedule settings

  Scenario: Share a YouTube video into Tink
    Given I open the Android YT screen
    When I share a YouTube video link with Tink
    Then Tink opens the add dialog with the shared link
