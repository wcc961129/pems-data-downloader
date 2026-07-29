import csv
import gzip
from pathlib import Path

from pems_data.filtering import filter_station_files
from pems_data.planner import parse_datetime


def test_filter_station_files_by_station_and_exact_time(tmp_path: Path):
    source = tmp_path / "d07.txt.gz"
    with gzip.open(source, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ["07/01/2026 08:00:00", "1001", "7", "101", "N", "ML", "0.5", "4", "100", "20", "0.1", "60"]
        )
        writer.writerow(
            ["07/01/2026 08:05:00", "1002", "7", "101", "N", "ML", "0.5", "4", "100", "20", "0.1", "60"]
        )
    output = tmp_path / "filtered.csv.gz"
    result = filter_station_files(
        [source],
        output,
        {1001},
        parse_datetime("2026-07-01T08:00"),
        parse_datetime("2026-07-01T08:05"),
    )
    with gzip.open(output, "rt", encoding="utf-8") as stream:
        rows = list(csv.reader(stream))
    assert result == {"rows_read": 2, "rows_written": 1}
    assert rows[1][1] == "1001"

