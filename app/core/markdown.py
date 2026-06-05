from __future__ import annotations

import re
from html import escape

from markupsafe import Markup


INLINE_PATTERNS = [
    (re.compile(r"\*\*(.+?)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"__(.+?)__"), r"<strong>\1</strong>"),
    (re.compile(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)"), r"<em>\1</em>"),
    (re.compile(r"(?<!_)_(?!\s)(.+?)(?<!\s)_(?!_)"), r"<em>\1</em>"),
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)"), r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>'),
]

ORDERED_LIST_RE = re.compile(r"(\d+)\.\s+(.*)")
UNORDERED_LIST_RE = re.compile(r"[-*]\s+(.*)")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")


def _render_inline(text: str) -> str:
    escaped = escape(text)
    for pattern, replacement in INLINE_PATTERNS:
        escaped = pattern.sub(replacement, escaped)
    return escaped


def _split_table_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def _parse_table_alignments(line: str) -> list[str]:
    alignments: list[str] = []
    for cell in _split_table_row(line):
        raw = cell.replace(" ", "")
        if raw.startswith(":") and raw.endswith(":"):
            alignments.append("center")
        elif raw.endswith(":"):
            alignments.append("right")
        else:
            alignments.append("left")
    return alignments


def render_markdown(value: str | None) -> Markup:
    if not value:
        return Markup("")

    lines = value.replace("\r\n", "\n").split("\n")
    parts: list[str] = []
    paragraph: list[str] = []
    list_stack: list[str] = []
    list_item_open: list[bool] = []
    i = 0

    def close_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            parts.append(f"<p>{'<br>'.join(_render_inline(line) for line in paragraph)}</p>")
            paragraph = []

    def close_lists(target_depth: int = 0) -> None:
        while len(list_stack) > target_depth:
            if list_item_open[-1]:
                parts.append("</li>")
                list_item_open[-1] = False
            parts.append(f"</{list_stack[-1]}>")
            list_stack.pop()
            list_item_open.pop()

    def ensure_list(depth: int, tag: str) -> None:
        while len(list_stack) > depth + 1:
            close_lists(len(list_stack) - 1)

        if len(list_stack) == depth + 1 and list_stack[-1] != tag:
            close_lists(depth)

        while len(list_stack) < depth + 1:
            next_tag = tag if len(list_stack) == depth else "ul"
            parts.append(f"<{next_tag}>")
            list_stack.append(next_tag)
            list_item_open.append(False)

        if list_stack[-1] != tag:
            parts.append(f"<{tag}>")
            list_stack.append(tag)
            list_item_open.append(False)

    while i < len(lines):
        raw_line = lines[i]
        stripped = raw_line.strip()
        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if not stripped:
            close_paragraph()
            close_lists()
            i += 1
            continue

        if (
            "|" in stripped
            and i + 1 < len(lines)
            and TABLE_SEPARATOR_RE.match(lines[i + 1].strip())
        ):
            close_paragraph()
            close_lists()
            headers = _split_table_row(stripped)
            alignments = _parse_table_alignments(lines[i + 1].strip())
            rows: list[list[str]] = []
            i += 2
            while i < len(lines):
                table_line = lines[i].strip()
                if not table_line or "|" not in table_line:
                    break
                rows.append(_split_table_row(table_line))
                i += 1

            parts.append("<div class=\"markdown-table-wrap\"><table class=\"markdown-table\">")
            parts.append("<thead><tr>")
            for idx, header in enumerate(headers):
                alignment = alignments[idx] if idx < len(alignments) else "left"
                parts.append(f"<th class=\"align-{alignment}\">{_render_inline(header)}</th>")
            parts.append("</tr></thead>")
            parts.append("<tbody>")
            for row in rows:
                parts.append("<tr>")
                for idx, cell in enumerate(row):
                    alignment = alignments[idx] if idx < len(alignments) else "left"
                    parts.append(f"<td class=\"align-{alignment}\">{_render_inline(cell)}</td>")
                parts.append("</tr>")
            parts.append("</tbody></table></div>")
            continue

        if stripped in {"---", "***"}:
            close_paragraph()
            close_lists()
            parts.append("<hr>")
            i += 1
            continue

        if stripped.startswith("### "):
            close_paragraph()
            close_lists()
            parts.append(f"<h3>{_render_inline(stripped[4:])}</h3>")
            i += 1
            continue

        if stripped.startswith("## "):
            close_paragraph()
            close_lists()
            parts.append(f"<h2>{_render_inline(stripped[3:])}</h2>")
            i += 1
            continue

        if stripped.startswith("# "):
            close_paragraph()
            close_lists()
            parts.append(f"<h1>{_render_inline(stripped[2:])}</h1>")
            i += 1
            continue

        if stripped.startswith("> "):
            close_paragraph()
            close_lists()
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            parts.append(f"<blockquote><p>{'<br>'.join(_render_inline(line) for line in quote_lines)}</p></blockquote>")
            continue

        ordered_match = ORDERED_LIST_RE.match(stripped)
        unordered_match = UNORDERED_LIST_RE.match(stripped)
        if ordered_match or unordered_match:
            close_paragraph()
            depth = 1 if indent >= 2 else 0
            tag = "ol" if ordered_match else "ul"
            content = ordered_match.group(2) if ordered_match else unordered_match.group(1)

            ensure_list(depth, tag)
            if list_item_open[-1]:
                parts.append("</li>")
            parts.append(f"<li>{_render_inline(content)}")
            list_item_open[-1] = True
            i += 1
            continue

        if list_stack and list_item_open[-1]:
            parts.append(f"<br>{_render_inline(stripped)}")
            i += 1
            continue

        close_lists()
        paragraph.append(stripped)
        i += 1

    close_paragraph()
    close_lists()
    return Markup("\n".join(parts))
