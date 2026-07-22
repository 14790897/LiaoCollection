#!/usr/bin/env python3
"""Promote missing chapter titles, then remove the redundant source TOC."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from remove_redundant_toc import COMMENT, HEADING, NUMBERED_ENTRY, TOC_MARKER, normalized_title


SUMMARY_LINK = re.compile(r"\]\(([^)]+\.md)\)")


@dataclass
class Reconciliation:
    start: int
    end: int
    promote: dict[int, str]
    entries: int


def find_reconciliation(lines: list[str]) -> Reconciliation | None:
    try:
        marker = lines.index(TOC_MARKER)
    except ValueError:
        return None

    numbered: list[int] = []
    block_end: int | None = None
    for index in range(marker + 1, len(lines)):
        line = lines[index]
        if line.startswith("##") and "目录" not in line and not numbered:
            return None
        if NUMBERED_ENTRY.match(line):
            numbered.append(index)
        if (
            numbered
            and index + 2 < len(lines)
            and not line
            and not lines[index + 1]
            and not lines[index + 2]
        ):
            block_end = index
            break
    if not numbered or block_end is None:
        return None

    entries = [NUMBERED_ENTRY.match(lines[index]).group(1).strip() for index in numbered]
    extras = [
        lines[index].strip()
        for index in range(marker + 1, numbered[-1] + 1)
        if lines[index].strip()
        and index not in numbered
        and "目录" not in lines[index]
        and not COMMENT.fullmatch(lines[index])
    ]
    if len(extras) > 10:
        return None

    heading_titles = {
        normalized_title(match.group(1).strip())
        for line in lines[block_end:]
        if (match := HEADING.match(line))
    }
    plain_lines: dict[str, list[int]] = {}
    for index in range(block_end, len(lines)):
        line = lines[index].strip()
        if not line or line.startswith(("#", "<", "- ", "* ", ">", "|")):
            continue
        plain_lines.setdefault(normalized_title(line), []).append(index)

    promote: dict[int, str] = {}
    for title in entries + extras:
        normalized = normalized_title(title)
        if normalized in heading_titles:
            continue
        matches = plain_lines.get(normalized, [])
        if not matches:
            return None
        promote[matches[0]] = title
        heading_titles.add(normalized)

    end = numbered[-1] + 1
    while end < len(lines) and not lines[end]:
        end += 1
    return Reconciliation(marker + 1, end, promote, len(entries))


def reconcile(text: str) -> tuple[str, int, int]:
    lines = text.splitlines()
    change = find_reconciliation(lines)
    if change is None:
        return text, 0, 0
    for index, title in change.promote.items():
        lines[index] = f"## {title}"
    rendered = lines[: change.start] + [""] + lines[change.end :]
    return "\n".join(rendered).rstrip() + "\n", change.entries, len(change.promote)


def active_paths(root: Path) -> list[Path]:
    summary = (root / "SUMMARY.md").read_text()
    return sorted(
        path
        for match in SUMMARY_LINK.findall(summary)
        if (path := root / match).exists()
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    files = 0
    entries = 0
    promoted = 0
    for path in active_paths(args.root):
        original = path.read_text()
        rendered, removed, headings = reconcile(original)
        if not removed:
            continue
        files += 1
        entries += removed
        promoted += headings
        print(f"{path.relative_to(args.root)}: entries={removed} headings={headings}")
        if args.apply:
            path.write_text(rendered)
    print(f"files={files} entries={entries} headings={promoted} apply={args.apply}")


if __name__ == "__main__":
    main()
