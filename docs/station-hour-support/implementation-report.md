# Station Hour support and sample refresh

## Background

The PeMS Clearinghouse exposes both `Station 5-Minute` and `Station Hour`,
while the downloader previously implemented only the five-minute catalog and
daily filename pattern. The README also used a 2014 sample, which made it hard
for a new user to confirm current availability and distinguish interval units.

## Implemented behavior

- `--granularity 5min` selects daily `station_5min` archives and remains the
  default.
- `--granularity hour` selects monthly `station_hour` archives.
- Exact timestamps and station selectors are applied after the applicable
  official archive is downloaded.
- The processed flow field is named `flow_veh_5min` or `flow_veh_hour`.
- The manifest records both `granularity` and `source_dataset`.
- GE-GAN research profiles remain fixed to five-minute input.

## Live validation

Validation was performed against the authenticated PeMS Clearinghouse on
2026-07-29.

| Check | Five-minute result | Hour result |
|---|---|---|
| District | 7 | 7 |
| Source | `d07_text_station_5min_2026_07_27.txt.gz` | `d07_text_station_hour_2026_06.txt.gz` |
| Requested interval | 2026-07-27 00:00–00:10 | 2026-06-01 00:00–02:00 |
| Selected stations | 5 | 5 |
| Processed rows | 15 | 15 |
| Flow field | `flow_veh_5min` | `flow_veh_hour` |

The five-minute run also returned two Caltrans SHN features and produced the
static screenshot in this directory.

## Boundaries and future work

The Clearinghouse also advertises Station Day, AADT, Link, Census, FasTrak,
Re-ID, and incident products. Their archive naming, metadata, schemas, and
quality semantics differ, so they should be added only with dataset-specific
parsers and live samples rather than routed through the Station parser.

The current CLI requires users to choose a known date. A future `latest`
discovery command could report the newest available period per District and
granularity without downloading an archive.
