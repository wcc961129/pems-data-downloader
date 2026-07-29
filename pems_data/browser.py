import asyncio
import os
import re
from datetime import date
from pathlib import Path
from typing import Any

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
            await page.select_option("#type", value="station_5min")
            await page.select_option("#district_id", value=str(district))
            await page.click("input[name='submit']")
            await page.wait_for_load_state("domcontentloaded")
            expected_by_month: dict[tuple[int, int], set[str]] = {}
            for day in days:
                expected_by_month.setdefault((day.year, day.month), set()).add(
                    daily_filename(district, day)
                )
            found: dict[str, RemoteFile] = {}
            for (year, month), expected in expected_by_month.items():
                await self._load_month(page, district, year, month, "station_5min")
                links = await self._download_links(page)
                for item in links:
                    if item["name"] not in expected:
                        continue
                    parsed = parse_remote_file(item["name"], item["url"])
                    if parsed:
                        found[parsed.name] = parsed
            missing = sorted(
                name for names in expected_by_month.values() for name in names if name not in found
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
            await page.select_option("#type", value="meta")
            await page.select_option("#district_id", value=str(district))
            await page.click("input[name='submit']")
            await page.wait_for_load_state("domcontentloaded")
            candidates = await self._metadata_candidates(page, district)
            cursor_year, cursor_month = target.year, target.month
            for _ in range(24):
                if candidates:
                    break
                await self._load_month(page, district, cursor_year, cursor_month, "meta")
                candidates = await self._metadata_candidates(page, district)
                cursor_month -= 1
                if cursor_month == 0:
                    cursor_year -= 1
                    cursor_month = 12
            if not candidates:
                raise FileNotFoundError(f"No station metadata listed for district {district}")
            before = [item for item in candidates if item.file_date <= target]
            return max(before or candidates, key=lambda item: item.file_date)
        finally:
            await browser.close()
            await manager.__aexit__(None, None, None)

    async def _metadata_candidates(self, page: Any, district: int) -> list[RemoteFile]:
        result = []
        for item in await self._download_links(page):
            parsed = parse_remote_file(item["name"], item["url"])
            if parsed and parsed.dataset == "meta" and parsed.district == district:
                result.append(parsed)
        return result

    async def _load_month(
        self,
        page: Any,
        district: int,
        year: int,
        month: int,
        dataset: str,
    ) -> None:
        await page.evaluate(
            """([district, year, dataset, monthIndex]) => {
                if (typeof processFiles !== 'function') {
                    throw new Error('PeMS processFiles function is unavailable');
                }
                const typeValue = dataset === 'meta' ? 'metadata' : dataset;
                if (processFiles.length >= 6) {
                    processFiles(String(district), '', year, typeValue, 'text', monthIndex);
                } else {
                    processFiles(String(district), year, typeValue, typeValue);
                }
            }""",
            [district, year, dataset, month - 1],
        )
        await page.wait_for_timeout(1200)

    async def _download_links(self, page: Any) -> list[dict[str, str]]:
        return await page.locator("a[href*='download=']").evaluate_all(
            """elements => elements.map(element => ({
                name: (element.textContent || '').trim(),
                url: element.href || ''
            }))"""
        )


def run(coroutine):
    return asyncio.run(coroutine)

