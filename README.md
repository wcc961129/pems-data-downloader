# Caltrans PeMS Data Downloader

[![CI](https://github.com/wcc961129/pems-data-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/wcc961129/pems-data-downloader/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/pems-data)](https://pypi.org/project/pems-data/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GE-GAN paper](https://img.shields.io/badge/DOI-10.1016%2Fj.trc.2020.102635-blue)](https://doi.org/10.1016/j.trc.2020.102635)

Download Caltrans PeMS traffic data by region and time range, without manually clicking through one station and one week at a time.

[中文文档](README.zh-CN.md) · [GE-GAN research profile](docs/ge-gan.md) · [Architecture](docs/architecture.md)

## Why this project

Caltrans PeMS provides valuable detector data, but research downloads still require an approved account and interaction with the Clearinghouse website. This tool turns that workflow into a repeatable command:

- select stations by bounding box, detector ID, freeway, direction, lane type, or county;
- select exact start and end times in California local time;
- discover real Clearinghouse download links after authentication;
- resume interrupted downloads and cache raw District files;
- produce a compressed long-format CSV and a reproducibility manifest.

PeMS requires a free registered account. This project does not bypass authentication, redistribute PeMS credentials, or mirror Caltrans data.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
playwright install chromium
```

## Authenticate once

```bash
pems-data auth
```

Complete the PeMS login in the opened browser. The browser session is stored locally in `.pems/storage-state.json` with `0600` permissions and is ignored by Git.

Environment variables can fill the form without putting credentials in source code:

```bash
PEMS_USERNAME='your-name' PEMS_PASSWORD='your-password' pems-data auth
```

## Download by region and time

```bash
pems-data fetch \
  --district 7 \
  --start 2026-07-01 \
  --end 2026-07-03 \
  --bbox=-118.70,33.70,-117.60,34.40 \
  --output data/los-angeles
```

Other selectors can be combined:

```bash
pems-data fetch \
  --district 4 \
  --start 2026-06-01T08:00 \
  --end 2026-06-07T18:00 \
  --freeway 80 \
  --direction E \
  --lane-type ML \
  --output data/i80-east
```

## Prepare the GE-GAN source dataset

This project includes a research profile for the Caltrans District 7 period and detector header published with GE-GAN:

```bash
pems-data profiles

pems-data fetch \
  --profile ge-gan-d7-2014 \
  --output data/ge-gan-d7-2014
```

In addition to the normalized dataset and manifest, this profile creates:

```text
ge_gan/combine_E_workday_n0.csv
ge_gan/combine_E_weekend_n0.csv
```

These matrices follow the public GE-GAN repository's station-as-columns format. The profile prepares the same PeMS source period and published detector set; it is not, by itself, a claim of bit-for-bit paper reproduction. See [the reproducibility notes](docs/ge-gan.md).

## Research origin

This downloader grew from the data acquisition work behind:

> Dongwei Xu, Chenchen Wei, Peng Peng, Qi Xuan, and Haifeng Guo.  
> **GE-GAN: A novel deep learning framework for road traffic state estimation.**  
> *Transportation Research Part C: Emerging Technologies*, 117, 102635, 2020.  
> [Paper](https://doi.org/10.1016/j.trc.2020.102635) · [Open-source code](https://github.com/wcc961129/GE-GAN)

If this downloader helps your data collection, cite this software using [CITATION.cff](CITATION.cff). If you use the GE-GAN research profile, model, data organization, or method, please also cite the paper.

```bibtex
@article{xu2020gegan,
  title={GE-GAN: A novel deep learning framework for road traffic state estimation},
  author={Xu, Dongwei and Wei, Chenchen and Peng, Peng and Xuan, Qi and Guo, Haifeng},
  journal={Transportation Research Part C: Emerging Technologies},
  volume={117},
  pages={102635},
  year={2020},
  doi={10.1016/j.trc.2020.102635}
}
```

## Output

- `filtered/station_5min.csv.gz`: normalized station observations.
- `manifest.json`: filters, station IDs, source files, metadata files, and row counts.
- `metadata/`: Station Metadata used for spatial selection.
- `raw/`: District day files when `--keep-raw` is used.
- `ge_gan/`: compatibility matrices when a GE-GAN profile is selected.

Naive input times are interpreted as `America/Los_Angeles`, including daylight saving time. A date-only end value includes the full day.

## Scope

Version 0.1 focuses on `station_5min`, the format most frequently used in traffic forecasting and state-estimation research. Hourly, daily, incident, truck, and vehicle-classification datasets require their own file planners and schemas.

## Contributing

Bug reports and pull requests are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before contributing. Do not include PeMS credentials, browser state, or downloaded Caltrans data in an issue or pull request.

## Disclaimer

This is an independent research utility and is not affiliated with, endorsed by, or operated by Caltrans. Users are responsible for complying with PeMS terms and applicable data policies.

