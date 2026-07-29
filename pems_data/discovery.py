from datetime import date
from pathlib import Path

from .browser import CatalogBrowser
from .http import ResumableDownloader
from .metadata import load_station_records, select_station_ids
from .models import Region, RemoteFile


async def discover_latest(
    state_path: Path,
    districts: tuple[int, ...],
    granularities: tuple[str, ...],
    target_year: int,
) -> list[RemoteFile]:
    catalog = CatalogBrowser(state_path)
    files = []
    for district in districts:
        found = await catalog.latest_station_files(
            district,
            granularities,
            target_year,
        )
        files.extend(found.values())
    return sorted(
        files,
        key=lambda item: (item.district, item.dataset),
    )


async def discover_stations(
    state_path: Path,
    district: int,
    target: date,
    region: Region,
    limit: int,
) -> tuple[list[dict[str, str]], int, RemoteFile]:
    catalog = CatalogBrowser(state_path)
    metadata_remote = await catalog.metadata_file(district, target)
    metadata_path = ResumableDownloader(state_path).download(
        metadata_remote.url,
        state_path.parent / "metadata-cache" / metadata_remote.name,
    )
    selected_ids = select_station_ids(metadata_path, region)
    records = load_station_records([metadata_path], selected_ids)
    rows = [records[station_id] for station_id in sorted(records)]
    return rows[:limit], len(rows), metadata_remote
