import csv
import gzip
import json
from pathlib import Path

from pems_data.research import export_research_dataset


def test_export_research_dataset_writes_ml_ready_outputs(tmp_path: Path):
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
        writer.writerow(
            [
                "05/01/2014 00:00:00",
                "1001",
                "7",
                "105",
                "E",
                "ML",
                ".5",
                "30",
                "100",
                "120",
                ".04",
                "65.5",
                "",
            ]
        )
    stations = {
        1001: {
            "station_id": "1001",
            "freeway": "105",
            "direction": "E",
            "district": "7",
            "county": "37",
            "city": "",
            "state_postmile": "R2.5",
            "absolute_postmile": "2.5",
            "latitude": "33.93",
            "longitude": "-118.36",
            "length": ".5",
            "lane_type": "ML",
            "lanes": "3",
            "name": "A",
        },
        1002: {
            "station_id": "1002",
            "freeway": "105",
            "direction": "E",
            "district": "7",
            "county": "37",
            "city": "",
            "state_postmile": "R3.0",
            "absolute_postmile": "3.0",
            "latitude": "33.94",
            "longitude": "-118.35",
            "length": ".5",
            "lane_type": "ML",
            "lanes": "3",
            "name": "B",
        },
    }
    result = export_research_dataset(source, stations, tmp_path / "processed")
    assert result["processed_observation_rows"] == 1
    assert result["processed_station_rows"] == 2
    assert result["detector_feature_count"] == 2
    assert result["approximate_edge_count"] == 1
    with gzip.open(
        tmp_path / "processed" / "observations.csv.gz",
        "rt",
        encoding="utf-8",
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["timestamp"] == "2014-05-01T00:00:00-07:00"
    assert rows[0]["speed_mph"] == "65.5"
    assert rows[0]["flow_veh_5min"] == "120"
    assert rows[0]["latitude"] == "33.93"
    detectors = json.loads(
        (tmp_path / "processed" / "detectors.geojson").read_text(encoding="utf-8")
    )
    assert detectors["features"][0]["geometry"]["type"] == "Point"
    with (tmp_path / "processed" / "edges.csv").open(encoding="utf-8") as stream:
        edges = list(csv.DictReader(stream))
    assert edges[0]["source_station_id"] == "1001"
    assert edges[0]["target_station_id"] == "1002"
    assert edges[0]["distance_miles"] == "0.500000"


def test_export_research_dataset_labels_hourly_flow_unit(tmp_path: Path):
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
        writer.writerow(
            [
                "06/01/2026 00:00:00",
                "1001",
                "7",
                "105",
                "E",
                "ML",
                ".5",
                "12",
                "100",
                "1440",
                ".04",
                "65.5",
                "",
            ]
        )
    stations = {
        1001: {
            "station_id": "1001",
            "freeway": "105",
            "direction": "E",
            "district": "7",
            "county": "37",
            "latitude": "33.93",
            "longitude": "-118.36",
            "lane_type": "ML",
        }
    }
    export_research_dataset(
        source,
        stations,
        tmp_path / "processed",
        granularity="hour",
    )
    with gzip.open(
        tmp_path / "processed" / "observations.csv.gz",
        "rt",
        encoding="utf-8",
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert "flow_veh_hour" in rows[0]
    assert "flow_veh_5min" not in rows[0]
    assert rows[0]["flow_veh_hour"] == "1440"
