#!/usr/bin/env python3
"""Refresh the README API count badge from the provider table size."""

from __future__ import annotations

from pathlib import Path
import re


README_PATH = Path(__file__).resolve().parents[1] / "README.md"

BADGE_PATTERN = re.compile(
    r"^(!\[API count\]\(https://img\.shields\.io/badge/API_Count-)(\d+)(-blue\?style=for-the-badge\))$"
)
ROW_PATTERN = re.compile(r"^\|\s*\[[^\]]+\]\(https?://[^)]+\)")


def update_badge() -> bool:
    lines = README_PATH.read_text(encoding="utf-8").splitlines()
    provider_count = sum(1 for line in lines if ROW_PATTERN.match(line))

    changed = False
    for index, line in enumerate(lines):
        match = BADGE_PATTERN.match(line)
        if not match:
            continue

        updated_line = f"{match.group(1)}{provider_count}{match.group(3)}"
        if updated_line != line:
            lines[index] = updated_line
            changed = True
        break

    if changed:
        README_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return changed


def main() -> None:
    changed = update_badge()
    print("README updated" if changed else "No changes needed")


if __name__ == "__main__":
    main()