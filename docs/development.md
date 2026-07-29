# Development with uv

## Environment

```bash
uv sync --locked --dev
uv run playwright install chromium
```

The committed `.python-version` selects Python 3.12 for local development. `uv.lock` covers all supported Python versions.

## Tests

From the repository root:

```bash
uv run pytest -q
uv run pems-data profiles
```

From another directory:

```bash
uv --directory /path/to/pems-data-downloader run --locked pytest -q
```

`uv run --project` selects dependency metadata but does not change pytest's collection directory; use `--directory` when invoking from outside the repository.

## Lock and build

After changing dependencies:

```bash
uv lock
uv sync --locked --dev
```

Build release artifacts:

```bash
uv build
```

## Live validation

Unit tests must not require PeMS credentials. Live smoke tests use a local ignored session and a narrow time/station selection. Do not commit browser state, full daily archives, or account information.

