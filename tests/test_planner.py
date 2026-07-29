from datetime import date

import pytest

from pems_data.planner import daily_filename, expected_days, parse_datetime, parse_remote_file


def test_parse_daily_file():
    item = parse_remote_file(
        "d07_text_station_5min_2026_07_01.txt.gz",
        "https://pems.dot.ca.gov/?download=42&dnode=Clearinghouse",
    )
    assert item is not None
    assert item.district == 7
    assert item.file_date == date(2026, 7, 1)


def test_expected_days_is_inclusive():
    start = parse_datetime("2026-07-01T08:00")
    end = parse_datetime("2026-07-03T09:00")
    assert expected_days(start, end) == [
        date(2026, 7, 1),
        date(2026, 7, 2),
        date(2026, 7, 3),
    ]


def test_end_before_start_is_rejected():
    with pytest.raises(ValueError):
        expected_days(parse_datetime("2026-07-02"), parse_datetime("2026-07-01"))


def test_daily_filename_zero_pads_district():
    assert daily_filename(4, date(2026, 3, 3)) == (
        "d04_text_station_5min_2026_03_03.txt.gz"
    )

