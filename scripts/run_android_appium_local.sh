#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

suite="mock"
build_apk=0
headless="${TINK_ANDROID_EMULATOR_HEADLESS:-1}"
pytest_args=()

usage() {
  cat <<'USAGE'
Usage: scripts/run_android_appium_local.sh [--suite mock|e2e|all] [--build-apk]

Environment:
  TINK_ANDROID_REPO          Android repo path. Defaults to ../Tink-Super-App.
  TINK_ANDROID_AVD_NAME      AVD to start. Defaults to Pixel_10 or first available AVD.
  TINK_ANDROID_APK_PATH      Existing APK path. Defaults to app/build/outputs/apk/debug/app-debug.apk.
  TINK_ANDROID_EMULATOR_HEADLESS=0  Show emulator window locally.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --)
      shift
      pytest_args=("$@")
      break
      ;;
    --suite)
      suite="${2:-}"
      shift 2
      ;;
    --suite=*)
      suite="${1#*=}"
      shift
      ;;
    --build-apk)
      build_apk=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$suite" != "mock" && "$suite" != "e2e" && "$suite" != "all" ]]; then
  echo "--suite must be one of: mock, e2e, all" >&2
  exit 2
fi

android_repo="${TINK_ANDROID_REPO:-$repo_root/../Tink-Super-App}"
android_repo="$(cd "$android_repo" && pwd)"

detect_android_sdk() {
  if [ -n "${ANDROID_HOME:-}" ]; then
    echo "$ANDROID_HOME"
    return
  fi
  if [ -n "${ANDROID_SDK_ROOT:-}" ]; then
    echo "$ANDROID_SDK_ROOT"
    return
  fi
  if [ -f "$android_repo/local.properties" ]; then
    sdk_dir="$(awk -F= '$1 == "sdk.dir" { print $2 }' "$android_repo/local.properties" | tail -n 1)"
    if [ -n "$sdk_dir" ]; then
      echo "$sdk_dir"
      return
    fi
  fi
  if [ -d "$HOME/Library/Android/sdk" ]; then
    echo "$HOME/Library/Android/sdk"
    return
  fi
}

android_sdk="$(detect_android_sdk)"
if [ -z "$android_sdk" ] || [ ! -d "$android_sdk" ]; then
  echo "Unable to locate Android SDK. Set ANDROID_HOME or ANDROID_SDK_ROOT." >&2
  exit 1
fi

export ANDROID_HOME="$android_sdk"
export ANDROID_SDK_ROOT="$android_sdk"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

if [ "$build_apk" = "1" ]; then
  "$android_repo/scripts/build-appium-debug-apk.sh"
fi

apk_path="${TINK_ANDROID_APK_PATH:-$android_repo/app/build/outputs/apk/debug/app-debug.apk}"
if [ ! -f "$apk_path" ]; then
  echo "APK not found at $apk_path. Re-run with --build-apk or set TINK_ANDROID_APK_PATH." >&2
  exit 1
fi
export TINK_ANDROID_APK_PATH="$apk_path"

if ! command -v appium >/dev/null 2>&1; then
  echo "Appium is not installed. Install it with: npm install -g appium" >&2
  exit 1
fi

if ! appium driver list --installed 2>&1 | perl -pe 's/\e\[[0-9;]*m//g' | grep -q "uiautomator2"; then
  appium driver install uiautomator2
fi

avd_name="${TINK_ANDROID_AVD_NAME:-}"
if [ -z "$avd_name" ]; then
  if "$ANDROID_HOME/emulator/emulator" -list-avds | grep -qx "Pixel_10"; then
    avd_name="Pixel_10"
  else
    avd_name="$("$ANDROID_HOME/emulator/emulator" -list-avds | head -n 1)"
  fi
fi

if [ -z "$avd_name" ]; then
  echo "No Android AVD found. Create an API 35 AVD first." >&2
  exit 1
fi

booted_device="$(adb devices | awk 'NR > 1 && $1 ~ /^emulator-/ && $2 == "device" { print $1; exit }')"
emulator_pid=""
if [ -z "$booted_device" ]; then
  emulator_args=(-avd "$avd_name" -no-snapshot-save -noaudio -no-boot-anim -no-metrics)
  if [ "$headless" = "1" ]; then
    emulator_args+=(-no-window -gpu swiftshader_indirect)
  fi
  "$ANDROID_HOME/emulator/emulator" "${emulator_args[@]}" >/tmp/tink-local-emulator.log 2>&1 &
  emulator_pid="$!"
  for _ in $(seq 1 120); do
    booted_device="$(adb devices | awk 'NR > 1 && $1 ~ /^emulator-/ && $2 == "device" { print $1; exit }')"
    if [ -n "$booted_device" ]; then
      break
    fi
    sleep 2
  done
fi

if [ -z "$booted_device" ]; then
  echo "No running emulator was found after starting AVD '$avd_name'." >&2
  echo "Emulator log: /tmp/tink-local-emulator.log" >&2
  exit 1
fi

export ANDROID_SERIAL="$booted_device"
export TINK_ANDROID_DEVICE_UDID="$booted_device"

cleanup() {
  if [ -n "$emulator_pid" ] && [ "${TINK_ANDROID_KEEP_EMULATOR:-0}" != "1" ]; then
    adb emu kill >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

adb wait-for-device
for _ in $(seq 1 180); do
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

run_suite() {
  local selected_suite="$1"
  export TINK_RUN_APPIUM=1
  export TINK_ANDROID_SUITE="$selected_suite"
  export TINK_ANDROID_POST_BOOT_SLEEP="${TINK_ANDROID_POST_BOOT_SLEEP:-5}"

  if [ "$selected_suite" = "mock" ]; then
    export TINK_ANDROID_API_BASE_URL_OVERRIDE="${TINK_ANDROID_API_BASE_URL_OVERRIDE:-http://10.0.2.2:8765/}"
  else
    unset TINK_ANDROID_API_BASE_URL_OVERRIDE
  fi

  if [ "${#pytest_args[@]}" -gt 0 ]; then
    bash .github/scripts/run_android_appium_suite.sh "${pytest_args[@]}"
  else
    bash .github/scripts/run_android_appium_suite.sh
  fi
}

if [ "$suite" = "all" ]; then
  run_suite e2e
  run_suite mock
else
  run_suite "$suite"
fi
