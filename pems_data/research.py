import csv
import gzip
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


PACIFIC = ZoneInfo("America/Los_Angeles")
OBSERVATION_COLUMNS = (
    "timestamp",
    "station_id",
    "speed_mph",
    "flow_veh_5min",
    "occupancy_fraction",
    "observed_percent",
    "latitude",
    "longitude",
    "freeway",
    "direction",
    "lane_type",
)
STATION_COLUMNS = (
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
)


def _float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def export_research_dataset(
    source: Path,
    stations: dict[int, dict[str, str]],
    destination: Path,
) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    observations_path = destination / "observations.csv.gz"
    stations_path = destination / "stations.csv"
    detectors_path = destination / "detectors.geojson"
    edges_path = destination / "edges.csv"
    observation_rows = 0
    with gzip.open(source, "rt", encoding="utf-8", newline="") as input_stream:
        reader = csv.DictReader(input_stream)
        with gzip.open(
            observations_path,
            "wt",
            encoding="utf-8",
            newline="",
        ) as output_stream:
            writer = csv.DictWriter(output_stream, fieldnames=OBSERVATION_COLUMNS)
            writer.writeheader()
            for row in reader:
                station_id = int(row["station"])
                station = stations.get(station_id)
                if station is None:
                    continue
                timestamp = datetime.strptime(
                    row["timestamp"],
                    "%m/%d/%Y %H:%M:%S",
                ).replace(tzinfo=PACIFIC)
                writer.writerow(
                    {
                        "timestamp": timestamp.isoformat(),
                        "station_id": station_id,
                        "speed_mph": row["average_speed"],
                        "flow_veh_5min": row["total_flow"],
                        "occupancy_fraction": row["average_occupancy"],
                        "observed_percent": row["percent_observed"],
                        "latitude": station["latitude"],
                        "longitude": station["longitude"],
                        "freeway": station["freeway"],
                        "direction": station["direction"],
                        "lane_type": station["lane_type"],
                    }
                )
                observation_rows += 1
    ordered_stations = [stations[key] for key in sorted(stations)]
    with stations_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=STATION_COLUMNS)
        writer.writeheader()
        for station in ordered_stations:
            writer.writerow({key: station.get(key, "") for key in STATION_COLUMNS})
    features = []
    for station in ordered_stations:
        longitude = _float(station.get("longitude", ""))
        latitude = _float(station.get("latitude", ""))
        if longitude is None or latitude is None:
            continue
        properties = {key: station.get(key, "") for key in STATION_COLUMNS}
        properties["direction_arrow"] = {
            "N": "↑",
            "S": "↓",
            "E": "→",
            "W": "←",
        }.get(station.get("direction", ""), "•")
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude],
                },
                "properties": properties,
            }
        )
    detectors_path.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": features,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    grouped = defaultdict(list)
    for station in ordered_stations:
        absolute_postmile = _float(station.get("absolute_postmile", ""))
        if absolute_postmile is None:
            continue
        key = (
            station.get("freeway", ""),
            station.get("direction", ""),
            station.get("lane_type", ""),
        )
        grouped[key].append((absolute_postmile, int(station["station_id"])))
    edge_rows = []
    for items in grouped.values():
        items.sort()
        for left, right in zip(items, items[1:]):
            edge_rows.append(
                {
                    "source_station_id": left[1],
                    "target_station_id": right[1],
                    "distance_miles": f"{right[0] - left[0]:.6f}",
                    "method": "same_route_direction_lane_type_postmile_order",
                }
            )
    with edges_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=(
                "source_station_id",
                "target_station_id",
                "distance_miles",
                "method",
            ),
        )
        writer.writeheader()
        writer.writerows(edge_rows)
    return {
        "processed_observation_rows": observation_rows,
        "processed_station_rows": len(ordered_stations),
        "detector_feature_count": len(features),
        "approximate_edge_count": len(edge_rows),
        "processed_observations": str(observations_path),
        "processed_stations": str(stations_path),
        "detectors_geojson": str(detectors_path),
        "approximate_edges": str(edges_path),
    }
