# Caltrans PeMS 数据下载器

[![CI](https://github.com/wcc961129/pems-data-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/wcc961129/pems-data-downloader/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue)](pyproject.toml)
[![uv](https://img.shields.io/badge/environment-uv-6f42c1)](https://docs.astral.sh/uv/)
[![License: MIT](https://img.shields.io/badge/code-MIT-yellow.svg)](LICENSE)
[![GE-GAN 论文](https://img.shields.io/badge/DOI-10.1016%2Fj.trc.2020.102635-blue)](https://doi.org/10.1016/j.trc.2020.102635)

按照区域和时间范围下载经过认证的 Caltrans PeMS 检测器数据，并直接生成速度、流量、占有率、检测器位置、研究型邻接关系，以及可选的 Caltrans 官方州道路网几何。

[English](README.md) · [完整用户指南](docs/user-guide.md) · [数据格式](docs/data-format.md) · [路网说明](docs/road-network.md) · [少量真实示例](examples/sample-output/README.md)

## 下载后可以得到什么

- 精确到时间范围和区域的 Station 5-Minute 数据。
- 带明确单位、坐标和方向的 `processed/observations.csv.gz`。
- 检测器表 `stations.csv`、点位图 `detectors.geojson`。
- 按相同道路、方向、车道类型和 postmile 顺序生成的研究型 `edges.csv`。
- 可选的 Caltrans 官方 SHN 道路几何 `caltrans_shn.geojson`。
- 标记检测器位置和方向的交互地图 `map.html`。
- 完整下载清单及 GE-GAN 内置研究配置。

## 使用 uv 快速开始

先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)，克隆仓库后执行：

```bash
uv sync --locked
uv run playwright install chromium
uv run pems-data auth
```

在弹出的浏览器中登录 PeMS。登录会话仅保存在本机 `.pems/storage-state.json`，权限为 `0600`，不会提交到 Git。

下载 5 个检测器的少量数据，并同时获取官方道路几何：

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2014-05-01T00:00 \
  --end 2014-05-01T00:15 \
  --station-id 760063,760074,760080,767838,773656 \
  --with-road-network \
  --output data/i105-east
```

主要研究数据位于：

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

经纬度框、道路、方向、车道类型、County 和 GE-GAN 配置的完整示例见[用户指南](docs/user-guide.md)。

## GE-GAN 论文与代码

本项目源自以下研究的数据获取工作：

> Dongwei Xu, Chenchen Wei, Peng Peng, Qi Xuan, Haifeng Guo.  
> **GE-GAN: A novel deep learning framework for road traffic state estimation.**  
> *Transportation Research Part C: Emerging Technologies*, 117, 102635, 2020.

[论文 DOI](https://doi.org/10.1016/j.trc.2020.102635) · [配套开源代码](https://github.com/wcc961129/GE-GAN)

```bash
uv run pems-data fetch \
  --profile ge-gan-d7-2014 \
  --output data/ge-gan-d7-2014
```

该配置准备论文公开的 PeMS 时间范围与检测器集合，但不宣称自动复现论文全部预处理细节。请阅读 [GE-GAN 可复现性说明](docs/ge-gan.md)。

## 研究用途声明

本软件面向科研和教学，不适用于交通控制、安全关键决策或实时事故响应。代码采用 MIT 许可证；下载的 PeMS 数据和 Caltrans GIS 数据仍受原始来源条款与署名要求约束。详见 [DISCLAIMER.md](DISCLAIMER.md)。

## 文档

- [完整用户指南](docs/user-guide.md)
- [数据格式与单位](docs/data-format.md)
- [官方道路几何与近似图边界](docs/road-network.md)
- [项目架构](docs/architecture.md)
- [使用 uv 进行开发](docs/development.md)
- [交通预测基准模型仓库方案](docs/model-repository-roadmap.md)
- [参与贡献](CONTRIBUTING.md)

