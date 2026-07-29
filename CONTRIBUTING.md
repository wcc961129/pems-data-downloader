# Contributing

Thank you for improving the PeMS Data Downloader.

## Choose the right channel

- Use the Bug Report form for a reproducible defect.
- Use the Feature Request form for a new dataset, selector, exporter, or
  reliability improvement.
- Follow `SECURITY.md` instead of opening a public Issue for a vulnerability.
- Read `SUPPORT.md` for PeMS account, source-data, and model-specific support.

Search existing Issues before creating a new one. A proposed dataset type must
include a public schema or filename-pattern source.

## Development setup

Fork the repository, create a focused branch, and prepare the environment:

```bash
git clone https://github.com/YOUR-USERNAME/pems-data-downloader.git
cd pems-data-downloader
git switch -c feature/short-description
uv sync --locked --dev
uv run pytest -q
uv run pems-data profiles
```

See [docs/development.md](docs/development.md) for lockfile, build, and live-validation commands.

## Pull requests

- Keep each pull request focused on one dataset type, bug, or documented behavior.
- Link the related Issue and explain the user-visible result.
- Add tests for filename planning, metadata parsing, or output conversion changes.
- Do not commit downloaded PeMS files, credentials, `.pems/storage-state.json`, cookies, or screenshots containing account information.
- Do not claim compatibility with a PeMS dataset until its filename pattern and schema have been verified.
- Synchronize English and Chinese user documentation when applicable.
- Update the changelog for user-visible behavior.
- Complete the Pull Request template and report all validation commands.

CI must pass before merge. The repository owner reviews proposed changes and
decides whether to merge. External contributors do not need direct repository
access; a fork-based Pull Request is the normal contribution path.

The project uses squash merging so each accepted Pull Request has one focused
commit on `main`.

## Live validation

Unit tests must not depend on PeMS credentials. Only perform an authenticated
smoke test when the change cannot be validated locally. Use the narrowest
useful District, period, and station selection, and describe the sanitized
result in the Pull Request.

## Research profiles

A research profile must include a public source for its time range and station IDs, an explicit reproducibility boundary, and a deterministic export test. Profiles must not bundle data whose redistribution terms are unclear.

## Reporting problems

Use the bug template and include the command, operating system, Python version, and sanitized error. Never paste credentials or browser state.

Participation is subject to [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
