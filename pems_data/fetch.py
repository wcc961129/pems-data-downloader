import json
from dataclasses import asdict
from pathlib import Path

from .browser import CatalogBrowser
from .exporters import export_ge_gan_matrices
from .filtering import filter_station_files
from .http import ResumableDownloader
from .metadata import load_station_records, select_station_ids
from .models import FetchPlan, RemoteFile
from .planner import expected_days
from .profiles import get_profile
from .research import export_research_dataset
from .road_network import download_official_road_network, render_network_map


async def execute(plan: FetchPlan, state_path: Path) -> Path:
    catalog = CatalogBrowser(state_path)
    transfer = ResumableDownloader(state_path)
    raw_files: list[Path] = []
    metadata_files: list[Path] = []
    selected_ids = set(plan.region.station_ids)
    remote_files: list[RemoteFile] = []
    days = expected_days(plan.start, plan.end)

    for district in plan.districts:
        metadata_remote = await catalog.metadata_file(district, plan.end.date())
        metadata_path = transfer.download(
            metadata_remote.url,
            plan.output / "metadata" / metadata_remote.name,
        )
        metadata_files.append(metadata_path)
        if plan.region.has_metadata_filters:
            selected_ids.update(select_station_ids(metadata_path, plan.region))
        station_remotes = await catalog.station_files(district, days)
        remote_files.extend(station_remotes)
        for remote in station_remotes:
            raw_files.append(
                transfer.download(remote.url, plan.output / "raw" / remote.name)
            )

    if not selected_ids:
        raise ValueError("Region filters selected zero PeMS stations")

    filtered_path = plan.output / "filtered" / "station_5min.csv.gz"
    counts = filter_station_files(
        raw_files,
        filtered_path,
        selected_ids,
        plan.start,
        plan.end,
    )
    station_records = load_station_records(metadata_files, selected_ids)
    missing_metadata = sorted(selected_ids - set(station_records))
    if missing_metadata:
        raise ValueError(
            "Selected PeMS stations are missing from the applicable metadata: "
            + ", ".join(str(item) for item in missing_metadata[:10])
        )
    processed = export_research_dataset(
        filtered_path,
        station_records,
        plan.output / "processed",
    )
    for key in (
        "processed_observations",
        "processed_stations",
        "detectors_geojson",
        "approximate_edges",
    ):
        processed[key] = str(Path(processed[key]).relative_to(plan.output))
    road_outputs = {}
    roads_path = None
    if plan.with_road_network:
        roads_path = plan.output / "network" / "caltrans_shn.geojson"
        road_outputs = download_official_road_network(station_records, roads_path)
        road_outputs["official_road_geojson"] = str(
            Path(road_outputs["official_road_geojson"]).relative_to(plan.output)
        )
    map_path = render_network_map(
        plan.output / "processed" / "detectors.geojson",
        roads_path,
        plan.output / "network" / "map.html",
    )
    road_outputs["network_map"] = str(map_path.relative_to(plan.output))
    profile_exports = {}
    if plan.profile:
        profile = get_profile(plan.profile)
        profile_exports = export_ge_gan_matrices(
            filtered_path,
            plan.output / "ge_gan",
            profile.station_ids,
        )
    manifest = {
        "districts": plan.districts,
        "start": plan.start.isoformat(),
        "end": plan.end.isoformat(),
        "research_profile": plan.profile,
        "region": {
            **asdict(plan.region),
            "station_ids": sorted(plan.region.station_ids),
            "freeways": sorted(plan.region.freeways),
            "directions": sorted(plan.region.directions),
            "lane_types": sorted(plan.region.lane_types),
            "counties": sorted(plan.region.counties),
        },
        "selected_station_count": len(selected_ids),
        "selected_station_ids": sorted(selected_ids),
        "source_files": [item.name for item in remote_files],
        "metadata_files": [item.name for item in metadata_files],
        **counts,
        **processed,
        **road_outputs,
        **profile_exports,
    }
    manifest_path = plan.output / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if not plan.keep_raw:
        for path in raw_files:
            path.unlink(missing_ok=True)
    return manifest_path
