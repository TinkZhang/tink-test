#!/usr/bin/env bash

set +e

suite="${TINK_ANDROID_SUITE:-e2e}"
report_dir="reports/android/$suite"
appium_log="appium-$suite.log"
logcat_log="logcat-$suite.log"

mkdir -p "$report_dir"
export TINK_ANDROID_REPORT_DIR="$report_dir"

adb wait-for-device

for _ in $(seq 1 120); do
  boot_completed="$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')"
  dev_bootcomplete="$(adb shell getprop dev.bootcomplete 2>/dev/null | tr -d '\r')"
  if [ "$boot_completed" = "1" ] && [ "$dev_bootcomplete" = "1" ]; then
    break
  fi
  sleep 2
done

adb shell wm dismiss-keyguard >/dev/null 2>&1 || true
adb shell settings put global window_animation_scale 0 >/dev/null 2>&1 || true
adb shell settings put global transition_animation_scale 0 >/dev/null 2>&1 || true
adb shell settings put global animator_duration_scale 0 >/dev/null 2>&1 || true
adb shell pm list packages >/dev/null 2>&1 || true
sleep "${TINK_ANDROID_POST_BOOT_SLEEP:-60}"

adb logcat -c >/dev/null 2>&1
adb logcat -v time > "$logcat_log" 2>&1 &
logcat_pid=$!

appium --log-level info > "$appium_log" 2>&1 &
appium_pid=$!

cleanup() {
  kill "$appium_pid" >/dev/null 2>&1 || true
  kill "$logcat_pid" >/dev/null 2>&1 || true
}
trap cleanup EXIT

appium_ready=0
for _ in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:4723/status >/dev/null 2>&1; then
    appium_ready=1
    break
  fi
  sleep 2
done

if [ "$appium_ready" != "1" ]; then
  echo "Appium server did not become ready"
  cat "$appium_log"
  echo "status=1" >> "$GITHUB_OUTPUT"
  exit 0
fi

if [ -z "${TINK_ANDROID_APK_PATH:-}" ] || [ ! -f "$TINK_ANDROID_APK_PATH" ]; then
  echo "TINK_ANDROID_APK_PATH does not point to an APK: ${TINK_ANDROID_APK_PATH:-}"
  echo "status=1" >> "$GITHUB_OUTPUT"
  exit 0
fi

adb install -r "$TINK_ANDROID_APK_PATH"
install_status=$?
if [ "$install_status" != "0" ]; then
  echo "Failed to preinstall Android APK"
  echo "status=$install_status" >> "$GITHUB_OUTPUT"
  exit 0
fi

if [ -n "${TINK_ANDROID_API_BASE_URL_OVERRIDE:-}" ]; then
  adb shell am broadcast \
    -n app.tinks.tink/.debug.ApiBaseUrlOverrideReceiver \
    -a app.tinks.tink.debug.SET_API_BASE_URL \
    --es base_url "$TINK_ANDROID_API_BASE_URL_OVERRIDE" >/dev/null
else
  adb shell am broadcast \
    -n app.tinks.tink/.debug.ApiBaseUrlOverrideReceiver \
    -a app.tinks.tink.debug.CLEAR_API_BASE_URL >/dev/null
fi

adb shell am force-stop app.tinks.tink >/dev/null 2>&1 || true

selector="android and $suite"
if [ "$GITHUB_EVENT_NAME" = "pull_request" ]; then
  selector="$selector and smoke"
fi

TINK_ANDROID_PREINSTALLED=1 \
  uv run pytest tests/android -m "$selector" \
    --bdd-report="$report_dir/bdd-report.html"
status=$?

echo "status=$status" >> "$GITHUB_OUTPUT"
exit 0
