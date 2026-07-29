# Changelog

All notable changes to this project will be documented in this file.

## 2026-07-29 12:31 CST — User-journey and fail-fast optimization

### Background

A first-time user could not discover valid dates or station IDs from the CLI,
received little progress feedback, and could trigger large archive downloads
before invalid selectors were detected.

### Functionality

- Fixed explicit station IDs to intersect with all metadata selectors.
- Moved station validation ahead of traffic archive discovery and download.
- Added zero-observation protection with an explicit `--allow-empty` override.
- Added `latest`, `stations`, and `doctor` discovery and diagnostic commands.
- Added transfer progress, preflight plans, completion summaries, and
  descriptive CLI help.
- Added a conditional Windows `tzdata` dependency and Ubuntu/macOS/Windows CI
  matrix.

### Documentation

- Added a complete Chinese user guide and linked it from the Chinese README.
- Updated user paths to discover availability and station IDs before fetching.
- Synchronized current examples and documented fail-fast behavior.

### Potential future optimizations

- Add an optional online session check to `doctor`.
- Add machine-readable JSON output to discovery commands.
- Add archive size estimates to preflight when PeMS provides reliable sizes.

## 2026-07-29 12:14 CST — Platform-specific README guidance

### Background

The core uv and downloader commands are cross-platform, but the README used
POSIX shell syntax without distinguishing verified support from expected
Windows compatibility.

### Documentation

- Added a support matrix for Windows, macOS, and Linux.
- Added copyable macOS/Linux Bash and Windows PowerShell setup commands.
- Documented Bash backslash versus PowerShell backtick line continuation.
- Documented the current Windows `tzdata` workaround, Unix permission
  difference, Linux browser dependency command, and CI coverage boundary.

### Potential future optimizations

- Add a conditional Windows `tzdata` dependency to the lockfile.
- Expand CI to Windows and macOS before marking both platforms formally
  verified.

## 2026-07-29 12:05 CST — Official Station Hour support and current samples

### Background

The downloader exposed only PeMS Station 5-Minute archives even though the
authenticated Clearinghouse also provides official Station Hour data. The
documentation examples were from 2014 and did not let new users compare the
supported schemas quickly.

### Functionality

- Added `--granularity 5min|hour`, with `5min` remaining the default.
- Added PeMS monthly Station Hour catalog discovery and archive parsing.
- Added explicit `flow_veh_hour` output and manifest source-granularity fields.
- Refreshed real examples from District 7 data available in 2026.
- Added one-row format previews and a generated road-network screenshot to both
  READMEs.

### Key changes

- Extended planner and catalog logic for
  `dDD_text_station_hour_YYYY_MM.txt.gz`.
- Kept profile-based GE-GAN exports restricted to five-minute source data.
- Added tests for monthly archive deduplication, parsing, and hourly flow
  labeling.
- Documented daily versus monthly transfer cost and unsupported Clearinghouse
  dataset families.

### Potential future optimizations

- Add a read-only `latest` command for each District and granularity.
- Add Station Day, AADT, and other families with schema-specific parsers and
  verified samples.
- Add optional streaming archive filtering if PeMS later exposes a compatible
  server-side or chunked interface.

## 0.2.0 - 2026-07-29 11:38 CST

### Added

- uv-managed Python 3.12 environment, cross-platform lockfile, uv-based CI, and detailed user/developer commands.
- ML-ready observations with explicit speed, flow, occupancy, quality, coordinate, route, direction, and lane-type fields.
- Detector node table, GeoJSON points, and transparent postmile-neighbor research edges.
- Optional official Caltrans SHN road geometry and interactive detector-direction map.
- Small real PeMS sample output covering five detectors and four five-minute intervals.
- Research-use disclaimer, data dictionary, road-network boundary, and baseline-model repository roadmap.

### Changed

- Manifest artifact paths are relative to the output directory.
- Root English and Chinese READMEs now act as concise entry points to task-focused documentation.
- Package metadata uses an SPDX license expression for warning-free uv builds.

### Fixed

- Read the authenticated Clearinghouse JSON catalog directly instead of relying on legacy page animation timing.
- Report non-successful PeMS catalog responses with their HTTP status and URL.
- Select metadata published on or before the requested data date instead of falling back to a future metadata snapshot.
- Escape detector metadata before rendering interactive-map popups.

### Verified

- Completed a live District 7 smoke download for station `767838` from `2014-05-01T00:00` through `00:10`, producing three observations from 1,332,864 streamed source rows.
- Completed a live uv-based v0.2 smoke run for five Route 105 detectors, producing 20 ML-ready observations, five detector features, four research edges, two official SHN features, and an interactive map.

## 0.1.0 - 2026-07-29

### Added

- One-time PeMS browser authentication with protected local session state.
- District and time-range planning for Station 5-Minute Clearinghouse files.
- Station selection by bounding box, ID, freeway, direction, lane type, and county.
- Resumable authenticated downloads, streaming filters, and reproducibility manifests.
- Built-in `ge-gan-d7-2014` research profile.
- GE-GAN-compatible weekday and weekend matrix exports.
- English and Chinese documentation, CI, citation metadata, and issue templates.
