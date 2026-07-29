from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


@dataclass(frozen=True)
class RemoteFile:
    name: str
    url: str
    district: int
    dataset: str
    file_date: date


@dataclass(frozen=True)
class Region:
    station_ids: frozenset[int] = frozenset()
    bbox: tuple[float, float, float, float] | None = None
    freeways: frozenset[int] = frozenset()
    directions: frozenset[str] = frozenset()
    lane_types: frozenset[str] = frozenset()
    counties: frozenset[int] = frozenset()

    @property
    def has_metadata_filters(self) -> bool:
        return any(
            (
                self.bbox,
                self.freeways,
                self.directions,
                self.lane_types,
                self.counties,
            )
        )

    @property
    def has_non_id_filters(self) -> bool:
        return self.has_metadata_filters


@dataclass(frozen=True)
class FetchPlan:
    districts: tuple[int, ...]
    start: datetime
    end: datetime
    region: Region
    output: Path
    keep_raw: bool
    granularity: str = "5min"
    allow_empty: bool = False
    profile: str | None = None
    with_road_network: bool = False
