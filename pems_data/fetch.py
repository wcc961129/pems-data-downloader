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
    remote_files: list[RemoteFile] = []
    days = expected_days(plan.start, plan.end)
    selected_by_district: dict[int, set[int]] = {}

    for district in plan.districts:
        metadata_remote = await catalog.metadata_file(district, plan.end.date())
        metadata_path = transfer.download(
            metadata_remote.url,
            plan.output / "metadata" / metadata_remote.name,
        )
        metadata_files.append(metadata_path)
        district_ids = select_station_ids(metadata_path, plan.region)
        if district_ids:
            selected_by_district[district] = district_ids

    selected_ids = (
        set().union(*selected_by_district.values())
        if selected_by_district
        else set()
    )
    if not selected_ids:
        raise ValueError(
            "Preflight selected zero PeMS stations; verify District, station IDs, "
            "freeway, direction, lane type, county, and bounding box"
        )
    if plan.region.station_ids and not plan.region.has_non_id_filters:
        missing_ids = sorted(plan.region.station_ids - selected_ids)
        if missing_ids:
            raise ValueError(
                "Requested station IDs are missing from the applicable metadata: "
                + ", ".join(str(item) for item in missing_ids[:10])
            )

    station_records = load_station_records(metadata_files, selected_ids)
    missing_metadata = sorted(selected_ids - set(station_records))
    if missing_metadata:
        raise ValueError(
            "Selected PeMS stations are missing from the applicable metadata: "
            + ", ".join(str(item) for item in missing_metadata[:10])
        )

    for district in selected_by_district:
        station_remotes = await catalog.station_files(
            district,
            days,
            plan.granularity,
        )
        remote_files.extend(station_remotes)
    print(
        f"Preflight: {len(selected_ids)} stations across "
        f"{len(selected_by_district)} Districts; {len(remote_files)} source archives"
    )
    for remote in remote_files:
        raw_files.append(
            transfer.download(remote.url, plan.output / "raw" / remote.name)
        )

    source_dataset = (
        "station_5min" if plan.granularity == "5min" else "station_hour"
    )
    filtered_path = plan.output / "filtered" / f"{source_dataset}.csv.gz"
    counts = filter_station_files(
        raw_files,
        filtered_path,
        selected_ids,
        plan.start,
        plan.end,
    )
    if counts["rows_written"] == 0 and not plan.allow_empty:
        if not plan.keep_raw:
            for path in raw_files:
                path.unlink(missing_ok=True)
        raise ValueError(
            "PeMS source contained zero observations for the selected stations "
            "and time range; verify data availability or use --allow-empty"
        )
    processed = export_research_dataset(
        filtered_path,
        station_records,
        plan.output / "processed",
        plan.granularity,
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
        "granularity": plan.granularity,
        "source_dataset": source_dataset,
        "allow_empty": plan.allow_empty,
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
    print(
        f"Output: {counts['rows_written']} observations, "
        f"{len(selected_ids)} stations, "
        f"{processed['approximate_edge_count']} approximate edges"
    )
    return manifest_path
