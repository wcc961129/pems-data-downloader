# Caltrans PeMS Data Downloader

[![CI](https://github.com/wcc961129/pems-data-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/wcc961129/pems-data-downloader/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue)](pyproject.toml)
[![uv](https://img.shields.io/badge/environment-uv-6f42c1)](https://docs.astral.sh/uv/)
[![License: MIT](https://img.shields.io/badge/code-MIT-yellow.svg)](LICENSE)
[![GE-GAN paper](https://img.shields.io/badge/DOI-10.1016%2Fj.trc.2020.102635-blue)](https://doi.org/10.1016/j.trc.2020.102635)

Download authenticated Caltrans PeMS detector data by region and time range, then export speed, flow, occupancy, detector locations, an approximate detector graph, and optional official Caltrans State Highway Network geometry.

[中文说明](README.zh-CN.md) · [User guide](docs/user-guide.md) · [Data format](docs/data-format.md) · [Road network](docs/road-network.md) · [Sample output](examples/sample-output/README.md)

## What you get

- Exact-time, exact-region Station 5-Minute observations.
- ML-ready `processed/observations.csv.gz` with explicit units and detector coordinates.
- `stations.csv`, `detectors.geojson`, and postmile-neighbor `edges.csv`.
- Optional `caltrans_shn.geojson` from the official Caltrans SHN FeatureServer.
- An interactive `map.html` with detector position and travel direction.
- A reproducibility manifest and the built-in GE-GAN research profile.

## Quick start with uv

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), clone this repository, and run:

```bash
uv sync --locked
uv run playwright install chromium
uv run pems-data auth
```

Complete the PeMS login in the opened browser. Your session is stored only in `.pems/storage-state.json`, protected with `0600` permissions and ignored by Git.

Download five detectors and include official road geometry:

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2014-05-01T00:00 \
  --end 2014-05-01T00:15 \
  --station-id 760063,760074,760080,767838,773656 \
  --with-road-network \
  --output data/i105-east
```

The main research output is:

```text
data/i105-east/
├── manifest.json
├── processed/
│   ├── observations.csv.gz
│   ├── stations.csv
│   ├── detectors.geojson
│   └── edges.csv
└── network/
    ├── caltrans_shn.geojson
    └── map.html
```

See the [user guide](docs/user-guide.md) for bounding-box, freeway, direction, lane-type, county, and GE-GAN profile examples.

## GE-GAN research profile

This project grew from the data acquisition work behind:

> Dongwei Xu, Chenchen Wei, Peng Peng, Qi Xuan, and Haifeng Guo.  
> **GE-GAN: A novel deep learning framework for road traffic state estimation.**  
> *Transportation Research Part C: Emerging Technologies*, 117, 102635, 2020.

[Paper](https://doi.org/10.1016/j.trc.2020.102635) · [Official open-source code](https://github.com/wcc961129/GE-GAN)

```bash
uv run pems-data fetch \
  --profile ge-gan-d7-2014 \
  --output data/ge-gan-d7-2014
```

This prepares the published PeMS source period and detector set. It does not claim bit-for-bit reproduction of every paper preprocessing step. Read the [GE-GAN reproducibility notes](docs/ge-gan.md).

## Research-use notice

This software is intended for research and education. It is not validated for operational traffic control, safety-critical decisions, or real-time incident response. The code is MIT-licensed; downloaded PeMS and Caltrans GIS data remain subject to their source terms and attribution requirements. Read [DISCLAIMER.md](DISCLAIMER.md).

## Documentation

- [User guide](docs/user-guide.md)
- [Data format and units](docs/data-format.md)
- [Official road geometry and approximate graph boundary](docs/road-network.md)
- [Architecture](docs/architecture.md)
- [Development with uv](docs/development.md)
- [Traffic forecasting baseline repository proposal](docs/model-repository-roadmap.md)
- [Contributing](CONTRIBUTING.md)

