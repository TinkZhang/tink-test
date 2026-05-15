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

## Structure

- `features/`: `.feature` files only.
- `tests/`: pytest-bdd step bindings and test files named `test_*.py`.
- `api/`: reusable black-box API clients built on `requests`.
