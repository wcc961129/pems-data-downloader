import csv
import gzip
from pathlib import Path

from pems_data.exporters import export_ge_gan_matrices


def test_export_ge_gan_matrices_splits_days_and_skips_incomplete(tmp_path: Path):
    source = tmp_path / "filtered.csv.gz"
    with gzip.open(source, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
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
            ]
        )
        writer.writerow(["05/02/2014 00:00:00", "1", "7", "5", "N", "ML", "", "", "", "10", "", "", ""])
        writer.writerow(["05/02/2014 00:00:00", "2", "7", "5", "N", "ML", "", "", "", "20", "", "", ""])
        writer.writerow(["05/03/2014 00:00:00", "1", "7", "5", "N", "ML", "", "", "", "30", "", "", ""])
        writer.writerow(["05/03/2014 00:00:00", "2", "7", "5", "N", "ML", "", "", "", "40", "", "", ""])
        writer.writerow(["05/04/2014 00:00:00", "1", "7", "5", "N", "ML", "", "", "", "50", "", "", ""])
    result = export_ge_gan_matrices(source, tmp_path / "out", (1, 2))
    assert result == {
        "workday_rows": 1,
        "weekend_rows": 1,
        "incomplete_rows": 1,
    }
    with (tmp_path / "out" / "combine_E_workday_n0.csv").open() as stream:
        assert list(csv.reader(stream)) == [["1", "2"], ["10", "20"]]

