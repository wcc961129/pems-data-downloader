# Research outputs v0.2 implementation report

## Background

The original filtered export preserved PeMS station fields but did not make detector coordinates, units, road geometry, or graph semantics prominent enough for traffic forecasting users.

## Decisions

1. Preserve `filtered/station_5min.csv.gz` for traceability.
2. Add a tidy, unit-labeled `processed/observations.csv.gz` rather than silently choosing a dense tensor, missing-value policy, or train/test split.
3. Export the applicable PeMS metadata snapshot as a detector node table and GeoJSON.
4. Query the public Caltrans SHN Lines FeatureServer only when requested.
5. Label postmile-neighbor edges as approximate and keep them separate from official road geometry.
6. Keep the downloader independent from the proposed forecasting-baseline repository.

## Live verification

Executed on 2026-07-29:

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2014-05-01T00:00 \
  --end 2014-05-01T00:15 \
  --station-id 760063,760074,760080,767838,773656 \
  --with-road-network \
  --output data/smoke-v02
```

Observed results:

- 1,332,864 PeMS source rows streamed;
- 20 selected detector-time rows;
- 5 detector metadata and point features;
- 4 approximate postmile-neighbor edges;
- 2 official SHN line features;
- one interactive HTML map;
- zero daily raw files retained after successful processing.

The final manifest uses relative artifact paths.

## Scientific boundaries

- `observed_percent` is retained because valid numeric speed or flow values can still be PeMS-imputed.
- SHN geometry may be newer than historical PeMS observations.
- Approximate edges do not encode ramps, merges, splits, lane transitions, or every upstream/downstream relationship.
- Dataset splits, normalization, imputation, windowing, masks, and evaluation metrics remain explicit model-repository responsibilities.

