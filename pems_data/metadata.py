import csv
from pathlib import Path

from .models import Region


META_COLUMNS = (
    "station_id",
    "freeway",
    "direction",
    "district",
    "county",
    "city",
    "state_postmile",
    "absolute_postmile",
    "latitude",
    "longitude",
    "length",
    "lane_type",
    "lanes",
    "name",
    "user_id_1",
    "user_id_2",
    "user_id_3",
    "user_id_4",
)


def _number(value: str, kind: type[int] | type[float]):
    try:
        return kind(value)
    except (TypeError, ValueError):
        return None


def read_station_records(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        first = source.readline()
        source.seek(0)
        delimiter = "\t" if first.count("\t") >= first.count(",") else ","
        reader = csv.reader(source, delimiter=delimiter)
        for raw in reader:
            if not raw:
                continue
            row = dict(zip(META_COLUMNS, (value.strip() for value in raw)))
            station_id = _number(row.get("station_id", ""), int)
            if station_id is None:
                continue
            row["station_id"] = str(station_id)
            yield row


def select_station_ids(path: Path, region: Region) -> set[int]:
    selected: set[int] = set()
    for row in read_station_records(path):
        station_id = int(row["station_id"])
        if region.station_ids and station_id not in region.station_ids:
            continue
        if region.freeways and _number(row.get("freeway", ""), int) not in region.freeways:
            continue
        if region.directions and row.get("direction", "").upper() not in region.directions:
            continue
        if region.lane_types and row.get("lane_type", "").upper() not in region.lane_types:
            continue
        if region.counties and _number(row.get("county", ""), int) not in region.counties:
            continue
        if region.bbox:
            longitude = _number(row.get("longitude", ""), float)
            latitude = _number(row.get("latitude", ""), float)
            if longitude is None or latitude is None:
                continue
            west, south, east, north = region.bbox
            if not (west <= longitude <= east and south <= latitude <= north):
                continue
        selected.add(station_id)
    return selected


def load_station_records(
    paths: list[Path],
    station_ids: set[int],
) -> dict[int, dict[str, str]]:
    records = {}
    for path in paths:
        for row in read_station_records(path):
            station_id = int(row["station_id"])
            if station_id in station_ids:
                records[station_id] = row
    return records
