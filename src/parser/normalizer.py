"""
Article-Level Markdown Normalizer (`src/parser/normalizer.py`).

Strips HTML/Formex boilerplate and converts legal text into canonical Markdown
so line-by-line diffs are clean and semantic. Normalizes paragraphs so each
numbered paragraph `1.`, `(1)`, or point `(a)`, `(i)` starts on its own line,
allowing `git diff` and `git blame` to highlight exact sub-clause edits rather
than whole-page blocks.

Emits the exact per-instrument tree for `refs/heads/corpus`:
<jurisdiction>/<instrument-slug>/
├── metadata.json
├── full-text.md
├── instrument.md
├── preamble/
│   └── recitals.md
├── recitals/
│   └── recital-001.md
├── articles/
│   ├── article-001.md
│   └── article-005.md
└── annexes/
    └── annex-iii.md
"""

from __future__ import annotations

import json
import re
from typing import Any


def normalize_legal_paragraphs(raw_text: str) -> str:
    """
    Normalize legal prose so that every numbered paragraph `(1)`, `1.`, or
    lettered/Roman point `(a)`, `(b)`, `(i)`, `(ii)` begins on its own clean line.
    """
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n").strip()
    # Collapse multiple horizontal spaces while preserving newlines
    text = re.sub(r"[ \t]+", " ", text)
    # Break inline sub-clauses like "; (a) " or ": (a) " onto new lines
    text = re.sub(r"([;:.,])\s+(\([a-z]{1,2}\)|\([ivx]+\)|\([0-9]+\))\s+", r"\1\n\2 ", text)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines) + "\n"


def format_article_slug(number: str) -> str:
    """
    Convert an article number (e.g., '5', '4a', '28b', '147') into a zero-padded
    filename slug like 'article-005.md' or 'article-004a.md'.
    """
    match = re.match(r"^(\d+)([a-zA-Z]*)$", str(number).strip())
    if match:
        digits, suffix = match.groups()
        return f"article-{int(digits):03d}{suffix.lower()}.md"
    clean = re.sub(r"[^a-z0-9]+", "-", str(number).lower()).strip("-")
    return f"article-{clean}.md"


def format_recital_slug(number: str) -> str:
    """
    Convert a recital number (e.g., '1', '12a', '111') into 'recital-001.md'.
    """
    match = re.match(r"^(\d+)([a-zA-Z]*)$", str(number).strip())
    if match:
        digits, suffix = match.groups()
        return f"recital-{int(digits):03d}{suffix.lower()}.md"
    clean = re.sub(r"[^a-z0-9]+", "-", str(number).lower()).strip("-")
    return f"recital-{clean}.md"


def format_annex_slug(number: str) -> str:
    """
    Convert an annex identifier (e.g., 'I', 'III') into 'annex-i.md', 'annex-iii.md'.
    """
    clean = re.sub(r"[^a-z0-9]+", "-", str(number).lower()).strip("-")
    return f"annex-{clean}.md"


