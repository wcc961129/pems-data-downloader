import asyncio
from datetime import date
from pathlib import Path

from pems_data.browser import CatalogBrowser


class FakeBrowser:
    async def close(self):
        return None


class FakeManager:
    async def __aexit__(self, exc_type, exc, traceback):
        return None


def test_latest_station_files_discovers_each_granularity(monkeypatch):
    catalog = CatalogBrowser(Path("state.json"))

    async def fake_open():
        return FakeManager(), FakeBrowser(), object()

    async def fake_payload(page, district, year, dataset):
        if year != 2026:
            return {}
        names = {
            "station_5min": "d07_text_station_5min_2026_07_27.txt.gz",
            "station_hour": "d07_text_station_hour_2026_06.txt.gz",
        }
        return {
            "files": [
                {
                    "file_name": names[dataset],
                    "url": f"/{dataset}",
                }
            ]
        }

    monkeypatch.setattr(catalog, "_open", fake_open)
    monkeypatch.setattr(catalog, "_catalog_payload", fake_payload)
    found = asyncio.run(
        catalog.latest_station_files(
            7,
            ("5min", "hour"),
            2026,
        )
    )
    assert found["5min"].file_date == date(2026, 7, 27)
    assert found["hour"].file_date == date(2026, 6, 1)
