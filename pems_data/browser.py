import asyncio
import os
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from .models import RemoteFile
from .planner import daily_filename, parse_remote_file


BASE_URL = "https://pems.dot.ca.gov/"
CLEARINGHOUSE_URL = f"{BASE_URL}?dnode=Clearinghouse"


class BrowserUnavailableError(RuntimeError):
    pass


def _playwright():
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise BrowserUnavailableError(
            "Install the project and Chromium before use: pip install -e . && playwright install chromium"
        ) from exc
    return async_playwright


async def authorize(state_path: Path, timeout_ms: int = 180_000) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    async with _playwright()() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(CLEARINGHOUSE_URL, wait_until="domcontentloaded")
        username = os.getenv("PEMS_USERNAME")
        password = os.getenv("PEMS_PASSWORD")
        if username and password and await page.locator("#username").count():
            await page.fill("#username", username)
            await page.fill("#password", password)
            await page.click("input[name='login']")
        print("Complete PeMS login in the opened browser. Waiting for the Clearinghouse page...")
        await page.wait_for_selector("#type", timeout=timeout_ms)
        await context.storage_state(path=str(state_path))
        os.chmod(state_path, 0o600)
        await browser.close()


class CatalogBrowser:
    def __init__(self, state_path: Path, timeout_ms: int = 60_000):
        self.state_path = state_path
        self.timeout_ms = timeout_ms

    async def _open(self):
        manager = _playwright()()
        playwright = await manager.__aenter__()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=str(self.state_path))
        page = await context.new_page()
        page.set_default_timeout(self.timeout_ms)
        await page.goto(CLEARINGHOUSE_URL, wait_until="domcontentloaded")
        if await page.locator("#type").count() != 1:
            await browser.close()
            await manager.__aexit__(None, None, None)
            raise RuntimeError("PeMS session is missing or expired; run `pems-data auth` again")
        return manager, browser, page

    async def station_files(
        self,
        district: int,
        days: list[date],
    ) -> list[RemoteFile]:
        manager, browser, page = await self._open()
        try:
            expected_by_year: dict[int, set[str]] = {}
            for day in days:
                expected_by_year.setdefault(day.year, set()).add(
                    daily_filename(district, day)
                )
            found: dict[str, RemoteFile] = {}
            for year, expected in expected_by_year.items():
                payload = await self._catalog_payload(
                    page,
                    district,
                    year,
                    "station_5min",
                )
                for entries in payload.values():
                    if not isinstance(entries, list):
                        continue
                    for item in entries:
                        name = item.get("file_name", "")
                        if name not in expected:
                            continue
                        parsed = parse_remote_file(
                            name,
                            urljoin(BASE_URL, item.get("url", "")),
                        )
                        if parsed:
                            found[parsed.name] = parsed
            missing = sorted(
                name
                for names in expected_by_year.values()
                for name in names
                if name not in found
            )
            if missing:
                raise FileNotFoundError(
                    "PeMS did not list expected files: " + ", ".join(missing[:10])
                )
            return sorted(found.values(), key=lambda item: item.file_date)
        finally:
            await browser.close()
            await manager.__aexit__(None, None, None)

    async def metadata_file(self, district: int, target: date) -> RemoteFile:
        manager, browser, page = await self._open()
        try:
            for offset in range(24):
                cursor_year = target.year - offset
                payload = await self._catalog_payload(
                    page,
                    district,
                    cursor_year,
                    "meta",
                )
                candidates = []
                for item in payload.values():
                    text_file = item.get("format", {}).get("text", {})
                    parsed = parse_remote_file(
                        text_file.get("file_name", ""),
                        urljoin(BASE_URL, text_file.get("url", "")),
                    )
                    if parsed:
                        candidates.append(parsed)
                before = [item for item in candidates if item.file_date <= target]
                if before:
                    return max(before, key=lambda item: item.file_date)
            raise FileNotFoundError(
                f"No station metadata on or before {target} listed for district {district}"
            )
        finally:
            await browser.close()
            await manager.__aexit__(None, None, None)

    async def _catalog_payload(
        self,
        page: Any,
        district: int,
        year: int,
        dataset: str,
    ) -> dict[str, Any]:
        response = await page.request.get(
            BASE_URL,
            params={
                "srq": "clearinghouse",
                "district_id": str(district),
                "geotag": "",
                "yy": str(year),
                "type": "metadata" if dataset == "meta" else dataset,
                "returnformat": "text",
            },
            timeout=self.timeout_ms,
        )
        if not response.ok:
            raise RuntimeError(
                f"PeMS catalog request failed with HTTP {response.status}: {response.url}"
            )
        payload = await response.json()
        data = payload.get("data")
        if not isinstance(data, dict):
            raise RuntimeError(
                f"PeMS catalog returned an unexpected payload for {dataset}, "
                f"district {district}, year {year}"
            )
        return data


def run(coroutine):
    return asyncio.run(coroutine)
