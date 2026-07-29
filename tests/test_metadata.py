from pathlib import Path

from pems_data.metadata import select_station_ids
from pems_data.models import Region


def test_select_station_ids_by_bbox_and_freeway(tmp_path: Path):
    metadata = tmp_path / "meta.txt"
    metadata.write_text(
        "1001\t101\tN\t7\t37\tLos Angeles\t1\t1\t34.10\t-118.30\t0.5\tML\t4\tA\n"
        "1002\t5\tS\t7\t37\tLos Angeles\t2\t2\t34.20\t-118.40\t0.5\tML\t4\tB\n"
        "1003\t101\tN\t7\t37\tLos Angeles\t3\t3\t36.00\t-120.00\t0.5\tML\t4\tC\n",
        encoding="utf-8",
    )
    region = Region(
        bbox=(-118.5, 34.0, -118.0, 34.5),
        freeways=frozenset({101}),
    )
    assert select_station_ids(metadata, region) == {1001}


def test_header_row_is_ignored(tmp_path: Path):
    metadata = tmp_path / "meta.csv"
    metadata.write_text(
        "ID,Freeway,Direction,District,County,City,State PM,Abs PM,Latitude,Longitude\n"
        "2001,80,E,4,1,Oakland,1,1,37.8,-122.2\n",
        encoding="utf-8",
    )
    assert select_station_ids(metadata, Region(freeways=frozenset({80}))) == {2001}

