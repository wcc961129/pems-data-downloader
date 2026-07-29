# Changelog

All notable changes to this project will be documented in this file.

## Unreleased - 2026-07-29 11:05 CST

### Fixed

- Read the authenticated Clearinghouse JSON catalog directly instead of relying on legacy page animation timing.
- Report non-successful PeMS catalog responses with their HTTP status and URL.
- Select metadata published on or before the requested data date instead of falling back to a future metadata snapshot.

### Verified

- Completed a live District 7 smoke download for station `767838` from `2014-05-01T00:00` through `00:10`, producing three observations from 1,332,864 streamed source rows.

## 0.1.0 - 2026-07-29

### Added

- One-time PeMS browser authentication with protected local session state.
- District and time-range planning for Station 5-Minute Clearinghouse files.
- Station selection by bounding box, ID, freeway, direction, lane type, and county.
- Resumable authenticated downloads, streaming filters, and reproducibility manifests.
- Built-in `ge-gan-d7-2014` research profile.
- GE-GAN-compatible weekday and weekend matrix exports.
- English and Chinese documentation, CI, citation metadata, and issue templates.
