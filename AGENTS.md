# Repository Instructions

`tink-test` owns black-box API and Android Appium scenarios for Tink.

- Work on `main`. Sync with `origin/main` before edits, then commit and push each completed Codex change to `origin/main`.
- Verify API changes with `uv run pytest tests/api --bdd-report=reports/api/bdd-report.html` against the development API.
- The Android release workflow runs both Appium suites against its built APK. Run Appium outside release verification on explicit request.
