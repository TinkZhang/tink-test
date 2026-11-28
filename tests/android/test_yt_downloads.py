from __future__ import annotations

import os

import pytest
from appium.webdriver.common.appiumby import AppiumBy
from pytest_bdd import given, when, then, scenario

from appium_client.yt_page import YtPage

pytestmark = pytest.mark.android
TEST_URL = "https://youtu.be/LbCHAQ7HKu4?si=k3IuU5o_SqidYee5"


@pytest.mark.mock
@pytest.mark.smoke
@scenario("android/yt_downloads.feature", "Reject a non-YouTube source")
def test_yt_rejects_other_sources():
    pass


@pytest.mark.mock
@pytest.mark.smoke
@scenario("android/yt_downloads.feature", "Choose audio or video without a backend")
def test_yt_audio_video_selection():
    pass


@pytest.mark.e2e
@pytest.mark.skipif(os.environ.get("TINK_YT_LIVE_DOWNLOAD") != "1", reason="Opt in to real YouTube downloads with TINK_YT_LIVE_DOWNLOAD=1")
@scenario("android/yt_downloads.feature", "Download the supplied YouTube video as audio and video")
def test_yt_real_audio_and_video_downloads():
    pass


@given("I open the Android YT screen", target_fixture="yt_page")
def open_yt(android_driver):
    page = YtPage(android_driver)
    page.open()
    return page


@when("I request an audio download from another website")
def invalid_source(yt_page):
    yt_page.submit("https://vimeo.com/123", "audio")


@then("YT asks for a valid YouTube video link")
def invalid_source_error(yt_page):
    assert yt_page.by_tag("yt_add_error").text == "Enter a YouTube video link."


@when("I select video mode in YT")
def select_video(yt_page):
    yt_page.open_add()
    yt_page.by_tag("yt_kind_video").click()


@when("I select audio mode in YT")
def select_audio(yt_page):
    yt_page.by_tag("yt_kind_audio").click()


@then("YT offers an MP4 video download")
def video_profile(yt_page):
    yt_page.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("MP4")')


@then("YT offers an M4A audio download")
def audio_profile(yt_page):
    yt_page.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("M4A")')


@when("I download the supplied YouTube link as audio")
def download_audio(yt_page):
    yt_page.submit(TEST_URL, "audio")
    yt_page.wait_for_download("LbCHAQ7HKu4", "audio")


@when("I download the supplied YouTube link as video")
def download_video(yt_page):
    yt_page.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiScrollable(new UiSelector().scrollable(true)).scrollToBeginning(5)')
    yt_page.submit(TEST_URL, "video")
    yt_page.wait_for_download("LbCHAQ7HKu4", "video")


@then("the YouTube audio file is stored on Android")
def audio_file(yt_page):
    yt_page.media_paths("audio")


@then("the YouTube video file is stored on Android")
def video_file(yt_page):
    yt_page.media_paths("video")


