import json
import os
from pathlib import Path

import requests


class SessionExpiredError(RuntimeError):
    pass


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
            with partial.open(mode) as target:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        target.write(chunk)
                target.flush()
                os.fsync(target.fileno())
        partial.replace(destination)
        return destination

