#!/usr/bin/env python3
"""Sort the provider table rows in README alphabetically by provider name."""

from __future__ import annotations

from pathlib import Path
import re


README_PATH = Path(__file__).resolve().parents[1] / "README.md"

ROW_PATTERN = re.compile(
    r"^\|\s*\[(?P<name>[^\]]+)\]\(https?://[^)]+\)\s*\|\s*\[More info\]\(config/PROVIDERS\.md#[^\)]+\)\s*\|$"
)

SECTION_HEADER = "| Name"
SECTION_FOOTER_PATTERN = re.compile(r"^\| --")


def extract_rows(lines: list[str]) -> tuple[int, int, list[str], list[str]]:
    """Find table bounds, return (start, end, matchable_rows, unmatched_rows)."""
    start = end = -1
    matchable: list[str] = []
    unmatched: list[str] = []
    for i, line in enumerate(lines):
        if line.startswith(SECTION_HEADER):
            start = i + 2  # skip header + separator
        if start != -1 and end == -1:
            if line.startswith("|"):
                if ROW_PATTERN.match(line):
                    matchable.append(line)
                elif SECTION_FOOTER_PATTERN.match(line):
                    pass  # skip separator row
                elif line.startswith("| Name"):
                    pass  # skip stray header row
                else:
                    unmatched.append(line)
            else:
                end = i
    if end == -1:
        end = len(lines)
    return start, end, matchable, unmatched


def sort_table() -> bool:
    content = README_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()

    start, end, matchable, unmatched = extract_rows(lines)
    if not matchable:
        print("No table rows found")
        return False

    sorted_rows = sorted(matchable, key=lambda r: r.strip().lower())

    if sorted_rows == matchable:
        return False

    new_lines = list(lines[:start])
    new_lines.extend(sorted_rows)
    new_lines.extend(unmatched)
    new_lines.extend(lines[end:])

    README_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return True


def main() -> None:
    changed = sort_table()
    print("README sorted" if changed else "No changes needed")


if __name__ == "__main__":
    main()
