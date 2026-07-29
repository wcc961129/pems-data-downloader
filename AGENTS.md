# Agent instructions

This file defines repository-specific guidance for coding agents working on the
Caltrans PeMS Data Downloader. It complements, but does not replace, the
project documentation and the user's explicit instructions.

## Project purpose

This is a Python CLI for discovering and downloading authenticated Caltrans
PeMS Station data. It produces traceable research outputs rather than silently
making modeling choices.

Primary users are transportation researchers and students who need:

- official Station 5-Minute or Station Hour observations;
- detector metadata and geographic locations;
- reproducible manifests and research-ready tables;
- optional Caltrans State Highway Network geometry;
- explicit data-quality and graph-construction boundaries.

## Repository map

- `pems_data/`: downloader, CLI, parsing, filtering, export, and diagnostics.
- `tests/`: credential-free unit tests.
- `examples/sample-output/`: minimal real-format previews.
- `docs/user-guide*.md`: task-oriented user instructions.
- `docs/data-format.md`: schemas, units, and quality-field meanings.
- `docs/architecture.md`: implementation structure.
- `docs/development.md`: environment, tests, build, and live validation.
- `CHANGELOG.md`: cumulative user-visible change history.

Do not duplicate detailed user or developer guidance here. Link to the
canonical document when more context is needed.

## Required workflow

Before changing behavior:

1. Read the relevant implementation, tests, and documentation.
2. State any assumption that affects data meaning, compatibility, or scope.
3. Prefer the smallest change that satisfies the request.
4. Add or update tests for behavior changes.
5. Update both English and Chinese documentation when user-facing instructions
   change.
6. Add a timestamped entry at the top of `CHANGELOG.md`.

Use the repository-managed environment:

```bash
uv sync --locked --dev
uv run pytest -q
uv run pems-data profiles
```

After dependency changes, also run:

```bash
uv lock
uv sync --locked --dev
```

Release artifacts can be checked with:

```bash
uv build
```

## Data semantics

- `--granularity 5min` uses official PeMS Station 5-Minute archives.
- `--granularity hour` uses official PeMS Station Hour archives.
- Never describe hourly output as a sum calculated from five-minute rows.
- A timestamp is the start of one observation interval, not a displayed time
  range.
- Preserve the timezone offset in exported ISO 8601 timestamps.
- Preserve `observed_percent`; a numerical value may still be PeMS-imputed.
- Do not treat every zero flow, speed, or occupancy value as missing.
- Do not assume every local day contains 288 five-minute rows or 24 hourly
  rows; California daylight-saving transitions change those counts.
- `edges.csv` is a reproducible postmile-neighbor approximation, not official
  Caltrans topology.
- Do not claim support for another Clearinghouse dataset family until its live
  filename pattern and schema have been verified and tested.

See `docs/data-format.md` and `docs/road-network.md` before changing exports or
graph behavior.

## Authentication and data safety

Never commit, print, upload, or include in screenshots:

- PeMS usernames or passwords;
- cookies or authenticated request headers;
- `.pems/storage-state.json`;
- complete downloaded PeMS source archives;
- private local paths that reveal account information.

Unit tests must not require credentials or live PeMS access. When a requested
task genuinely needs live validation, use the narrowest useful District,
period, and station selection. Keep generated downloads under the ignored
`data/` directory and report what was transferred.

Do not weaken the permissions applied to the saved browser session on Unix.
Account for the documented Windows permission difference.

## Documentation rules

- Keep `README.md` and `README.zh-CN.md` aligned.
- Keep `docs/user-guide.md` and `docs/user-guide.zh-CN.md` aligned.
- Use current `latest` and `stations` discovery flows instead of encouraging
  users to guess dates or station IDs.
- Clearly distinguish verified behavior from planned support.
- Use one header and one representative row for format previews.
- Keep sample dates labeled as verified examples, not permanent latest dates.
- Link detailed material from the root README instead of making the README an
  implementation manual.
- Record process and design explanations in `docs/`, not as long source-code
  comments.

## Cross-platform expectations

Core command names and arguments must remain usable on Windows, macOS, and
Linux. When adding commands to documentation:

- use Bash/Zsh syntax for macOS and Linux;
- provide PowerShell syntax when line continuation or paths differ;
- avoid assuming Unix file modes exist on Windows;
- retain the conditional Windows `tzdata` dependency;
- update the CI matrix when changing the supported Python or OS range.

## Change boundaries

- Preserve unrelated user changes in a dirty worktree.
- Avoid broad refactors during a focused bug or documentation task.
- Do not silently change output schemas, filenames, units, or manifest fields.
- Do not add model preprocessing choices such as imputation, normalization,
  data splits, or forecast horizons to the downloader by default.
- Keep generated artifacts and downloaded data out of version control unless
  they are intentionally minimal, attributed format samples.

See `CONTRIBUTING.md`, `DISCLAIMER.md`, and `docs/development.md` before
preparing a release or accepting a new research profile.
