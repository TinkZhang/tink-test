#!/usr/bin/env bash

set +e

appium --log-level error > appium.log 2>&1 &
appium_ready=0
for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:4723/status >/dev/null 2>&1; then
    appium_ready=1
    break
  fi
  sleep 2
done

if [ "$appium_ready" != "1" ]; then
  echo "Appium server did not become ready"
  cat appium.log
  {
    echo "e2e_status=1"
    echo "mock_status=1"
  } >> "$GITHUB_OUTPUT"
  exit 0
fi

selector="android"
if [ "$GITHUB_EVENT_NAME" = "pull_request" ]; then
  selector="android and smoke"
fi

TINK_ANDROID_APK_PATH="$PWD/app-e2e-debug.apk" \
  timeout 12m uv run pytest tests/android -m "$selector and e2e" \
    --bdd-report=reports/android/e2e/bdd-report.html
e2e_status=$?

TINK_ANDROID_APK_PATH="$PWD/app-mock-debug.apk" \
  timeout 12m uv run pytest tests/android -m "$selector and mock" \
    --bdd-report=reports/android/mock/bdd-report.html
mock_status=$?

{
  echo "e2e_status=$e2e_status"
  echo "mock_status=$mock_status"
} >> "$GITHUB_OUTPUT"

exit 0
