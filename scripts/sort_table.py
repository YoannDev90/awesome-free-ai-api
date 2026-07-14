#!/usr/bin/env python3
"""Sort the provider table rows in README alphabetically by provider name."""

from __future__ import annotations

from pathlib import Path
import re


README_PATH = Path(__file__).resolve().parents[1] / "README.md"

ROW_PATTERN = re.compile(
    r"^\|\s*\[(?P<name>[^\]]+)\]\(https?://[^)]+\)\s*\|.*\|$"
)

SECTION_HEADER = "| Name "
SECTION_FOOTER = "^\\| --"


def extract_rows(lines: list[str]) -> tuple[int, int, list[tuple[int, str]]]:
    """Find table bounds, return (start, end, [(line_index, line_text), ...])."""
    start = end = -1
    rows: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if line.startswith(SECTION_HEADER):
            start = i + 2  # skip header + separator
        if start != -1 and end == -1:
            if line.startswith("|"):
                if ROW_PATTERN.match(line):
                    rows.append((i, line))
                else:
                    # malformed or non-matching row — still inside table
                    pass
            else:
                end = i
    if end == -1:
        end = len(lines)
    return start, end, rows


def sort_table() -> bool:
    content = README_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()

    start, end, rows = extract_rows(lines)
    if not rows:
        print("No table rows found")
        return False

    sorted_rows = sorted(rows, key=lambda r: r[1].strip().lower())

    if sorted_rows == rows:
        return False

    # rebuild lines
    new_lines = list(lines[:start])
    for _, row_text in sorted_rows:
        new_lines.append(row_text)
    new_lines.extend(lines[end:])

    README_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return True


def main() -> None:
    changed = sort_table()
    print("README sorted" if changed else "No changes needed")


if __name__ == "__main__":
    main()
