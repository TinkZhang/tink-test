# tink-test

Black-box E2E tests for Tink APIs and, later, Android/iOS/Mac flows.

The current suite covers the deployed development API with BDD scenarios written in Gherkin and executed through `pytest-bdd`.

## API E2E Tests

Default target:

```sh
https://api.tinks.app/dev
```

Run the tests:

```sh
uv run pytest tests/api --bdd-report=reports/api/bdd-report.html
```

Override the target API:

```sh
TINK_API_BASE_URL=http://localhost:8000/dev uv run pytest tests/api --bdd-report=reports/api/bdd-report.html
```

Current API coverage:

- Root health endpoint
- Weight CRUD
- Haircut CRUD
- Zi upsert and read
- Story create, list, read, delete
- Book lifecycle and notes
- Time create, update, list, statistics, delete
- Merriam statistics

The story generation endpoint and Merriam write endpoint are intentionally not covered yet because they trigger external AI/calendar side effects and do not provide a clean black-box cleanup path.

## Android Appium BDD Tests

Android Appium tests are black-box tests for the Android app. They are skipped unless `TINK_RUN_APPIUM=1` is set.

Two layers are available:

- E2E: the app talks to `https://api.tinks.app/dev`, while tests use the API client for setup and cleanup.
- Mock: the app talks to a local mock server built from JSON fixtures under `fixtures/android/weight`.

Run E2E tests after building or providing a debug APK:

```sh
TINK_RUN_APPIUM=1 \
TINK_ANDROID_APK_PATH=/path/to/app-debug.apk \
uv run pytest tests/android -m "android and e2e" --bdd-report=reports/android/e2e/bdd-report.html
```

Run mock tests with the same debug APK. The Appium runner sets the debug-only API override to `http://10.0.2.2:8765/` before launching the app:

```sh
TINK_RUN_APPIUM=1 \
TINK_ANDROID_APK_PATH=/path/to/app-debug.apk \
TINK_ANDROID_API_BASE_URL_OVERRIDE=http://10.0.2.2:8765/ \
uv run pytest tests/android -m "android and mock" --bdd-report=reports/android/mock/bdd-report.html
```

### Local Android Appium Loop

For faster iteration, build the debug APK locally in `Tink-Super-App`, then run Appium from this repo against a local emulator:

```sh
cd ../Tink-Super-App
scripts/build-appium-debug-apk.sh

cd ../tink-test
scripts/run_android_appium_local.sh --suite e2e
scripts/run_android_appium_local.sh --suite mock
```

The local runner starts an emulator when needed, starts Appium, installs the APK, runs the requested BDD suite, and writes the same HTML reports used by CI:

- `reports/android/e2e/bdd-report.html`
- `reports/android/mock/bdd-report.html`

By default it temporarily sets the emulator viewport to CI's `320x640` size, then restores the previous size/density on exit. Set `TINK_ANDROID_MATCH_CI_VIEWPORT=0` if you want to keep your local emulator's current display size while debugging.

Use `--build-apk` when you want the test repo script to build the local Android APK first:

```sh
scripts/run_android_appium_local.sh --suite mock --build-apk
```

To iterate on one scenario, pass pytest arguments after `--`:

```sh
scripts/run_android_appium_local.sh --suite e2e -- -k "add_and_delete"
```

`Tink-Super-App` owns APK builds in CI and dispatches this repository with the Android workflow run id. GitHub Actions downloads the published `tink-android-debug-apk` artifact, runs Appium with the UiAutomator2 driver on an Android emulator, uploads artifacts, and publishes API/Android report links to GitHub Pages.

During Appium runs, every Appium-backed BDD step captures a screenshot. The generated Android BDD HTML report embeds those screenshots directly under an `Android Step Screenshots` section so the executed flow can be reviewed without downloading a separate artifact.

Required GitHub secrets:

- `Tink-Super-App`: `TINK_TEST_DISPATCH_TOKEN` can dispatch events to `TinkZhang/tink-test`.
- `tink-test`: `TINK_ANDROID_ARTIFACT_TOKEN` can read Android workflow artifacts from `TinkZhang/Tink-Super-App`.

## Structure

- `features/`: `.feature` files only.
- `tests/`: pytest-bdd step bindings and test files named `test_*.py`.
- `api/`: reusable black-box API clients built on `requests`.
- `appium_client/`: Appium driver setup and Android page objects.
- `mock_server/`: local mock HTTP servers for app black-box tests.
- `fixtures/`: JSON fixture data for mock tests.
