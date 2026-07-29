import json
import os
import time
from pathlib import Path

import requests


class SessionExpiredError(RuntimeError):
    pass


def _format_bytes(value: int) -> str:
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if amount < 1024 or unit == "GiB":
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{amount:.1f} GiB"


class ResumableDownloader:
    def __init__(self, state_path: Path, timeout: int = 120):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "pems-data/0.1"
        self.timeout = timeout
        state = json.loads(state_path.read_text(encoding="utf-8"))
        for cookie in state.get("cookies", []):
            self.session.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain"),
                path=cookie.get("path", "/"),
            )

    def download(self, url: str, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.stat().st_size > 0:
            print(
                f"Reusing {destination.name} "
                f"({_format_bytes(destination.stat().st_size)})"
            )
            return destination
        partial = destination.with_suffix(destination.suffix + ".part")
        offset = partial.stat().st_size if partial.exists() else 0
        headers = {"Range": f"bytes={offset}-"} if offset else {}
        with self.session.get(
            url.replace("http://", "https://"),
            headers=headers,
            stream=True,
            timeout=self.timeout,
            allow_redirects=True,
        ) as response:
            if offset and response.status_code == 200:
                offset = 0
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" in content_type:
                raise SessionExpiredError("PeMS returned HTML instead of a data file")
            mode = "ab" if offset and response.status_code == 206 else "wb"
            content_length = int(response.headers.get("Content-Length", 0))
            total = offset + content_length if content_length else 0
            downloaded = offset
            started = time.monotonic()
            last_update = started
            size_label = _format_bytes(total) if total else "unknown size"
            print(f"Downloading {destination.name} ({size_label})")
            with partial.open(mode) as target:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        target.write(chunk)
                        downloaded += len(chunk)
                        now = time.monotonic()
                        if now - last_update >= 1:
                            elapsed = max(now - started, 0.001)
                            speed = _format_bytes(
                                max(downloaded - offset, 0) / elapsed
                            )
                            if total:
                                percent = downloaded / total * 100
                                progress = (
                                    f"{percent:5.1f}% "
                                    f"{_format_bytes(downloaded)}/{_format_bytes(total)}"
                                )
                            else:
                                progress = _format_bytes(downloaded)
                            print(
                                f"\r  {progress} at {speed}/s",
                                end="",
                                flush=True,
                            )
                            last_update = now
                target.flush()
                os.fsync(target.fileno())
            elapsed = max(time.monotonic() - started, 0.001)
            speed = _format_bytes(max(downloaded - offset, 0) / elapsed)
            print(
                f"\rDownloaded {destination.name}: "
                f"{_format_bytes(downloaded)} at {speed}/s"
            )
        partial.replace(destination)
        return destination