def render_stage_files(
    instrument: dict[str, Any],
    version: dict[str, Any],
    stage_payload: dict[str, Any],
) -> dict[str, str]:
    """
    Render the complete dictionary of `{relative_repo_path: file_content_str}`
    for a single instrument at a specific chronological version stage.
    """
    base_path = instrument["path"].strip("/")
    files: dict[str, str] = {}

    metadata = {
        "instrument_id": instrument["id"],
        "path": base_path,
        "jurisdiction": instrument["jurisdiction"],
        "title": instrument["title"],
        "short_title": instrument.get("short_title", instrument["title"]),
        "type": instrument.get("type", "instrument"),
        "celex": version.get("celex") or instrument.get("celex"),
        "document_symbol": version["document_symbol"],
        "stage": version["stage"],
        "stage_label": version["stage_label"],
        "published_date": version["date"],
        "in_force_date": instrument.get("in_force_date"),
        "status": instrument.get("status"),
        "institutional_author": {
            "name": version["author_name"],
            "email": version["author_email"],
        },
        "source_url": version.get("source_url"),
        "summary": version.get("summary"),
        "counts": {
            "recitals": len(stage_payload.get("recitals", [])),
            "articles": len(stage_payload.get("articles", [])),
            "annexes": len(stage_payload.get("annexes", [])),
        },
    }
    files[f"{base_path}/metadata.json"] = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"

    full_sections: list[str] = [
        f"# {instrument['title']}",
        "",
        f"- **Stage**: {version['stage_label']} (`{version['stage']}`)",
        f"- **Document Symbol**: `{version['document_symbol']}`",
        f"- **Date**: `{version['date']}`",
        f"- **Institutional Author**: `{version['author_name']} <{version['author_email']}>`",
        f"- **Source**: {version.get('source_url', 'N/A')}",
        "",
        f"> {version.get('summary', '')}",
        "",
    ]

    # Recitals
    recitals = stage_payload.get("recitals", [])
    recital_blocks: list[str] = [
        f"# Preamble & Recitals — {instrument.get('short_title', instrument['title'])}",
        f"**Stage**: {version['stage_label']} ({version['date']})",
        "",
    ]
    for rec in recitals:
        rec_num = str(rec["number"])
        norm_text = normalize_legal_paragraphs(rec["text"]).strip()
        rec_md = (
            f"# Recital ({rec_num})\n\n"
            f"- **Instrument**: {instrument.get('short_title', instrument['title'])}\n"
            f"- **Stage**: {version['stage_label']} (`{version['date']}`)\n"
            f"- **Author**: {version['author_name']} `<{version['author_email']}>`\n\n"
            f"{norm_text}\n"
        )
        rec_slug = format_recital_slug(rec_num)
        files[f"{base_path}/recitals/{rec_slug}"] = rec_md
        recital_blocks.append(f"## Recital ({rec_num})\n\n{norm_text}\n")

    preamble_text = "\n".join(recital_blocks).strip() + "\n"
    files[f"{base_path}/preamble/recitals.md"] = preamble_text
    if recitals:
        full_sections.append("## Preamble & Recitals\n")
        for rec in recitals:
            full_sections.append(normalize_legal_paragraphs(rec["text"]).strip() + "\n")

    # Articles
    articles = stage_payload.get("articles", [])
    if articles:
        full_sections.append("## Enacting Terms (Articles)\n")
    for art in articles:
        art_num = str(art["number"])
        art_title = art.get("title", "").strip()
        norm_text = normalize_legal_paragraphs(art["text"]).strip()
        heading = f"# Article {art_num}" + (f" — {art_title}" if art_title else "")
        art_md = (
            f"{heading}\n\n"
            f"- **Instrument**: {instrument.get('short_title', instrument['title'])}\n"
            f"- **Stage**: {version['stage_label']} (`{version['date']}`)\n"
            f"- **Document Symbol**: `{version['document_symbol']}`\n"
            f"- **Institutional Author**: {version['author_name']} `<{version['author_email']}>`\n\n"
            f"{norm_text}\n"
        )
        art_slug = format_article_slug(art_num)
        files[f"{base_path}/articles/{art_slug}"] = art_md
        full_sections.append(f"### Article {art_num}" + (f" — {art_title}" if art_title else ""))
        full_sections.append("")
        full_sections.append(norm_text)
        full_sections.append("")

    # Annexes
    annexes = stage_payload.get("annexes", [])
    if annexes:
        full_sections.append("## Annexes\n")
    for anx in annexes:
        anx_num = str(anx["number"])
        anx_title = anx.get("title", "").strip()
        norm_text = normalize_legal_paragraphs(anx["text"]).strip()
        heading = f"# Annex {anx_num}" + (f" — {anx_title}" if anx_title else "")
        anx_md = (
            f"{heading}\n\n"
            f"- **Instrument**: {instrument.get('short_title', instrument['title'])}\n"
            f"- **Stage**: {version['stage_label']} (`{version['date']}`)\n"
            f"- **Institutional Author**: {version['author_name']} `<{version['author_email']}>`\n\n"
            f"{norm_text}\n"
        )
        anx_slug = format_annex_slug(anx_num)
        files[f"{base_path}/annexes/{anx_slug}"] = anx_md
        full_sections.append(f"### Annex {anx_num}" + (f" — {anx_title}" if anx_title else ""))
        full_sections.append("")
        full_sections.append(norm_text)
        full_sections.append("")

    compiled_markdown = "\n".join(full_sections).strip() + "\n"
    files[f"{base_path}/full-text.md"] = compiled_markdown
    files[f"{base_path}/instrument.md"] = compiled_markdown

    return files
