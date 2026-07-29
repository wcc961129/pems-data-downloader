# Small real-data preview

This directory contains a deliberately small, human-readable preview produced from a live PeMS download:

- District 7;
- five eastbound mainline detectors on Route 105;
- `2014-05-01T00:00` through `00:15` California local time;
- 20 detector-time observations.

Recreate it with:

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2014-05-01T00:00 \
  --end 2014-05-01T00:15 \
  --station-id 760063,760074,760080,767838,773656 \
  --with-road-network \
  --output data/sample-output
```

Files:

- `observations.csv`: uncompressed preview of `processed/observations.csv.gz`;
- `stations.csv`: detector attributes and coordinates;
- `edges.csv`: approximate postmile-neighbor graph;
- `detectors.geojson`: detector point features with direction.

The complete daily PeMS source archive and browser state are not included. The sample is attributed to Caltrans PeMS and is provided for format evaluation, research, and education. Review [DISCLAIMER.md](../../DISCLAIMER.md) and the current [Caltrans Conditions of Use](https://dot.ca.gov/conditions-of-use) before redistributing source data.

The `observed_percent` value demonstrates why measurement quality must be retained: station `760063` has values supplied with `0` percent directly observed for this interval.

