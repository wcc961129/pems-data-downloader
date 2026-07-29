# User guide

[中文用户指南](user-guide.zh-CN.md)

## 1. Prerequisites

PeMS requires an approved account. Register on the
[Caltrans PeMS website](https://pems.dot.ca.gov/) before downloading data.

Follow the platform-specific setup in the
[root README](../README.md#windows-macos-and-linux). Then verify the local
environment:

```bash
uv run pems-data doctor
```

The command checks Python, the California timezone, Playwright Chromium, the
PeMS browser session, and session-file permissions.

## 2. Authenticate

```bash
uv run pems-data auth
```

Log in to PeMS in the opened browser. The resulting browser state is written
to `.pems/storage-state.json`. It contains session cookies and must never be
committed or shared.

On Bash/Zsh, the login form can be filled from temporary environment
variables:

```bash
PEMS_USERNAME='your-name' \
PEMS_PASSWORD='your-password' \
uv run pems-data auth
```

PowerShell uses:

```powershell
$Env:PEMS_USERNAME="your-name"
$Env:PEMS_PASSWORD="your-password"
uv run pems-data auth
Remove-Item Env:PEMS_USERNAME, Env:PEMS_PASSWORD
```

If PeMS reports an expired session, run `auth` again. Authentication launches
a visible browser and therefore requires a desktop-capable environment.

## 3. Discover available data

Do not guess the newest date. Query the authenticated Clearinghouse:

```bash
uv run pems-data latest --district 7
```

Example:

```csv
district,granularity,latest_period,source_file
7,5min,2026-07-27,d07_text_station_5min_2026_07_27.txt.gz
7,hour,2026-06,d07_text_station_hour_2026_06.txt.gz
```

Find station IDs from metadata before downloading a traffic archive:

```bash
uv run pems-data stations \
  --district 7 \
  --date 2026-07-27 \
  --freeway 105 \
  --direction E \
  --lane-type ML \
  --limit 5
```

The command displays station ID, route, direction, lane type, postmile,
coordinates, and name. It accepts the same bounding-box, station, freeway,
direction, lane-type, and county selectors as `fetch`.

## 4. Fetch observations

All naive timestamps are interpreted in `America/Los_Angeles`, including
daylight saving time. Start and end timestamps are inclusive. A date-only end
value includes the full day.

### Five-minute observations

```bash
uv run pems-data fetch \
  --granularity 5min \
  --district 7 \
  --start 2026-07-27T00:00 \
  --end 2026-07-27T00:10 \
  --station-id 760063,760074,760080,767838,773656 \
  --output data/i105-5min
```

### Hourly observations

```bash
uv run pems-data fetch \
  --granularity hour \
  --district 7 \
  --start 2026-06-01T00:00 \
  --end 2026-06-01T02:00 \
  --station-id 760063,760074,760080,767838,773656 \
  --output data/i105-hour
```

The default granularity is `5min`. Hourly values come directly from the
official PeMS Station Hour archive.

### Bounding box

The order is `west,south,east,north`:

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2026-07-27T00:00 \
  --end 2026-07-27T00:10 \
  --bbox=-118.38,33.92,-118.34,33.95 \
  --output data/by-bbox
```

### Road, direction, and lane type

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2026-07-27T00:00 \
  --end 2026-07-27T00:10 \
  --freeway 105 \
  --direction E \
  --lane-type ML \
  --output data/i105-east-mainline
```

### County

County uses the numeric FIPS code stored in PeMS metadata:

```bash
uv run pems-data fetch \
  --district 4 \
  --start 2025-06-01T00:00 \
  --end 2025-06-01T01:00 \
  --county 1 \
  --lane-type ML \
  --output data/alameda-mainline
```

Selectors are combined with logical AND. Multiple values may be comma
separated or supplied by repeating an option. Metadata preflight completes
before traffic archives are downloaded. Zero matching stations stop
immediately.

`fetch` requires an explicit District to prevent accidental statewide archive
downloads. Repeat `--district` or use comma-separated values for a deliberate
multi-District request.

Zero observation rows are treated as an error. Automated workflows that
intentionally accept an empty dataset can add `--allow-empty`.

## 5. Include official road geometry

Add `--with-road-network`:

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2026-07-27T00:00 \
  --end 2026-07-27T00:10 \
  --station-id 760063,760074,760080,767838,773656 \
  --with-road-network \
  --output data/i105-network
```

This creates:

- `network/caltrans_shn.geojson`: official State Highway Network lines;
- `network/map.html`: an interactive detector and road map.

The map uses Leaflet and OpenStreetMap assets from public CDNs. Internet
access is required when opening it.

## 6. Understand transfer cost

Station 5-Minute archives are organized by District and day. A ten-minute
request still transfers the applicable daily archive.

Station Hour archives are organized by District and month. A two-hour request
still transfers the applicable monthly archive.

The downloader:

1. validates station metadata;
2. shows the station and source-archive preflight plan;
3. downloads archives serially with progress;
4. streams rows without loading the archive fully into memory;
5. keeps exact stations and inclusive timestamps;
6. deletes raw archives unless `--keep-raw` is supplied;
7. prints observation, station, and edge counts.

Downloads are serial because the PeMS Clearinghouse warns against concurrent
automated downloads.

## 7. Inspect output

The primary table is `processed/observations.csv.gz`. Inspect the first two
rows without adding pandas:

```bash
uv run python -c "import gzip,itertools; print(''.join(itertools.islice(gzip.open('data/i105-5min/processed/observations.csv.gz','rt'),2)))"
```

PowerShell can run the same command unchanged. See
[data-format.md](data-format.md) for columns, units, detector metadata, graph
edges, and manifest fields.

## 8. GE-GAN profile

```bash
uv run pems-data profiles

uv run pems-data fetch \
  --profile ge-gan-d7-2014 \
  --output data/ge-gan-d7-2014
```

The profile produces station-as-columns GE-GAN compatibility matrices. Read
[ge-gan.md](ge-gan.md) before making a reproducibility claim.

## 9. Other open data and modeling

For research beyond PeMS, use
[wcc961129/transdim](https://github.com/wcc961129/transdim) to find open data
or source links for Guangzhou, Hangzhou, Birmingham, Seattle, London, NYC,
Portland, NGSIM, electricity load, and temperature.

`transdim` also provides traffic imputation and forecasting notebooks. This
project's `processed/observations.csv.gz` can be reshaped into a
station-by-time matrix or station-by-day-by-interval tensor for those models.
Preserve `observed_percent` or an explicit missing-value mask during
conversion; do not automatically interpret every numerical zero as missing.

See the [transdim integration notes](related-projects/transdim.md) for project
roles, dataset directories, conversion boundaries, and licensing.

## 10. Resume and troubleshoot

- Run `uv run pems-data doctor` before investigating deeper failures.
- Interrupted files use a `.part` suffix and resume with HTTP Range when
  supported.
- Existing complete files are reused.
- HTML returned in place of data is treated as an expired session.
- A missing expected archive usually means the requested period is not
  published; check `latest`.
- Zero stations indicate a District or metadata-selector mismatch; check
  `stations`.
- Zero observations usually indicate unavailable timestamps or inactive
  stations.
- Use `--keep-raw` only when debugging a parser or preserving the official
  archive.
- Never publish `.pems/storage-state.json`, credentials, or complete source
  archives.
