import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


SHN_QUERY_URL = (
    "https://caltrans-gis.dot.ca.gov/arcgis/rest/services/"
    "CHHighway/SHN_Lines/FeatureServer/0/query"
)
SHN_LAYER_URL = (
    "https://caltrans-gis.dot.ca.gov/arcgis/rest/services/"
    "CHHighway/SHN_Lines/FeatureServer/0"
)


def _number(value: str, kind: type[int] | type[float]):
    try:
        return kind(value)
    except (TypeError, ValueError):
        return None


def download_official_road_network(
    stations: dict[int, dict[str, str]],
    destination: Path,
    timeout: int = 120,
) -> dict[str, Any]:
    coordinates = [
        (longitude, latitude)
        for station in stations.values()
        if (longitude := _number(station.get("longitude", ""), float)) is not None
        and (latitude := _number(station.get("latitude", ""), float)) is not None
    ]
    if not coordinates:
        raise ValueError("Selected PeMS stations do not contain usable coordinates")
    routes = sorted(
        {
            route
            for station in stations.values()
            if (route := _number(station.get("freeway", ""), int)) is not None
        }
    )
    west = min(item[0] for item in coordinates) - 0.02
    east = max(item[0] for item in coordinates) + 0.02
    south = min(item[1] for item in coordinates) - 0.02
    north = max(item[1] for item in coordinates) + 0.02
    where = "1=1"
    if routes:
        where = f"Route IN ({','.join(str(route) for route in routes)})"
    features = []
    offset = 0
    page_size = 2000
    while True:
        response = requests.get(
            SHN_QUERY_URL,
            params={
                "where": where,
                "geometry": f"{west},{south},{east},{north}",
                "geometryType": "esriGeometryEnvelope",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": (
                    "OBJECTID,Route,RouteS,District,County,Direction,"
                    "bPM,ePM,AlignCode,RouteType"
                ),
                "returnGeometry": "true",
                "outSR": "4326",
                "resultOffset": str(offset),
                "resultRecordCount": str(page_size),
                "f": "geojson",
            },
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if "error" in payload:
            raise RuntimeError(
                f"Caltrans SHN query failed: {payload['error'].get('message', 'unknown error')}"
            )
        page = payload.get("features", [])
        features.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "source": SHN_LAYER_URL,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "bbox": [west, south, east, north],
                "features": features,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "official_road_feature_count": len(features),
        "official_road_source": SHN_LAYER_URL,
        "official_road_geojson": str(destination),
    }


def render_network_map(
    detectors_path: Path,
    roads_path: Path | None,
    destination: Path,
) -> Path:
    detectors = json.loads(detectors_path.read_text(encoding="utf-8"))
    roads = (
        json.loads(roads_path.read_text(encoding="utf-8"))
        if roads_path and roads_path.exists()
        else {"type": "FeatureCollection", "features": []}
    )
    html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PeMS detector network</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
html,body,#map{height:100%;margin:0}
.legend{background:white;padding:8px 10px;border-radius:6px;box-shadow:0 1px 8px #0004;font:13px system-ui}
</style>
</head>
<body>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const detectors=__DETECTORS__;
const roads=__ROADS__;
const map=L.map("map");
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{
  maxZoom:19,
  attribution:"&copy; OpenStreetMap contributors"
}).addTo(map);
L.geoJSON(roads,{style:{color:"#64748b",weight:4,opacity:.75}}).addTo(map);
const colors={N:"#2563eb",S:"#dc2626",E:"#16a34a",W:"#9333ea"};
const escapeHtml=value=>String(value??"").replace(/[&<>"']/g,character=>({
  "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
})[character]);
const detectorLayer=L.geoJSON(detectors,{
  pointToLayer:(feature,latlng)=>L.circleMarker(latlng,{
    radius:7,
    color:"#fff",
    weight:2,
    fillColor:colors[feature.properties.direction]||"#111827",
    fillOpacity:1
  }),
  onEachFeature:(feature,layer)=>{
    const p=feature.properties;
    layer.bindPopup(`<b>${escapeHtml(p.direction_arrow)} Station ${escapeHtml(p.station_id)}</b><br>Route ${escapeHtml(p.freeway)} ${escapeHtml(p.direction)}<br>${escapeHtml(p.name)}<br>Postmile ${escapeHtml(p.absolute_postmile)}`);
  }
}).addTo(map);
const bounds=detectorLayer.getBounds();
if(bounds.isValid()){map.fitBounds(bounds.pad(.25))}
else{map.setView([37.2,-119.5],6)}
const legend=L.control({position:"bottomright"});
legend.onAdd=()=>{
  const div=L.DomUtil.create("div","legend");
  div.innerHTML="<b>PeMS detectors</b><br>↑ N &nbsp; ↓ S &nbsp; → E &nbsp; ← W<br>Gray: Caltrans SHN geometry";
  return div;
};
legend.addTo(map);
</script>
</body>
</html>
"""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        html.replace(
            "__DETECTORS__",
            json.dumps(detectors, ensure_ascii=False).replace("</", "<\\/"),
        ).replace(
            "__ROADS__",
            json.dumps(roads, ensure_ascii=False).replace("</", "<\\/"),
        ),
        encoding="utf-8",
    )
    return destination
