#!/usr/bin/env python3
"""Remove hand-written TOCs that are fully reproduced by document headings."""

from __future__ import annotations

import argparse
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


TOC_MARKER = "<!-- toc -->"
NUMBERED_ENTRY = re.compile(r"^\d{1,4}\.\s*(.+)$")
HEADING = re.compile(r"^#{2,3}\s+(.+)$")
COMMENT = re.compile(r"<!--.*-->")


def normalized_title(title: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFKC", title)
        if char.isalnum() or "\u4e00" <= char <= "\u9fff"
    )


@dataclass
class RedundantToc:
    start: int
    end: int
    entries: int


def find_redundant_toc(lines: list[str]) -> RedundantToc | None:
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

    prefix = [
        lines[index]
        for index in range(marker + 1, numbered[0])
        if lines[index]
        and "目录" not in lines[index]
        and not COMMENT.fullmatch(lines[index])
    ]
    middle = [
        lines[index]
        for index in range(numbered[0], numbered[-1] + 1)
        if lines[index] and index not in numbered
    ]
    if prefix or middle:
        return None

    titles = [NUMBERED_ENTRY.match(lines[index]).group(1).strip() for index in numbered]
    headings = {
        normalized_title(match.group(1).strip())
        for line in lines[block_end:]
        if (match := HEADING.match(line))
    }
    if any(normalized_title(title) not in headings for title in titles):
        return None

    end = numbered[-1] + 1
    while end < len(lines) and not lines[end]:
        end += 1
    return RedundantToc(marker + 1, end, len(numbered))


def clean(text: str) -> tuple[str, int]:
    lines = text.splitlines()
    toc = find_redundant_toc(lines)
    if toc is None:
        return text, 0
    rendered = lines[: toc.start] + [""] + lines[toc.end :]
    return "\n".join(rendered).rstrip() + "\n", toc.entries


def markdown_files(root: Path) -> list[Path]:
    return sorted(
        path
        for directory in root.iterdir()
        if directory.is_dir() and re.match(r"^\d{2}\.", directory.name)
        for path in directory.rglob("*.md")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    files = 0
    entries = 0
    for path in markdown_files(args.root):
        original = path.read_text()
        rendered, removed = clean(original)
        if not removed:
            continue
        files += 1
        entries += removed
        print(f"{path.relative_to(args.root)}: entries={removed}")
        if args.apply:
            path.write_text(rendered)
    print(f"files={files} entries={entries} apply={args.apply}")


if __name__ == "__main__":
    main()
