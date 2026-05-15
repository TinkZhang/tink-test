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
uv run pytest --bdd-report=reports/bdd-report.html
```

Override the target API:

```sh
TINK_API_BASE_URL=http://localhost:8000/dev uv run pytest --bdd-report=reports/bdd-report.html
```

## Structure

- `features/`: `.feature` files only.
- `tests/`: pytest-bdd step bindings and test files named `test_*.py`.
- `api/`: reusable black-box API clients built on `requests`.
