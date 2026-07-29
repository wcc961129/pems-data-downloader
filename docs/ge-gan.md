# GE-GAN Research Profile

## Paper

Dongwei Xu, Chenchen Wei, Peng Peng, Qi Xuan, and Haifeng Guo, “GE-GAN: A novel deep learning framework for road traffic state estimation,” *Transportation Research Part C: Emerging Technologies*, vol. 117, article 102635, 2020.

- DOI: https://doi.org/10.1016/j.trc.2020.102635
- Code: https://github.com/wcc961129/GE-GAN

The paper uses Caltrans District 7 traffic volume data from May 1 through June 30, 2014, aggregated at five-minute intervals. The public GE-GAN data matrix contains 23 station columns.

## Download

```bash
pems-data auth
pems-data fetch --profile ge-gan-d7-2014 --output data/ge-gan-d7-2014
```

The built-in profile fixes:

- District: 7
- Time: 2014-05-01 00:00:00 through 2014-06-30 23:59:59 Pacific Time
- Station IDs: the 23-column header published in `GE_GAN/data/combine_E_workday_n0.csv`
- Measure: PeMS `Total Flow`

The exporter separates complete five-minute rows into weekday and weekend matrices. The first row contains station IDs, matching the public GE-GAN repository's orientation.

## Reproducibility boundary

This profile provides a transparent path from the PeMS Clearinghouse to matrices compatible with the public repository. It does not guarantee byte-identical historical files because PeMS metadata, reprocessing, imputation, and website behavior can change.

Complete model reproduction also depends on:

- the `pems_24_point.adjlist` graph;
- the preprocessing behavior in the GE-GAN code;
- the original TensorFlow and dependency environment;
- random seeds and training configuration.

The downloader skips an output timestamp if any of the 23 stations is absent. The manifest reports `incomplete_rows`; researchers should disclose how missing rows were treated.

## Citation

If you use only the downloader, cite the software. If you use this profile, the GE-GAN matrix organization, or the GE-GAN method, cite both the software and paper.

