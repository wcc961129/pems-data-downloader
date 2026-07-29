import csv
import gzip
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


PACIFIC = ZoneInfo("America/Los_Angeles")
OUTPUT_HEADER = (
    "timestamp",
    "station",
    "district",
    "freeway",
    "direction",
    "lane_type",
    "station_length",
    "samples",
    "percent_observed",
    "total_flow",
    "average_occupancy",
    "average_speed",
    "lane_values",
)


def filter_station_files(
    sources: list[Path],
    destination: Path,
    station_ids: set[int],
    start: datetime,
    end: datetime,
) -> dict[str, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows_read = 0
    rows_written = 0
    with gzip.open(destination, "wt", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(OUTPUT_HEADER)
        for source_path in sources:
            with gzip.open(source_path, "rt", encoding="utf-8", newline="") as source:
                for row in csv.reader(source):
                    rows_read += 1
                    if len(row) < 12:
                        continue
                    try:
                        station_id = int(row[1])
                        timestamp = datetime.strptime(row[0], "%m/%d/%Y %H:%M:%S").replace(
                            tzinfo=PACIFIC
                        )
                    except ValueError:
                        continue
                    if station_id not in station_ids or not (start <= timestamp <= end):
                        continue
                    writer.writerow(row[:12] + ["|".join(row[12:])])
                    rows_written += 1
    return {"rows_read": rows_read, "rows_written": rows_written}

