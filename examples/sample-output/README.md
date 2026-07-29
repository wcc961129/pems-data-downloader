# Small real-data format preview

These files are intentionally limited to a header and one representative row
or feature so a new user can evaluate the schema without downloading a PeMS
archive.

The previews were produced by live authenticated downloads:

| Preview | PeMS source | Verified date |
|---|---|---|
| `observations.csv` | District 7 Station 5-Minute | 2026-07-27 |
| `observations_hour.csv` | District 7 Station Hour | 2026-06 |
| `stations.csv` | Station Metadata applicable to the sample | 2026 |
| `edges.csv` | Project-generated postmile-neighbor graph | 2026-07-27 |
| `detectors.geojson` | Project-generated detector point | 2026-07-27 |

Before recreating them, confirm current availability and station metadata:

```bash
uv run pems-data latest --district 7
uv run pems-data stations \
  --district 7 \
  --date 2026-07-27 \
  --freeway 105 \
  --direction E \
  --lane-type ML \
  --limit 5
```

Recreate the five-minute sample:

```bash
uv run pems-data fetch \
  --granularity 5min \
  --district 7 \
  --start 2026-07-27T00:00 \
  --end 2026-07-27T00:10 \
  --station-id 760063,760074,760080,767838,773656 \
  --with-road-network \
  --output data/sample-5min
```

Recreate the hourly sample:

```bash
uv run pems-data fetch \
  --granularity hour \
  --district 7 \
  --start 2026-06-01T00:00 \
  --end 2026-06-01T02:00 \
  --station-id 760063,760074,760080,767838,773656 \
  --output data/sample-hour
```

The complete source archives and browser state are not included. The samples
are attributed to Caltrans PeMS and are provided for format evaluation,
research, and education. Review [DISCLAIMER.md](../../DISCLAIMER.md) and the
current [Caltrans Conditions of Use](https://dot.ca.gov/conditions-of-use)
before redistributing source data.
