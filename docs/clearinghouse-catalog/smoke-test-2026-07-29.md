# Clearinghouse smoke test — 2026-07-29

## Purpose

Validate the complete authenticated workflow against the live Caltrans PeMS 20.0.1 Clearinghouse after replacing legacy fixed-delay page scraping with the authenticated JSON catalog.

## Command

```bash
pems-data fetch \
  --district 7 \
  --start 2014-05-01T00:00 \
  --end 2014-05-01T00:10 \
  --station-id 767838 \
  --output data/smoke-d7-20140501
```

## Result

- Exit status: `0`
- Source catalog file: `d07_text_station_5min_2014_05_01.txt.gz`
- Metadata selected: `d07_text_meta_2014_04_29.txt`
- Input rows streamed: `1,332,864`
- Output observations: `3`
- Output time range: `05/01/2014 00:00:00` through `05/01/2014 00:10:00`
- Selected station: `767838`
- Filtered gzip size: `320 bytes`
- Manifest size: `550 bytes`
- Metadata size: `388,331 bytes`
- Raw files retained: `0`

## Integrity

```text
station_5min.csv.gz
45b020d79326b1adab307234cb379b462558ab9d336fae50244fb89443621d57

manifest.json
2ad929859b249a331432800548a87f406671cfca3e621b86dda586a7e8ae9e10
```

The authenticated catalog lookup, serial download, metadata date selection, streaming station/time filter, manifest creation, and default raw-file cleanup all completed successfully.