@then("I can play the downloaded audio inside YT and change speed")
def play_local_audio(yt_page):
    yt_page.by_tag("yt_tab_0").click()
    yt_page.wait.until(lambda driver: driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().resourceIdMatches("yt_play_[0-9]+")').is_enabled())
    yt_page.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().resourceIdMatches("yt_play_[0-9]+")').click()
    yt_page.by_tag("yt_player")
    yt_page.by_tag("yt_player_speed").click()
    yt_page.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("1.5×")').click()
    yt_page.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("1.5×")')
    yt_page.by_tag("yt_player_toggle").click()
    date = yt_page.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView('
        'new UiSelector().resourceIdMatches("yt_download_date_[0-9]+"))')
    assert date.text.startswith(("Downloaded ", "Added "))


@pytest.mark.mock
@scenario("android/yt_downloads.feature", "Reject an invalid playlist title filter")
def test_yt_invalid_playlist_filter():
    pass


@when("I enter a playlist with an invalid title regex")
def invalid_playlist_regex(yt_page):
    yt_page.open_add()
    yt_page.by_tag("yt_add_playlist").click()
    yt_page.by_tag("yt_add_url").send_keys("https://youtube.com/playlist?list=PL64Si-sSRnvZxhAwf2kxsqQXsg8Qd9FDG")
    yt_page.by_tag("yt_title_regex").send_keys("[")
    try:
        yt_page.driver.hide_keyboard()
    except Exception:
        pass
    yt_page.by_tag("yt_add_confirm").click()


@then("YT explains the title regex is invalid")
def invalid_regex_error(yt_page):
    assert "Invalid title regex" in yt_page.by_tag("yt_add_error").text


@then("I can label the individual audio and browse its group")
def label_individual_audio(yt_page):
    yt_page.by_tag("yt_tab_0").click()
    menu = yt_page.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView('
        'new UiSelector().resourceIdMatches("yt_episode_menu_[0-9]+"))')
    menu.click()
    yt_page.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Edit labels")').click()
    field = yt_page.by_tag("yt_labels_input")
    field.clear()
    field.send_keys("History, Interviews")
    try:
        yt_page.driver.hide_keyboard()
    except Exception:
        pass
    yt_page.by_tag("yt_labels_save").click()
    yt_page.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView('
        'new UiSelector().resourceId("yt_label_history"))').click()
    yt_page.by_tag("yt_play_label")


@then("I can play the downloaded video inside Tink")
def play_local_video(yt_page):
    card = yt_page.by_tag("yt_download_LbCHAQ7HKu4_video")
    card.find_element(AppiumBy.ACCESSIBILITY_ID, "Play video").click()
    yt_page.by_tag("yt_video_player")
    yt_page.wait.until(lambda _: yt_page.by_tag("yt_video_toggle").is_enabled())
    yt_page.by_tag("yt_video_speed").click()
    yt_page.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("1.5×")').click()
    yt_page.by_tag("yt_video_toggle").click()
    yt_page.by_tag("yt_video_fullscreen").click()
    yt_page.by_tag("yt_video_fullscreen").click()
    yt_page.by_tag("yt_video_back").click()
    yt_page.by_tag("yt_library")


@pytest.mark.mock
@scenario("android/yt_downloads.feature", "Choose audio or video for a subscription")
def test_yt_subscription_formats():
    pass


@when("I choose video download format for a playlist")
def choose_subscription_formats(yt_page):
    yt_page.open_add()
    yt_page.by_tag("yt_add_playlist").click()
    yt_page.by_tag("yt_subscription_format_video").click()


@then("the playlist form keeps Video selected")
def subscription_both_selected(yt_page):
    assert yt_page.by_tag("yt_subscription_format_video").get_attribute("selected") == "true"


@pytest.mark.mock
@scenario("android/yt_downloads.feature", "Choose a one-time full playlist import")
def test_yt_one_time_import():
    pass


@when("I choose to download the whole playlist once")
def one_time_playlist(yt_page):
    yt_page.open_add()
    yt_page.by_tag("yt_add_playlist").click()
    yt_page.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView('
        'new UiSelector().resourceId("yt_download_all_once"))').click()


@then("the playlist form hides recurring schedule settings")
def no_recurring_fields(yt_page):
    assert yt_page.by_tag("yt_download_all_once").get_attribute("checked") == "true"
    assert not yt_page.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().resourceId("yt_cron")')
    assert not yt_page.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().resourceId("yt_latest_count")')


@pytest.mark.mock
@scenario("android/yt_downloads.feature", "Share a YouTube video into Tink")
def test_yt_shared_link():
    pass


@when("I share a YouTube video link with Tink")
def share_youtube_link(yt_page):
    import subprocess
    subprocess.run(["adb", "shell", "am", "start", "-n", "app.tinks.tink/.MainActivity",
        "-a", "android.intent.action.SEND", "-t", "text/plain", "--es", "android.intent.extra.TEXT",
        "https://youtu.be/LbCHAQ7HKu4"], check=True, capture_output=True, text=True)


@then("Tink opens the add dialog with the shared link")
def shared_link_dialog(yt_page):
    assert "LbCHAQ7HKu4" in yt_page.by_tag("yt_add_url").text
    yt_page.by_tag("yt_add_confirm")
