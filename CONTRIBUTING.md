# Contributing

Thank you for improving the PeMS Data Downloader.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
python -m pytest -q
```

## Pull requests

- Keep each pull request focused on one dataset type, bug, or documented behavior.
- Add tests for filename planning, metadata parsing, or output conversion changes.
- Do not commit downloaded PeMS files, credentials, `.pems/storage-state.json`, cookies, or screenshots containing account information.
- Do not claim compatibility with a PeMS dataset until its filename pattern and schema have been verified.
- Update the changelog for user-visible behavior.

## Research profiles

A research profile must include a public source for its time range and station IDs, an explicit reproducibility boundary, and a deterministic export test. Profiles must not bundle data whose redistribution terms are unclear.

## Reporting problems

Use the bug template and include the command, operating system, Python version, and sanitized error. Never paste credentials or browser state.

