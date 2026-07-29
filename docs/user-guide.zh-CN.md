# 用户指南

[English user guide](user-guide.md)

## 1. 准备工作

PeMS 要求使用经过批准的账户。下载前请先在
[Caltrans PeMS 网站](https://pems.dot.ca.gov/)完成注册。

按照[根目录 README](../README.zh-CN.md#windowsmacos-和-linux)完成对应平台的
安装，然后检查本地环境：

```bash
uv run pems-data doctor
```

该命令检查 Python、California 时区、Playwright Chromium、PeMS 登录会话
以及会话文件权限。

## 2. 登录认证

```bash
uv run pems-data auth
```

在弹出的浏览器中登录 PeMS。浏览器状态保存在
`.pems/storage-state.json`，其中包含会话 Cookie，禁止提交或分享。

Bash/Zsh 可以临时提供账号环境变量：

```bash
PEMS_USERNAME='your-name' \
PEMS_PASSWORD='your-password' \
uv run pems-data auth
```

PowerShell 写法：

```powershell
$Env:PEMS_USERNAME="your-name"
$Env:PEMS_PASSWORD="your-password"
uv run pems-data auth
Remove-Item Env:PEMS_USERNAME, Env:PEMS_PASSWORD
```

会话过期时重新执行 `auth`。认证会启动可见浏览器，因此需要能够显示桌面的
运行环境。

## 3. 发现可用数据

不要猜测 PeMS 最新日期，直接查询认证后的 Clearinghouse：

```bash
uv run pems-data latest --district 7
```

示例输出：

```csv
district,granularity,latest_period,source_file
7,5min,2026-07-27,d07_text_station_5min_2026_07_27.txt.gz
7,hour,2026-06,d07_text_station_hour_2026_06.txt.gz
```

下载交通归档前，先从 metadata 查找站点：

```bash
uv run pems-data stations \
  --district 7 \
  --date 2026-07-27 \
  --freeway 105 \
  --direction E \
  --lane-type ML \
  --limit 5
```

输出包含站点 ID、道路、方向、车道类型、postmile、坐标和名称。
`stations` 支持与 `fetch` 相同的边界框、站点、道路、方向、车道类型和
County 筛选参数。

## 4. 下载观测数据

未带时区的时间统一解释为 `America/Los_Angeles`，包括夏令时。开始和结束
时间都包含在结果内；只写日期的结束值会包含当天全部时间。

### 5 分钟数据

```bash
uv run pems-data fetch \
  --granularity 5min \
  --district 7 \
  --start 2026-07-27T00:00 \
  --end 2026-07-27T00:10 \
  --station-id 760063,760074,760080,767838,773656 \
  --output data/i105-5min
```

### 小时数据

```bash
uv run pems-data fetch \
  --granularity hour \
  --district 7 \
  --start 2026-06-01T00:00 \
  --end 2026-06-01T02:00 \
  --station-id 760063,760074,760080,767838,773656 \
  --output data/i105-hour
```

默认粒度是 `5min`。小时值直接来自 PeMS Station Hour 官方归档。

### 经纬度边界框

顺序为 `west,south,east,north`：

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2026-07-27T00:00 \
  --end 2026-07-27T00:10 \
  --bbox=-118.38,33.92,-118.34,33.95 \
  --output data/by-bbox
```

### 道路、方向和车道类型

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2026-07-27T00:00 \
  --end 2026-07-27T00:10 \
  --freeway 105 \
  --direction E \
  --lane-type ML \
  --output data/i105-east-mainline
```

### County

County 使用 PeMS metadata 中的数字 FIPS 代码：

```bash
uv run pems-data fetch \
  --district 4 \
  --start 2025-06-01T00:00 \
  --end 2025-06-01T01:00 \
  --county 1 \
  --lane-type ML \
  --output data/alameda-mainline
```

多个筛选条件按逻辑 AND 组合。一个参数可以使用逗号分隔多个值，也可以重复
传入。交通归档下载前会完成 metadata 预检；零匹配站点会立即终止。

`fetch` 必须显式指定 District，避免意外触发全州归档下载。确实需要多个
District 时，可以重复 `--district` 或使用逗号分隔多个值。

零观测行默认视为错误。确实允许空数据集的自动化流程可以显式增加
`--allow-empty`。

## 5. 获取官方道路几何

增加 `--with-road-network`：

```bash
uv run pems-data fetch \
  --district 7 \
  --start 2026-07-27T00:00 \
  --end 2026-07-27T00:10 \
  --station-id 760063,760074,760080,767838,773656 \
  --with-road-network \
  --output data/i105-network
```

生成：

- `network/caltrans_shn.geojson`：官方 State Highway Network 线几何；
- `network/map.html`：检测器和道路交互地图。

地图从公共 CDN 加载 Leaflet 和 OpenStreetMap 资源，打开时需要联网。

## 6. 理解下载成本

Station 5-Minute 按 District 和日期归档。即使只请求 10 分钟，也需要传输
对应的完整日归档。

Station Hour 按 District 和月份归档。即使只请求 2 小时，也需要传输对应的
完整月归档。

下载器会：

1. 验证站点 metadata；
2. 显示站点和源归档预检计划；
3. 串行下载并显示进度；
4. 流式读取，不把完整归档一次载入内存；
5. 保留精确站点和包含首尾的时间范围；
6. 默认删除原始归档，`--keep-raw` 时保留；
7. 输出观测、站点和图边数量。

PeMS Clearinghouse 提醒不要并发自动下载，因此项目使用串行下载。

## 7. 检查输出

主要数据表是 `processed/observations.csv.gz`。不安装 pandas 也可以查看前
两行：

```bash
uv run python -c "import gzip,itertools; print(''.join(itertools.islice(gzip.open('data/i105-5min/processed/observations.csv.gz','rt'),2)))"
```

PowerShell 可以原样执行该命令。字段、单位、检测器 metadata、图边和
manifest 见[数据格式说明](data-format.md)。

## 8. GE-GAN 配置

```bash
uv run pems-data profiles

uv run pems-data fetch \
  --profile ge-gan-d7-2014 \
  --output data/ge-gan-d7-2014
```

配置会额外生成以站点为列的 GE-GAN 兼容矩阵。声明复现结果前请阅读
[GE-GAN 说明](ge-gan.md)。

## 9. 恢复与排错

- 深入排查前先执行 `uv run pems-data doctor`。
- 中断文件使用 `.part` 后缀，服务器支持时通过 HTTP Range 续传。
- 已完成的文件会直接复用。
- PeMS 返回 HTML 而非数据时，会被识别为会话过期。
- 缺少预期归档通常表示请求时间尚未发布，请检查 `latest`。
- 零站点通常表示 District 或 metadata 筛选不匹配，请检查 `stations`。
- 零观测通常表示时间不可用或站点在该时段不活跃。
- 仅在调试解析器或必须保留官方归档时使用 `--keep-raw`。
- 禁止公开 `.pems/storage-state.json`、账号密码或完整源归档。
