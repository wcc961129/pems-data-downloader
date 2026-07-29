import json
from dataclasses import asdict
from pathlib import Path

from .browser import CatalogBrowser
from .exporters import export_ge_gan_matrices
from .filtering import filter_station_files
from .http import ResumableDownloader
from .metadata import select_station_ids
from .models import FetchPlan, RemoteFile
from .planner import expected_days
from .profiles import get_profile


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
