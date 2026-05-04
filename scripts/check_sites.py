#!/usr/bin/env python3
"""Check provider sites and refresh the README status table."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


README_PATH = Path(__file__).resolve().parents[1] / "README.md"
TIMEOUT_SECONDS = 30
MAX_WORKERS = 8


ROW_PATTERN = re.compile(
    r"^(?P<prefix>\|\s*\[[^\]]+\]\((?P<url>https?://[^)]+)\)\s*\|.*?\|\s*)"
    r"(?P<tested>[✅❌])(?P<tested_spacing>\s*\|\s*)"
    r"(?P<last_checked>\d{4}-\d{2}-\d{2})(?P<date_spacing>\s*\|\s*\[Status\]\([^)]+\)\s*\|\s*)$"
)


def check_url(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status_code = response.getcode() or 0
            return "✅" if status_code < 400 else "❌"
    except (HTTPError, URLError, TimeoutError, ValueError):
        return "❌"
    except Exception:
        return "❌"


def update_readme() -> bool:
    today = datetime.now(timezone.utc).date().isoformat()
    content = README_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()

    indexed_rows: list[tuple[int, str, re.Match[str]]] = []
    for index, line in enumerate(lines):
        match = ROW_PATTERN.match(line)
        if match:
            indexed_rows.append((index, match.group("url"), match))

    results: dict[int, str] = {}
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, max(1, len(indexed_rows)))) as executor:
        future_by_index = {
            executor.submit(check_url, url): index for index, url, _ in indexed_rows
        }
        for future in as_completed(future_by_index):
            index = future_by_index[future]
            results[index] = future.result()

    changed = False
    for index, _, match in indexed_rows:
        tested = results.get(index, "❌")
        updated_line = (
            f"{match.group('prefix')}{tested}{match.group('tested_spacing')}"
            f"{today}{match.group('date_spacing')}"
        )
        if updated_line != lines[index]:
            lines[index] = updated_line
            changed = True

    if changed:
        README_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return changed


def main() -> None:
    changed = update_readme()
    print("README updated" if changed else "No changes needed")


if __name__ == "__main__":
    main()