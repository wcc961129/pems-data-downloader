## Summary

Describe the problem, the chosen solution, and the user-visible result.

Closes #

## Validation

List the commands you ran and their results.

```text
uv run pytest -q
uv run pems-data profiles
```

## Data and compatibility checklist

- [ ] The change is focused and does not include unrelated refactoring.
- [ ] Tests cover changed parsing, filtering, planning, or export behavior.
- [ ] No PeMS credentials, cookies, browser state, or complete source archives
      are included.
- [ ] Five-minute, hourly, timestamp, quality-field, and graph semantics remain
      accurate.
- [ ] Output schema, filenames, units, and manifest changes are documented.
- [ ] English and Chinese user documentation are synchronized when applicable.
- [ ] `CHANGELOG.md` contains a timestamped entry for user-visible changes.
- [ ] Windows, macOS, and Linux implications have been considered.

## Live validation

State whether authenticated PeMS validation was necessary. If performed,
describe the sanitized District, period, station count, and result without
including credentials or private files.
