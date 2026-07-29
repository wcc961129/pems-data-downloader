# Changelog

All notable changes to this project will be documented in this file.

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
