# Architecture

The project separates volatile website behavior from stable local data processing.

```mermaid
flowchart LR
    A["One-time PeMS login"] --> B["Local browser state"]
    B --> C["Authenticated Clearinghouse JSON catalog"]
    C --> D["Authenticated resumable HTTP download"]
    D --> E["District raw files"]
    C --> F["Station Metadata"]
    F --> G["Spatial station selection"]
    E --> H["Streaming time/station filter"]
    G --> H
    H --> I["Source-preserving filtered CSV.GZ"]
    F --> J["Detector node table + GeoJSON"]
    I --> K["ML-ready observations"]
    J --> L["Postmile-neighbor research graph"]
    J --> M["Caltrans SHN FeatureServer"]
    M --> N["Official road GeoJSON + interactive map"]
    K --> O["Manifest"]
    L --> O
    N --> O
    O --> P["Optional GE-GAN exporter"]
```

## Modules

- `browser.py`: one-time browser login and authenticated JSON catalog discovery.
- `http.py`: authenticated transfer, `.part` files, HTTP Range, and HTML-response rejection.
- `planner.py`: Pacific-time parsing and Clearinghouse filename contracts.
- `metadata.py`: bounding-box and station-attribute selection.
- `filtering.py`: streaming long-format output.
- `research.py`: unit-labeled observations, detector metadata, GeoJSON, and approximate edges.
- `road_network.py`: official Caltrans SHN geometry and interactive map export.
- `profiles.py`: sourced, immutable research configurations.
- `exporters.py`: model- or paper-specific output adapters.

New PeMS dataset types should add a planner and schema rather than adding conditionals to the station-five-minute parser.
