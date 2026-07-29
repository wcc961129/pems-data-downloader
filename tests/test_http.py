import json
from pathlib import Path

from pems_data.http import ResumableDownloader


class FakeResponse:
    status_code = 200
    headers = {
        "Content-Length": "6",
        "Content-Type": "application/gzip",
    }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return None

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size: int):
        yield b"abc"
        yield b"def"


class FakeSession:
    def get(self, url, headers, stream, timeout, allow_redirects):
        return FakeResponse()


def test_download_reports_progress_and_writes_file(
    tmp_path: Path,
    capsys,
):
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"cookies": []}), encoding="utf-8")
    downloader = ResumableDownloader(state)
    downloader.session = FakeSession()
    destination = tmp_path / "source.gz"
    result = downloader.download("https://example.test/source.gz", destination)
    assert result.read_bytes() == b"abcdef"
    output = capsys.readouterr().out
    assert "Downloading source.gz" in output
    assert "Downloaded source.gz" in output
