# User-journey optimization report

## Objective

Reduce the time and cost between cloning the repository and completing a
correct first PeMS download.

## Implemented changes

### Correct selection

Explicit station IDs now intersect with freeway, direction, lane type, county,
and bounding-box selectors. Metadata is validated before traffic archives are
discovered or downloaded.

### Fail-fast behavior

Zero matching stations stop during preflight. Zero observation rows fail by
default, with `--allow-empty` available for explicit automated use.

### Discovery

- `pems-data latest` reports current five-minute and hourly source periods.
- `pems-data stations` searches applicable metadata and prints usable IDs.
- `pems-data doctor` checks local runtime, timezone, browser, session, and
  permissions.

### Feedback

Transfers display file size, progress, and throughput. Fetches display a
preflight plan and final observation, station, and edge counts. CLI help now
documents defaults, units, inclusive timestamps, and selector behavior.

### Platform support

Windows receives `tzdata` through a conditional locked dependency. CI is
configured for Python 3.10–3.12 on Ubuntu and Python 3.12 on macOS and Windows.

## Verification

- Unit coverage includes station-ID intersection, fail-before-download, and
  zero-observation handling.
- Local `doctor` passed all checks on macOS.
- Live `latest` returned District 7 periods `2026-07-27` and `2026-06`.
- Live `stations` matched 41 Route 105 eastbound mainline stations from the
  applicable metadata without downloading a traffic archive.
- A live one-station fetch preflighted one daily archive, displayed progress
  for an 18.1 MiB transfer, produced one observation, and removed the raw
  archive by default.
