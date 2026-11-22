"""
Article-Level Markdown Normalizer (`src/parser/normalizer.py` — v2.0).

Converts raw parsed primary XML/XHTML/PDF provisions into canonical Markdown where
every numbered paragraph (`1.`, `(1)`) and sub-clause (`(a)`, `(i)`) begins on its
own line for surgical `git diff`, phrase-level institutional `git blame`, and
byte-exact verbatim citation verification. Embeds SHA-256 cryptographic provenance
and Akoma Ntoso `eId` anchors inside `metadata.json`.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any


def normalize_legal_paragraphs(raw_text: str) -> str:
    """
    Normalize legal prose so every numbered paragraph and lettered/Roman sub-clause
    starts on its own clean line for semantic Git diffs and phrase-level blame.
    """
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n").strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"([;:.,])\s+(\([a-z]{1,2}\)|\([ivx]+\)|\([0-9]+\))\s+", r"\1\n\2 ", text)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines) + "\n"


def format_article_slug(number: str) -> str:
    match = re.match(r"^(\d+)([a-zA-Z]*)$", str(number).strip())
    if match:
        digits, suffix = match.groups()
        return f"article-{int(digits):03d}{suffix.lower()}.md"
    clean = re.sub(r"[^a-z0-9]+", "-", str(number).lower()).strip("-")
    return f"article-{clean}.md"


def format_recital_slug(number: str) -> str:
    match = re.match(r"^(\d+)([a-zA-Z]*)$", str(number).strip())
    if match:
        digits, suffix = match.groups()
        return f"recital-{int(digits):03d}{suffix.lower()}.md"
    clean = re.sub(r"[^a-z0-9]+", "-", str(number).lower()).strip("-")
    return f"recital-{clean}.md"


def format_annex_slug(number: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "-", str(number).lower()).strip("-")
    return f"annex-{clean}.md"


def render_stage_files(
    instrument: dict[str, Any],
    version: dict[str, Any],
    stage_payload: dict[str, Any],
) -> dict[str, str]:
    """
    Render the full `{relative_repo_path: file_content}` dictionary for one
    chronological stage, including Akoma Ntoso `eId` metadata and SHA-256 hashes.
    """
    base_path = instrument["path"].strip("/")
    files: dict[str, str] = {}
    prov = stage_payload.get("provenance", {})

    recitals = stage_payload.get("recitals", [])
    articles = stage_payload.get("articles", [])
    annexes = stage_payload.get("annexes", [])

    full_sections: list[str] = [
        f"# {instrument['title']}",
        "",
        f"- **Stage**: {version['stage_label']} (`{version['stage']}`)",
        f"- **Document Symbol**: `{version['document_symbol']}`",
        f"- **Date**: `{version['date']}`",
        f"- **Institutional Author**: `{version['author_name']} <{version['author_email']}>`",
        f"- **Provenance Mode**: `{prov.get('provenance_mode', 'unknown')}`",
        f"- **Primary Source SHA-256**: `{prov.get('sha256_raw', 'n/a')}`",
        f"- **Source URL**: {prov.get('final_url') or version.get('source_url', 'N/A')}",
        "",
        f"> {version.get('summary', '')}",
        "",
    ]

    # Recitals
    recital_blocks: list[str] = [
        f"# Preamble & Recitals — {instrument.get('short_title', instrument['title'])}",
        f"**Stage**: {version['stage_label']} ({version['date']})",
        "",
    ]
    for rec in recitals:
        rec_num = str(rec["number"])
        eid = rec.get("eid", f"rct_{rec_num}")
        norm_text = normalize_legal_paragraphs(rec["text"]).strip()
        rec_md = (
            f"# Recital ({rec_num})\n\n"
            f"- **Instrument**: {instrument.get('short_title', instrument['title'])}\n"
            f"- **Stage**: {version['stage_label']} (`{version['date']}`)\n"
            f"- **Akoma Ntoso eId**: `{eid}`\n"
            f"- **Provenance Mode**: `{prov.get('provenance_mode', 'unknown')}`\n"
            f"- **Author**: {version['author_name']} `<{version['author_email']}>`\n\n"
            f"{norm_text}\n"
        )
        rec_slug = format_recital_slug(rec_num)
        files[f"{base_path}/recitals/{rec_slug}"] = rec_md
        recital_blocks.append(f"## Recital ({rec_num})\n\n{norm_text}\n")

    files[f"{base_path}/preamble/recitals.md"] = "\n".join(recital_blocks).strip() + "\n"
    if recitals:
        full_sections.append("## Preamble & Recitals\n")
        for rec in recitals:
            full_sections.append(normalize_legal_paragraphs(rec["text"]).strip() + "\n")

    # Articles
    if articles:
        full_sections.append("## Enacting Terms (Articles)\n")
    for art in articles:
        art_num = str(art["number"])
        eid = art.get("eid", f"art_{art_num}")
        art_title = art.get("title", "").strip()
        norm_text = normalize_legal_paragraphs(art["text"]).strip()
        heading = f"# Article {art_num}" + (f" — {art_title}" if art_title else "")
        art_md = (
            f"{heading}\n\n"
            f"- **Instrument**: {instrument.get('short_title', instrument['title'])}\n"
            f"- **Stage**: {version['stage_label']} (`{version['date']}`)\n"
            f"- **Document Symbol**: `{version['document_symbol']}`\n"
            f"- **Akoma Ntoso eId**: `{eid}`\n"
            f"- **Provenance Mode**: `{prov.get('provenance_mode', 'unknown')}`\n"
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
    if annexes:
        full_sections.append("## Annexes\n")
    for anx in annexes:
        anx_num = str(anx["number"])
        eid = anx.get("eid", f"anx_{anx_num}")
        anx_title = anx.get("title", "").strip()
        norm_text = normalize_legal_paragraphs(anx["text"]).strip()
        heading = f"# Annex {anx_num}" + (f" — {anx_title}" if anx_title else "")
        anx_md = (
            f"{heading}\n\n"
            f"- **Instrument**: {instrument.get('short_title', instrument['title'])}\n"
            f"- **Stage**: {version['stage_label']} (`{version['date']}`)\n"
            f"- **Akoma Ntoso eId**: `{eid}`\n"
            f"- **Provenance Mode**: `{prov.get('provenance_mode', 'unknown')}`\n"
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

    normalized_sha256 = hashlib.sha256(compiled_markdown.encode("utf-8")).hexdigest()
    metadata = {
        "schema_version": "2.0.0",
        "instrument_id": instrument["id"],
        "path": base_path,
        "jurisdiction": instrument["jurisdiction"],
        "domain": instrument.get("domain", "ai"),
        "title": instrument["title"],
        "short_title": instrument.get("short_title", instrument["title"]),
        "type": instrument.get("type", "instrument"),
        "celex": version.get("celex") or instrument.get("celex"),
        "eli": version.get("eli") or instrument.get("eli"),
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
        "source_url": prov.get("final_url") or version.get("source_url"),
        "summary": version.get("summary"),
        "provenance": {
            **prov,
            "sha256_normalized_full_text": normalized_sha256,
        },
        "counts": {
            "recitals": len(recitals),
            "articles": len(articles),
            "annexes": len(annexes),
        },
    }
    files[f"{base_path}/metadata.json"] = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"

    return files
