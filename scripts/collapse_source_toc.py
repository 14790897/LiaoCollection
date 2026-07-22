#!/usr/bin/env python3
"""Collapse source TOCs that contain information absent from generated TOCs."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from reconcile_toc_headings import active_paths
from remove_redundant_toc import NUMBERED_ENTRY, TOC_MARKER


EDITOR_NOTE = re.compile(r"^(?:wjm_tcy\s*注|注[：:])")


def source_toc_span(lines: list[str]) -> tuple[int, int, list[int]] | None:
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
    return marker + 1, block_end, numbered


def render_details(lines: list[str], start: int, end: int, numbered: list[int]) -> tuple[list[str], list[str]]:
    numbered_set = set(numbered)
    prefix_items: list[str] = []
    groups: list[tuple[str, str, list[str]]] = []
    trailing_notes: list[str] = []
    current: tuple[str, str, list[str]] | None = None

    for index in range(start, end):
        line = lines[index].strip()
        if not line or "目录" in line or line.startswith("<!--"):
            continue
        if index in numbered_set:
            match = NUMBERED_ENTRY.match(line)
            current = (line.split(".", 1)[0], match.group(1).strip(), [])
            groups.append(current)
        elif EDITOR_NOTE.match(line):
            trailing_notes.append(line)
        elif current is None:
            prefix_items.append(line)
        else:
            current[2].append(line)

    output = [
        '<details class="leeao-source-toc">',
        "<summary>原书详细目录（含补充条目）</summary>",
        "<ul>",
    ]
    for item in prefix_items:
        output.append(f"<li>{html.escape(item)}</li>")
    for number, title, children in groups:
        label = f'<span class="leeao-source-toc-number">{html.escape(number)}.</span> {html.escape(title)}'
        if children:
            output.extend([f"<li>{label}", "<ul>"])
            output.extend(f"<li>{html.escape(child)}</li>" for child in children)
            output.extend(["</ul>", "</li>"])
        else:
            output.append(f"<li>{label}</li>")
    output.extend(["</ul>", "</details>"])
    return output, trailing_notes


def collapse(text: str) -> tuple[str, int]:
    lines = text.splitlines()
    span = source_toc_span(lines)
    if span is None:
        return text, 0
    start, end, numbered = span
    details, notes = render_details(lines, start, end, numbered)
    rendered = lines[:start] + [""] + details + ([""] + notes if notes else []) + [""] + lines[end:]
    return "\n".join(rendered).rstrip() + "\n", len(numbered)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    files = 0
    entries = 0
    for path in active_paths(args.root):
        original = path.read_text()
        rendered, collapsed = collapse(original)
        if not collapsed:
            continue
        files += 1
        entries += collapsed
        print(f"{path.relative_to(args.root)}: entries={collapsed}")
        if args.apply:
            path.write_text(rendered)
    print(f"files={files} entries={entries} apply={args.apply}")


if __name__ == "__main__":
    main()
