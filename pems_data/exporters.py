import csv
import gzip
from collections import OrderedDict
from datetime import datetime
from pathlib import Path


def export_ge_gan_matrices(
    source: Path,
    destination: Path,
    station_ids: tuple[int, ...],
) -> dict[str, int]:
    destination.mkdir(parents=True, exist_ok=True)
    station_set = set(station_ids)
    by_timestamp: OrderedDict[str, dict[int, str]] = OrderedDict()
    with gzip.open(source, "rt", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            station_id = int(row["station"])
            if station_id not in station_set:
                continue
            by_timestamp.setdefault(row["timestamp"], {})[station_id] = row["total_flow"]

    workday = destination / "combine_E_workday_n0.csv"
    weekend = destination / "combine_E_weekend_n0.csv"
    writers = {}
    handles = {}
    try:
        for label, path in (("workday", workday), ("weekend", weekend)):
            handle = path.open("w", encoding="utf-8", newline="")
            handles[label] = handle
            writer = csv.writer(handle)
            writer.writerow(station_ids)
            writers[label] = writer
        counts = {"workday_rows": 0, "weekend_rows": 0, "incomplete_rows": 0}
        for timestamp, values in by_timestamp.items():
            if len(values) != len(station_ids):
                counts["incomplete_rows"] += 1
                continue
            moment = datetime.strptime(timestamp, "%m/%d/%Y %H:%M:%S")
            label = "weekend" if moment.weekday() >= 5 else "workday"
            writers[label].writerow(values[station_id] for station_id in station_ids)
            counts[f"{label}_rows"] += 1
    finally:
        for handle in handles.values():
            handle.close()
    return counts

