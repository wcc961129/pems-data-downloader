# User guide

## 1. Prerequisites

PeMS requires an approved account. Register on the [Caltrans PeMS website](https://pems.dot.ca.gov/) before downloading data.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and verify it:

```bash
uv --version
```

uv reads `.python-version`, installs a compatible Python when needed, creates `.venv`, and resolves the committed `uv.lock`.

```bash
git clone https://github.com/wcc961129/pems-data-downloader.git
cd pems-data-downloader
uv sync --locked
uv run playwright install chromium
```

## 2. Authenticate

```bash
uv run pems-data auth
```

Log in to PeMS in the opened browser. The resulting browser state is written to `.pems/storage-state.json` with `0600` permissions. It contains session cookies and must never be committed or shared.

The form can also be filled from environment variables:

```bash
PEMS_USERNAME='your-name' \
PEMS_PASSWORD='your-password' \
uv run pems-data auth
```

If PeMS reports an expired session, run the authentication command again.

## 3. Select data

All naive timestamps are interpreted in `America/Los_Angeles`, including daylight saving time. A date-only end value includes the full day.

### Detector IDs

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2014-05-01T00:00 \
  --end 2014-05-01T00:15 \
  --station-id 760063,760074,760080,767838,773656 \
  --output data/by-station
```

### Bounding box

The order is `west,south,east,north`.

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2014-05-01 \
  --end 2014-05-02 \
  --bbox=-118.38,33.92,-118.34,33.95 \
  --output data/by-bbox
```

### Road, direction, and lane type

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2014-05-01 \
  --end 2014-05-02 \
  --freeway 105 \
  --direction E \
  --lane-type ML \
  --output data/i105-east-mainline
```

### County

County uses the numeric FIPS county code stored in PeMS metadata.

```bash
uv run pems-data fetch \
  --district 4 \
  --start 2025-06-01 \
  --end 2025-06-01T01:00 \
  --county 1 \
  --lane-type ML \
  --output data/alameda-mainline
```

Selectors are combined with logical AND. Multiple values can be comma-separated or supplied by repeating the option.

## 4. Include official road geometry

Add `--with-road-network`:

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2014-05-01T00:00 \
  --end 2014-05-01T00:15 \
  --station-id 760063,760074,760080,767838,773656 \
  --with-road-network \
  --output data/i105-network
```

This queries the public Caltrans SHN Lines FeatureServer for relevant routes inside the selected detector bounding box. It creates:

- `network/caltrans_shn.geojson`: official State Highway Network line geometry;
- `network/map.html`: interactive detector and road map.

The HTML uses Leaflet and OpenStreetMap tiles from their public CDNs, so an internet connection is required when opening it.

## 5. GE-GAN profile

```bash
uv run pems-data profiles

uv run pems-data fetch \
  --profile ge-gan-d7-2014 \
  --output data/ge-gan-d7-2014
```

The profile additionally produces the station-as-columns GE-GAN compatibility matrices. Read [ge-gan.md](ge-gan.md) before making a reproducibility claim.

## 6. PeMS download granularity

PeMS Station 5-Minute source archives are organized by District and day. A ten-minute request still transfers the applicable daily archive, then this tool:

1. streams the archive without loading it fully into memory;
2. keeps only the selected detectors and exact timestamps;
3. creates research-ready outputs;
4. deletes the daily archive unless `--keep-raw` is supplied.

Downloads are serial because the PeMS Clearinghouse explicitly warns against concurrent automated downloads.

## 7. Resume and troubleshoot

- Interrupted files use a `.part` suffix and resume with HTTP Range when supported.
- Existing complete files are reused.
- HTML returned in place of a data file is treated as an expired session.
- Use `--keep-raw` when debugging a parser or preserving the official archive.
- Never publish `.pems/storage-state.json`, credentials, or complete source archives.

