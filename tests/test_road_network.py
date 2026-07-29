import json
from pathlib import Path

from pems_data.road_network import download_official_road_network, render_network_map


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[-118.37, 33.93], [-118.35, 33.94]],
                    },
                    "properties": {"Route": 105},
                }
            ],
        }


def test_download_and_render_official_network(tmp_path: Path, monkeypatch):
    captured = {}

    def fake_get(url, params, timeout):
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("pems_data.road_network.requests.get", fake_get)
    stations = {
        1001: {
            "station_id": "1001",
            "freeway": "105",
            "latitude": "33.93",
            "longitude": "-118.36",
        }
    }
    road_path = tmp_path / "network" / "caltrans_shn.geojson"
    result = download_official_road_network(stations, road_path)
    assert result["official_road_feature_count"] == 1
    assert captured["params"]["where"] == "Route IN (105)"
    detectors_path = tmp_path / "detectors.geojson"
    detectors_path.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-118.36, 33.93],
                        },
                        "properties": {
                            "station_id": "1001",
                            "freeway": "105",
                            "direction": "E",
                            "direction_arrow": "→",
                            "name": "A",
                            "absolute_postmile": "2.5",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    map_path = render_network_map(
        detectors_path,
        road_path,
        tmp_path / "network" / "map.html",
    )
    html = map_path.read_text(encoding="utf-8")
    assert "Station ${escapeHtml(p.station_id)}" in html
    assert "Caltrans SHN geometry" in html
