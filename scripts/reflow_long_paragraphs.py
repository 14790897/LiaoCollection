#!/usr/bin/env python3
"""Split overly long prose paragraphs at Chinese sentence boundaries."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

MIN_LENGTH = 480
TARGET_LENGTH = 300
MIN_CHUNK_LENGTH = 180
SENTENCE_END = re.compile(r"[。！？!?](?:[”’」』）》】])?")
MARKDOWN_BLOCK = re.compile(r"^(?:\s{4}|#{1,6}\s|>|[-+*]\s|\d+[.)]\s|\||<|```|~~~)")
SUMMARY_LINK = re.compile(r"\]\(([^)]+\.md)\)")


def split_paragraph(line: str) -> list[str]:
    if len(line) < MIN_LENGTH or MARKDOWN_BLOCK.match(line):
        return [line]

    boundaries = [match.end() for match in SENTENCE_END.finditer(line)]
    if len(boundaries) < 3:
        return [line]

    sentences: list[str] = []
    start = 0
    for end in boundaries:
        sentences.append(line[start:end])
        start = end
    if start < len(line):
        sentences.append(line[start:])

    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if current and len(current) + len(sentence) > TARGET_LENGTH and len(current) >= MIN_CHUNK_LENGTH:
            chunks.append(current)
            current = sentence
        else:
            current += sentence
    if current:
        chunks.append(current)

    if len(chunks) > 1 and len(chunks[-1]) < MIN_CHUNK_LENGTH:
        trailing = chunks.pop()
        chunks[-1] += trailing
    return chunks if len(chunks) > 1 else [line]


def reflow(text: str) -> tuple[str, int, int]:
    output: list[str] = []
    paragraphs = 0
    chunks = 0
    in_fence = False
    for line in text.splitlines():
        if line.startswith(("```", "~~~")):
            in_fence = not in_fence
            output.append(line)
            continue
        parts = [line] if in_fence else split_paragraph(line)
        if len(parts) > 1:
            paragraphs += 1
            chunks += len(parts)
            output.extend([part for chunk in parts for part in (chunk, "")][:-1])
        else:
            output.append(line)
    if not paragraphs:
        return text, 0, 0
    return "\n".join(output).rstrip() + "\n", paragraphs, chunks


def target_paths(root: Path) -> list[Path]:
    summary = (root / "SUMMARY.md").read_text()
    paths = {root / match for match in SUMMARY_LINK.findall(summary)}
    return sorted(path for path in paths if path.exists())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    changed_files = 0
    paragraph_count = 0
    chunk_count = 0
    for path in target_paths(args.root):
        original = path.read_text()
        rendered, paragraphs, chunks = reflow(original)
        if rendered == original:
            continue
        changed_files += 1
        paragraph_count += paragraphs
        chunk_count += chunks
        print(f"{path.relative_to(args.root)}: paragraphs={paragraphs} chunks={chunks}")
        if args.apply:
            path.write_text(rendered)

    print(
        f"files={changed_files} paragraphs={paragraph_count} "
        f"chunks={chunk_count} apply={args.apply}"
    )


if __name__ == "__main__":
    main()
