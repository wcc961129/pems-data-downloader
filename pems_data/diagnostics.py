import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo


def diagnose_environment(
    state_path: Path,
) -> tuple[list[tuple[str, str, str]], bool]:
    checks: list[tuple[str, str, str]] = []
    checks.append(
        (
            "PASS",
            "Python",
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        )
    )
    try:
        ZoneInfo("America/Los_Angeles")
        checks.append(("PASS", "Timezone", "America/Los_Angeles available"))
    except Exception as exc:
        checks.append(("FAIL", "Timezone", str(exc)))
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            executable = Path(playwright.chromium.executable_path)
        if executable.exists():
            checks.append(("PASS", "Chromium", str(executable)))
        else:
            checks.append(
                (
                    "FAIL",
                    "Chromium",
                    "run `uv run playwright install chromium`",
                )
            )
    except Exception as exc:
        checks.append(("FAIL", "Playwright", str(exc)))
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        cookie_count = len(state.get("cookies", []))
        if cookie_count:
            checks.append(
                (
                    "PASS",
                    "PeMS session",
                    f"{cookie_count} cookies in {state_path}",
                )
            )
        else:
            checks.append(("FAIL", "PeMS session", f"no cookies in {state_path}"))
    except Exception:
        checks.append(
            (
                "FAIL",
                "PeMS session",
                f"run `uv run pems-data auth`; missing or invalid {state_path}",
            )
        )
    if os.name == "posix" and state_path.exists():
        mode = state_path.stat().st_mode & 0o777
        if mode == 0o600:
            checks.append(("PASS", "Session permissions", "0600"))
        else:
            checks.append(
                (
                    "WARN",
                    "Session permissions",
                    f"{mode:04o}; expected 0600",
                )
            )
    elif os.name == "nt":
        checks.append(
            (
                "WARN",
                "Session permissions",
                "verify the Windows ACL for the session file",
            )
        )
    failed = any(status == "FAIL" for status, _, _ in checks)
    return checks, failed
