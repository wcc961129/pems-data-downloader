# Caltrans PeMS 数据下载器

[![CI](https://github.com/wcc961129/pems-data-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/wcc961129/pems-data-downloader/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue)](pyproject.toml)
[![uv](https://img.shields.io/badge/environment-uv-6f42c1)](https://docs.astral.sh/uv/)
[![License: MIT](https://img.shields.io/badge/code-MIT-yellow.svg)](LICENSE)
[![GE-GAN 论文](https://img.shields.io/badge/DOI-10.1016%2Fj.trc.2020.102635-blue)](https://doi.org/10.1016/j.trc.2020.102635)

按照区域和时间范围下载经过认证的 Caltrans PeMS 检测器数据，并直接生成研究用观测表、检测器位置、近似邻接关系，以及可选的 Caltrans 官方州道路网几何。

[English](README.md) · [完整用户指南](docs/user-guide.zh-CN.md) · [数据格式](docs/data-format.md) · [真实格式样例](examples/sample-output/README.md)

![District 7 Route 105 检测器与 Caltrans SHN 路网](docs/station-hour-support/network-map.jpg)

上图由本项目使用 2026-07-27 的 PeMS 检测器 metadata 和下载时获取的 Caltrans SHN 几何生成。绿色点是 PeMS 检测器，灰线是官方道路几何；交互版本位于每次下载结果的 `network/map.html`。

## 当前支持的数据粒度

本项目不是只能下载 5 分钟数据。它直接使用 PeMS 官方的两类 Station 归档：

| 源数据 | CLI 参数 | PeMS 归档方式 | 研究表中的流量列 | 已验证的最新样例 |
|---|---|---|---|---|
| Station 5-Minute | `--granularity 5min`，默认值 | 每 District、每天一个归档 | `flow_veh_5min` | District 7，2026-07-27 |
| Station Hour | `--granularity hour` | 每 District、每月一个归档 | `flow_veh_hour` | District 7，2026-06 |

“最新样例”是 2026-07-29 实际查询 PeMS Clearinghouse 后得到的结果，不代表 PeMS 永远以相同延迟发布。小时数据是官方小时归档，并非本项目把 5 分钟数据简单相加。

PeMS Clearinghouse 还列出了 Station Day、AADT、Link、Census、FasTrak、Re-ID 和事故等数据，但当前版本尚未实现这些解析器。README 只把已经下载并测试过的类型列为“支持”。

## 30 秒判断数据格式

5 分钟观测：

```csv
timestamp,station_id,speed_mph,flow_veh_5min,occupancy_fraction,observed_percent,latitude,longitude,freeway,direction,lane_type
2026-07-27T00:00:00-07:00,760063,69.4,159,.0296,0,33.929816,-118.373757,105,E,ML
```

小时观测：

```csv
timestamp,station_id,speed_mph,flow_veh_hour,occupancy_fraction,observed_percent,latitude,longitude,freeway,direction,lane_type
2026-06-01T00:00:00-07:00,760063,68.8,1560,.0246,0,33.929816,-118.373757,105,E,ML
```

检测器静态属性：

```csv
station_id,freeway,direction,district,county,city,state_postmile,absolute_postmile,latitude,longitude,length,lane_type,lanes,name
760063,105,E,7,37,44000,R1.8,1.8,33.929816,-118.373757,.6,ML,3,IMPERIAL 1
```

近似图边：

```csv
source_station_id,target_station_id,distance_miles,method
760063,767838,0.700000,same_route_direction_lane_type_postmile_order
```

GeoJSON 点、manifest 和更多一行样例见[真实格式样例](examples/sample-output/README.md)。`observed_percent=0` 表示该值没有直接观测点支撑，可能由 PeMS 插补；建模时不要丢弃这一质量字段。

## Windows、macOS 和 Linux

`uv sync`、`uv run playwright install chromium` 和
`uv run pems-data ...` 的命令名及参数在三个平台上相同；主要区别是
安装方式、Shell 的多行符号和系统时区数据。

| 平台 | 当前状态 | 推荐终端 | 注意事项 |
|---|---|---|---|
| macOS | 已实际运行验证 | Terminal + Zsh/Bash | README 中的 Bash 命令可直接使用 |
| Linux | Ubuntu CI 覆盖 Python 3.10–3.12 | Bash | 无桌面服务器执行 `auth` 时需要可显示浏览器的环境 |
| Windows | Windows CI 已配置 Python 3.12 | PowerShell | `tzdata` 由 uv 条件依赖安装；`0600` 权限语义与 Unix 不同 |

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/wcc961129/pems-data-downloader.git
cd pems-data-downloader
uv sync --locked
uv run playwright install chromium
uv run pems-data auth
```

Linux 缺少 Chromium 系统库时，可改用：

```bash
uv run playwright install --with-deps chromium
```

### Windows PowerShell

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
git clone https://github.com/wcc961129/pems-data-downloader.git
Set-Location pems-data-downloader
uv sync --locked
uv run playwright install chromium
uv run pems-data auth
```

代码使用 `America/Los_Angeles` IANA 时区。Windows 通常不提供系统
IANA 时区数据库，因此 `uv sync --locked` 会通过条件依赖自动安装
`tzdata`。CI 配置同时覆盖 Ubuntu、macOS 和 Windows。

README 其余示例使用 Bash/Zsh 的反斜杠 `\` 换行。PowerShell 应使用反引号
`` ` ``：

```powershell
uv run pems-data fetch `
  --granularity 5min `
  --district 7 `
  --start 2026-07-27T00:00 `
  --end 2026-07-27T00:10 `
  --station-id 760063,760074,760080,767838,773656 `
  --with-road-network `
  --output data\i105-5min
```

也可以在任何平台把完整命令写在一行。`--granularity`、时间、District
和区域筛选参数不因操作系统而变化。uv 安装方式见
[uv 官方安装说明](https://docs.astral.sh/uv/getting-started/installation/)，
浏览器依赖见
[Playwright 官方说明](https://playwright.dev/python/docs/browsers)。

## 使用 uv 快速开始

完成上方对应平台的安装和认证后，先检查环境并查看实际可用数据：

```bash
uv run pems-data doctor
uv run pems-data latest --district 7
uv run pems-data stations \
  --district 7 \
  --date 2026-07-27 \
  --freeway 105 \
  --direction E \
  --lane-type ML \
  --limit 5
```

`latest` 避免猜测可用日期，`stations` 避免猜测站点 ID。完整中文流程见
[用户指南](docs/user-guide.zh-CN.md)。

下载 5 个检测器的 5 分钟数据，并同时获取官方道路几何：

```bash
uv run pems-data fetch \
  --granularity 5min \
  --district 7 \
  --start 2026-07-27T00:00 \
  --end 2026-07-27T00:10 \
  --station-id 760063,760074,760080,767838,773656 \
  --with-road-network \
  --output data/i105-5min
```

下载同一组检测器的官方小时数据：

```bash
uv run pems-data fetch \
  --granularity hour \
  --district 7 \
  --start 2026-06-01T00:00 \
  --end 2026-06-01T02:00 \
  --station-id 760063,760074,760080,767838,773656 \
  --output data/i105-hour
```

主要输出结构：

```text
data/i105-5min/
├── manifest.json
├── filtered/
│   └── station_5min.csv.gz
├── processed/
│   ├── observations.csv.gz
│   ├── stations.csv
│   ├── detectors.geojson
│   └── edges.csv
└── network/
    ├── caltrans_shn.geojson
    └── map.html
```

小时任务会把 `filtered/station_5min.csv.gz` 改为 `filtered/station_hour.csv.gz`，其他路径保持一致。边界框、道路、方向、车道类型、County 和 GE-GAN 配置见[完整用户指南](docs/user-guide.zh-CN.md)。

## 下载前要知道

- 一个很短的 5 分钟请求仍需传输对应的完整日归档；小时请求仍需传输完整月归档。
- 默认删除大体积源归档；只有确实需要复查原始数据时才使用 `--keep-raw`。
- 先用少量站点和短时间范围验证字段，再扩展下载，可以更早发现站点、时区和质量问题。
- 下载前会先完成 metadata 预检；零站点不会开始下载交通归档，零观测默认报错，可用 `--allow-empty` 显式放行。
- `edges.csv` 是按相同道路、方向、车道类型和 postmile 生成的透明近似关系，不是 Caltrans 官方拓扑。
- `manifest.json` 记录实际源文件、metadata、行数、粒度和生成产物，建议与实验结果一起保存。

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

该配置使用 5 分钟数据准备论文公开的 PeMS 时间范围与检测器集合，但不宣称自动复现论文全部预处理细节。请阅读 [GE-GAN 可复现性说明](docs/ge-gan.md)。

## 研究用途声明

本软件面向科研和教学，不适用于交通控制、安全关键决策或实时事故响应。代码采用 MIT 许可证；下载的 PeMS 数据和 Caltrans GIS 数据仍受原始来源条款与署名要求约束。详见 [DISCLAIMER.md](DISCLAIMER.md)。

## 文档

- [完整用户指南](docs/user-guide.zh-CN.md)
- [English user guide](docs/user-guide.md)
- [数据格式、单位和质量字段](docs/data-format.md)
- [官方道路几何与近似图边界](docs/road-network.md)
- [小时级支持实现记录](docs/station-hour-support/implementation-report.md)
- [易用性优化实现记录](docs/usability-optimization/implementation-report.md)
- [项目架构](docs/architecture.md)
- [使用 uv 进行开发](docs/development.md)
- [交通预测基准模型仓库方案](docs/model-repository-roadmap.md)
- [参与贡献](CONTRIBUTING.md)
