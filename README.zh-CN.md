# Caltrans PeMS 数据下载器

按区域和时间范围获取 Caltrans PeMS 交通检测器数据，避免逐站点、逐周手工点击。

[English](README.md) · [GE-GAN 研究配置](docs/ge-gan.md)

## 主要能力

- 经度纬度框、站点 ID、高速公路、方向、车道类型和 County 筛选。
- 使用 `America/Los_Angeles` 处理 PST/PDT。
- 登录后发现真实 Clearinghouse 下载链接。
- `.part` 文件、断点续传和原始 District 文件缓存。
- 输出压缩 CSV 与包含完整来源信息的 Manifest。

PeMS 要求申请免费账号。本项目不会绕过认证、分享账号或镜像 Caltrans 数据。

## 安装与授权

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
playwright install chromium
pems-data auth
```

会话只保存在本地 `.pems/storage-state.json`，文件权限为 `0600`，不会提交到 Git。

## 区域下载

```bash
pems-data fetch \
  --district 7 \
  --start 2026-07-01 \
  --end 2026-07-03 \
  --bbox=-118.70,33.70,-117.60,34.40 \
  --output data/los-angeles
```

## GE-GAN 数据配置

项目内置了 GE-GAN 论文所用 District 7 时间范围与公开检测器表头：

```bash
pems-data fetch \
  --profile ge-gan-d7-2014 \
  --output data/ge-gan-d7-2014
```

该命令会额外生成与 GE-GAN 开源仓库一致的宽表文件：

- `ge_gan/combine_E_workday_n0.csv`
- `ge_gan/combine_E_weekend_n0.csv`

这代表同源数据准备，不等同于自动完成论文全部复现实验。详细边界见 [docs/ge-gan.md](docs/ge-gan.md)。

## 论文与代码

本项目源自以下研究的数据获取工作：

> Dongwei Xu, Chenchen Wei, Peng Peng, Qi Xuan, Haifeng Guo.  
> **GE-GAN: A novel deep learning framework for road traffic state estimation.**  
> *Transportation Research Part C: Emerging Technologies*, 117, 102635, 2020.

[论文 DOI](https://doi.org/10.1016/j.trc.2020.102635) · [配套开源代码](https://github.com/wcc961129/GE-GAN)

如果工具帮助了你的数据收集，请引用本项目的 `CITATION.cff`；如果使用了 GE-GAN 配置、数据组织或方法，请同时引用论文。

