# Detector locations and road network

Three outputs serve different purposes and must not be conflated.

## PeMS detector points

PeMS Station Metadata supplies detector ID, latitude, longitude, route, direction, station type, and postmile. The downloader selects the metadata snapshot effective on or before the requested traffic-data date.

`processed/detectors.geojson` therefore represents the recorded detector positions and attributes for the chosen PeMS snapshot.

## Official Caltrans road geometry

With `--with-road-network`, the downloader queries:

```text
Caltrans CHHighway/SHN_Lines/FeatureServer/0
```

The service provides official State Highway Network polyline geometry with route, District, County, direction, postmile interval, alignment code and route type. The query is restricted to routes and a padded bounding box around the selected detectors.

Source:

- [SHN Lines FeatureServer](https://caltrans-gis.dot.ca.gov/arcgis/rest/services/CHHighway/SHN_Lines/FeatureServer/0)

The downloaded `network/caltrans_shn.geojson` preserves the source URL, retrieval time and query bounding box.

## Approximate detector adjacency

The SHN geometry is authoritative road linework, but it is not a ready-made detector graph. PeMS metadata does not directly state every upstream/downstream detector relationship, interchange movement, ramp connection or lane-level topology.

`processed/edges.csv` is therefore labeled approximate. It orders selected detectors by absolute postmile within the same freeway, direction and lane type. It is suitable as a transparent baseline, but researchers should validate it for corridors with:

- route splits or merges;
- independent alignments;
- postmile resets or exceptions;
- ramps and connectors;
- missing or inactive detectors;
- detectors located near interchange boundaries.

## Interactive map

`network/map.html` overlays:

- gray official SHN polylines;
- colored PeMS detector points;
- direction arrows and detector metadata.

Opening the map requires internet access for Leaflet and OpenStreetMap tile assets. The detector and SHN GeoJSON data themselves remain embedded in the file.

![Route 105 detector and SHN map](station-hour-support/network-map.jpg)

This static preview was rendered from the verified District 7 sample dated
2026-07-27. The generated `map.html` remains the preferred artifact for
zooming, panning, and opening detector popups.

## Temporal mismatch

PeMS metadata is selected for the traffic-data date. The public SHN service may represent a newer road-network extraction. The manifest records the SHN retrieval source, but Caltrans does not expose historical SHN geometry for every PeMS observation date through this workflow. Historical studies must disclose this possible temporal mismatch.
