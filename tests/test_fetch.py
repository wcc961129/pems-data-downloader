import asyncio
import gzip
from datetime import date
from pathlib import Path

import pytest

from pems_data.fetch import execute
from pems_data.models import FetchPlan, Region, RemoteFile
from pems_data.planner import parse_datetime


class FakeCatalog:
    station_file_calls = 0
    metadata_source: Path
    station_source: Path

    def __init__(self, state_path: Path):
        self.state_path = state_path

    async def metadata_file(self, district: int, target: date) -> RemoteFile:
        return RemoteFile(
            name="d07_text_meta_2026_07_17.txt",
            url="metadata",
            district=district,
            dataset="meta",
            file_date=date(2026, 7, 17),
        )

    async def station_files(
        self,
        district: int,
        days: list[date],
        granularity: str,
    ) -> list[RemoteFile]:
        type(self).station_file_calls += 1
        return [
            RemoteFile(
                name="d07_text_station_5min_2026_07_27.txt.gz",
                url="station",
                district=district,
                dataset="station_5min",
                file_date=date(2026, 7, 27),
            )
        ]


class FakeDownloader:
    def __init__(self, state_path: Path):
        self.state_path = state_path

    def download(self, url: str, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        source = (
            FakeCatalog.metadata_source
            if url == "metadata"
            else FakeCatalog.station_source
        )
        destination.write_bytes(source.read_bytes())
        return destination


def _metadata(path: Path) -> None:
    path.write_text(
        "1001\t105\tE\t7\t37\t44000\tR1.8\t1.8\t33.93\t-118.37\t.6\tML\t3\tA\n",
        encoding="utf-8",
    )


def _station_source(path: Path, timestamp: str) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as stream:
        stream.write(
            f"{timestamp},1001,7,105,E,ML,.6,12,100,120,.04,65.5\n"
        )


def _plan(tmp_path: Path, region: Region, allow_empty: bool = False) -> FetchPlan:
    return FetchPlan(
        districts=(7,),
        start=parse_datetime("2026-07-27T00:00"),
        end=parse_datetime("2026-07-27T00:10"),
        region=region,
        output=tmp_path / "output",
        keep_raw=False,
        allow_empty=allow_empty,
    )


def test_explicit_station_id_is_intersected_with_metadata_filters(
    tmp_path: Path,
    monkeypatch,
):
    metadata = tmp_path / "metadata.txt"
    source = tmp_path / "station.txt.gz"
    _metadata(metadata)
    _station_source(source, "07/27/2026 00:00:00")
    FakeCatalog.metadata_source = metadata
    FakeCatalog.station_source = source
    FakeCatalog.station_file_calls = 0
    monkeypatch.setattr("pems_data.fetch.CatalogBrowser", FakeCatalog)
    monkeypatch.setattr("pems_data.fetch.ResumableDownloader", FakeDownloader)
    plan = _plan(
        tmp_path,
        Region(
            station_ids=frozenset({1001}),
            directions=frozenset({"W"}),
        ),
    )
    with pytest.raises(ValueError, match="Preflight selected zero"):
        asyncio.run(execute(plan, tmp_path / "state.json"))
    assert FakeCatalog.station_file_calls == 0


def test_zero_observations_fail_unless_explicitly_allowed(
    tmp_path: Path,
    monkeypatch,
):
    metadata = tmp_path / "metadata.txt"
    source = tmp_path / "station.txt.gz"
    _metadata(metadata)
    _station_source(source, "07/27/2026 01:00:00")
    FakeCatalog.metadata_source = metadata
    FakeCatalog.station_source = source
    monkeypatch.setattr("pems_data.fetch.CatalogBrowser", FakeCatalog)
    monkeypatch.setattr("pems_data.fetch.ResumableDownloader", FakeDownloader)
    plan = _plan(tmp_path, Region(station_ids=frozenset({1001})))
    with pytest.raises(ValueError, match="zero observations"):
        asyncio.run(execute(plan, tmp_path / "state.json"))
    assert not list((plan.output / "raw").glob("*.gz"))

    allowed = _plan(
        tmp_path / "allowed",
        Region(station_ids=frozenset({1001})),
        allow_empty=True,
    )
    manifest = asyncio.run(execute(allowed, tmp_path / "state.json"))
    assert manifest.exists()
