# Data format

## Recommended research table

`processed/observations.csv.gz` is the primary model-input table. It is tidy long-form data: one detector and one five-minute interval per row.

| Column | Meaning | Unit |
|---|---|---|
| `timestamp` | ISO 8601 timestamp in California local time | timezone-aware |
| `station_id` | PeMS station identifier | integer |
| `speed_mph` | PeMS flow-weighted average station speed | mph |
| `flow_veh_5min` | Total station flow over the interval | vehicles / 5 min |
| `occupancy_fraction` | Average station occupancy | fraction |
| `observed_percent` | Percentage of lane points observed rather than imputed | percent |
| `latitude` | Detector latitude from applicable PeMS metadata | WGS84 degrees |
| `longitude` | Detector longitude from applicable PeMS metadata | WGS84 degrees |
| `freeway` | State route/freeway number | integer |
| `direction` | Detector travel direction | `N`, `S`, `E`, or `W` |
| `lane_type` | PeMS lane/station type | `ML`, `HV`, `OR`, `FR`, and others |

Example:

```csv
timestamp,station_id,speed_mph,flow_veh_5min,occupancy_fraction,observed_percent,latitude,longitude,freeway,direction,lane_type
2014-05-01T00:00:00-07:00,767838,70.3,143,.0427,100,33.931513,-118.361927,105,E,ML
```

Keep `observed_percent` during training. A numerical value may be imputed by PeMS; it is not automatically equivalent to a directly observed measurement.

## Detector table

`processed/stations.csv` contains one row per selected detector:

- station ID, route, direction, District and County;
- state and absolute postmile;
- latitude and longitude;
- detector length, lane type, lane count and station name.

Use it as the node table for a graph or as static covariates.

## Detector points

`processed/detectors.geojson` contains the same detectors as GeoJSON Points. Each feature includes a `direction_arrow` property for display.

## Approximate graph

`processed/edges.csv` connects consecutive selected detectors after grouping by:

1. freeway;
2. direction;
3. lane type;
4. absolute postmile order.

| Column | Meaning |
|---|---|
| `source_station_id` | First detector |
| `target_station_id` | Next selected detector |
| `distance_miles` | Difference in absolute postmile |
| `method` | Construction rule identifier |

This is a reproducible research adjacency, not an official Caltrans topology. See [road-network.md](road-network.md).

## Source-preserving table

`filtered/station_5min.csv.gz` retains the standard PeMS station-level fields and packs lane-level values into `lane_values`. It is provided for traceability and advanced preprocessing.

## Manifest

`manifest.json` records:

- requested Districts, time range, selectors and research profile;
- selected detector IDs;
- source and metadata filenames;
- input and output row counts;
- generated research and network artifacts;
- official road geometry source when requested.

Artifact paths are relative to the output directory so the dataset can be moved without rewriting its manifest.

## Model preparation boundary

This downloader does not silently choose:

- train, validation and test dates;
- missing-value imputation;
- normalization statistics;
- history and forecast horizon;
- graph self-loops or edge weights.

Those choices affect scientific results and belong in a versioned experiment configuration. See the [baseline repository proposal](model-repository-roadmap.md).

