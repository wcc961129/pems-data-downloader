# Related project: wcc961129/transdim

## 项目定位

[wcc961129/transdim](https://github.com/wcc961129/transdim) 是公开的
`xinychen/transdim` fork，保留了上游作者和论文引用，项目定位是交通数据
缺失值插补与预测。仓库采用 MIT 代码许可证，并以 Jupyter Notebook 为主要
实现形式。

本项目与 `transdim` 解决不同阶段的问题：

| 项目 | 主要职责 | 典型输出或输入 |
|---|---|---|
| `pems-data-downloader` | 从认证后的 PeMS Clearinghouse 获取指定时间和区域的数据 | 长表 CSV、站点 metadata、GeoJSON、图边、manifest |
| `transdim` | 提供或索引多城市数据，并进行矩阵/张量插补与预测实验 | MAT、NPY、CSV、pickle、矩阵/张量和 Notebook |

因此，`transdim` 是本项目的相关数据与下游建模资源，不是 PeMS 官方下载器的
替代品。

## 数据目录

截至 2026-07-29，`wcc961129/transdim` 的 `datasets/` 目录公开列出了：

### 交通与移动数据

- `Birmingham-data-set`：停车数据；
- `California-data-set`：California/PeMS 大规模交通数据；
- `Guangzhou-data-set`：城市道路速度；
- `Hangzhou-data-set`：地铁客流；
- `London-data-set`：Uber Movement 道路速度；
- `NGSIM-data-set`：车辆轨迹相关数据；
- `NYC-data-set`：New York City taxi；
- `PeMS-data-set`：PeMS 交通速度；
- `Portland-data-set`：Portland-Vancouver 交通数据；
- `Seattle-data-set`：高速公路环形检测器速度。

### 其他时空序列

- `Energy-data-set`：电力负荷/用电量；
- `Temperature-data-set`：温度时空序列。

仓库的数据说明还链接了 PeMS-BAY、Seattle Loop、Guangzhou、UTD19、
London Movement 和 Portland PORTAL 等公开来源。

目录名称不等于完整原始数据一定被仓库重新分发。一些大型数据只提供处理代码、
派生文件或原始提供方的下载入口。使用前应阅读
[`datasets/README.md`](https://github.com/wcc961129/transdim/blob/master/datasets/README.md)
及对应子目录。

## 模型与 Notebook

`transdim` 包含多种矩阵和张量方法，例如：

- BPMF、TRMF、BTRMF、BTMF；
- BGCP、BATF、BTTF；
- HaLRTC、LRTC-TNN；
- 面向缺失数据插补和多步预测的实验 Notebook。

这些资源适合用于比较不同缺失模式、插补方法和预测方法，也可以作为本项目
下载结果的下游建模参考。

## 从本项目衔接到 transdim

推荐流程：

1. 使用本项目通过 `latest` 和 `stations` 确定 PeMS 可用时间与站点；
2. 使用 `fetch` 下载并保存 `manifest.json`；
3. 以 `processed/observations.csv.gz` 为来源创建站点-时间矩阵或
   站点-日期-时段张量；
4. 为缺失值建立独立布尔掩码；
5. 根据目标 Notebook 的输入形状和单位进行转换；
6. 将来源 manifest、站点顺序、时间范围和转换脚本与实验结果一起保存。

5 分钟数据可以按每天 288 个时段构造张量，小时数据可以按每天 24 个时段
构造张量，但夏令时切换日可能不是标准的 288 或 24 个本地时间点。不要在未
定义 DST 处理规则的情况下直接 reshape。

## 缺失值与零值

部分 `transdim` 示例通过数值 `0` 表示缺失位置。PeMS 数据中的零流量可能是
真实观测，`observed_percent=0` 的非零数值也可能是 PeMS 插补结果。因此跨项目
使用时应：

- 保留 `observed_percent`；
- 明确区分真实零、PeMS 插补值和本地构造的缺失值；
- 使用独立 missing mask，而不是无条件执行 `value == 0`；
- 在论文或报告中记录缺失场景和转换规则。

## 许可与引用边界

- `pems-data-downloader` 和 `transdim` 的代码许可证不自动覆盖数据本身；
- PeMS、Uber Movement、NYC TLC、UCI、Zenodo、PORTAL、NGSIM 等数据仍受
  各自条款、署名和再分发规则约束；
- 使用 `transdim` Notebook 时，应引用其 README 中对应论文和原始数据来源；
- 使用本项目下载的数据时，应保留 PeMS 来源、下载时间和 manifest。

## English summary

[`wcc961129/transdim`](https://github.com/wcc961129/transdim) complements
this downloader with multi-city transportation datasets, source links, and
matrix/tensor imputation and forecasting notebooks. Use this project to
acquire current authenticated PeMS observations and reproducibility metadata;
use `transdim` for benchmark-oriented data preparation and downstream
modeling. Dataset availability, formats, licenses, and missing-value semantics
must be checked per source. In particular, preserve an explicit missing mask
instead of assuming that every numerical zero is missing.
