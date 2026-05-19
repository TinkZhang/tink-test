from __future__ import annotations

import os
from pathlib import Path

from appium import webdriver
from appium.options.android import UiAutomator2Options


def create_android_driver() -> webdriver.Remote:
    apk_path = Path(
        os.environ.get(
            "TINK_ANDROID_APK_PATH",
            "android-app/app/build/outputs/apk/debug/app-debug.apk",
        )
    ).resolve()
    if not apk_path.exists():
        raise AssertionError(
            f"Android APK not found at {apk_path}. Build the debug APK or set TINK_ANDROID_APK_PATH."
        )

    capabilities = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": os.environ.get("TINK_ANDROID_DEVICE_NAME", "Android Emulator"),
        "app": str(apk_path),
        "appPackage": os.environ.get("TINK_ANDROID_APP_PACKAGE", "app.tinks.tink"),
        "appActivity": os.environ.get("TINK_ANDROID_APP_ACTIVITY", ".MainActivity"),
        "autoGrantPermissions": True,
        "noReset": False,
        "fullReset": False,
        "newCommandTimeout": 120,
    }
    server_url = os.environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
    options = UiAutomator2Options().load_capabilities(capabilities)
    return webdriver.Remote(server_url, options=options)
