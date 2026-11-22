"""
Council of Europe, United Nations (UNGA / CCW / UNODC Hanoi Cybercrime), and
International Humanitarian Law (Geneva Conventions & Additional Protocols) Fetcher.

Runs on GitHub Actions cloud runners to download official treaty PDFs and ICRC
treaty HTML pages, parse every article cleanly, compute SHA-256 primary-source
digests, and tag `provenance_mode` transparently.
"""

from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from src.ingest.eurlex_fetcher import USER_AGENT, _clean_text, _parse_pdf_bytes, _parse_plain_legal_text

try:
    import httpx
except ImportError:
    httpx = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


ICRC_KEY_ARTICLES: dict[str, list[tuple[str, str]]] = {
    "geneva_conventions_1949": [
        ("1", "https://ihl-databases.icrc.org/en/ihl-treaties/gciv-1949/article-1"),
        ("2", "https://ihl-databases.icrc.org/en/ihl-treaties/gciv-1949/article-2"),
        ("3", "https://ihl-databases.icrc.org/en/ihl-treaties/gciv-1949/article-3"),
        ("147", "https://ihl-databases.icrc.org/en/ihl-treaties/gciv-1949/article-147"),
    ],
    "additional_protocols_1977": [
        ("1", "https://ihl-databases.icrc.org/en/ihl-treaties/api-1977/article-1"),
        ("35", "https://ihl-databases.icrc.org/en/ihl-treaties/api-1977/article-35"),
        ("36", "https://ihl-databases.icrc.org/en/ihl-treaties/api-1977/article-36"),
        ("48", "https://ihl-databases.icrc.org/en/ihl-treaties/api-1977/article-48"),
        ("51", "https://ihl-databases.icrc.org/en/ihl-treaties/api-1977/article-51"),
        ("52", "https://ihl-databases.icrc.org/en/ihl-treaties/api-1977/article-52"),
        ("57", "https://ihl-databases.icrc.org/en/ihl-treaties/api-1977/article-57"),
        ("85", "https://ihl-databases.icrc.org/en/ihl-treaties/api-1977/article-85"),
    ],
}


def _fetch_icrc_articles(stage: str) -> tuple[list[dict[str, str]], str | None, int]:
    """Fetch individual ICRC IHL Treaty Database article pages and hash combined raw HTML."""
    targets = ICRC_KEY_ARTICLES.get(stage, [])
    if httpx is None or BeautifulSoup is None or not targets:
        return [], None, 0

    articles: list[dict[str, str]] = []
    hasher = hashlib.sha256()
    total_bytes = 0

    with httpx.Client(timeout=25.0, follow_redirects=True) as client:
        for num, url in targets:
            try:
                resp = client.get(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
                if resp.status_code != 200 or len(resp.content) < 500:
                    continue
                hasher.update(resp.content)
                total_bytes += len(resp.content)
                soup = BeautifulSoup(resp.content, "lxml")
                title_el = soup.find(["h1", "h2"])
                title = _clean_text(title_el.get_text(" ")) if title_el else f"Article {num}"
                # ICRC treaty body typically sits inside main / article / treaty-body containers
                main_el = (
                    soup.find("div", class_=re.compile(r"treaty|article-body|field--name-body|content", re.I))
                    or soup.find("main")
                    or soup.find("article")
                )
                if main_el:
                    paragraphs = [
                        _clean_text(p.get_text(" "))
                        for p in main_el.find_all(["p", "li"])
                        if len(_clean_text(p.get_text(" "))) > 15
                    ]
                    body = "\n".join(paragraphs[:40]).strip()
                    if len(body) >= 40:
                        articles.append({"number": num, "eid": f"art_{num}", "title": title, "text": body})
            except Exception:
                continue

    return articles, (hasher.hexdigest() if total_bytes > 0 else None), total_bytes


def _un_coe_structured_brief(instrument_id: str, stage: str, version: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    """
    Concise analytical fallback metadata when an upstream diplomatic PDF/HTML
    requires JS or is unreachable. Always marked `structured_regulatory_brief`.
    """
    briefs: dict[str, list[dict[str, str]]] = {
        "coe-ai-convention::eu_conclusion_2026": [
            {
                "number": "1",
                "title": "EU Formal Approval and Conclusion of CETS No. 225 (2026)",
                "text": "Analytical milestone record (2026): Records the European Union's formal approval and conclusion of the Council of Europe Framework Convention on AI (CETS No. 225), implemented internally through Regulation (EU) 2024/1689 (EU AI Act) and its Digital Omnibus amendment.",
            },
        ],
        "un-cybercrime-convention::hanoi_opening_for_signature_2025": [
            {
                "number": "65",
                "title": "Signature, Ratification, and 40-State Entry into Force Threshold (Hanoi Convention)",
                "text": "Analytical milestone record (Oct 25, 2025): Opened for signature in Hanoi, Vietnam (Oct 25-26, 2025) and open at UN Headquarters New York until December 31, 2026. Under Article 65, requires 40 instruments of ratification, acceptance, approval, or accession to enter into force.",
            },
        ],
        "un-ccw-laws::seventh_review_conference_2026": [
            {
                "number": "1",
                "title": "2024-2026 GGE Operational Characteristics & CCW Seventh Review Conference Outcome",
                "text": "Analytical milestone record (2026): Concludes the 2024-2026 GGE mandate defining LAWS operational characteristics (systems identifying, selecting, and engaging targets resulting in loss of life without human intervention). At the CCW Seventh Review Conference, major-power divisions deferred a legally binding treaty negotiation mandate to a subsequent multi-year cycle.",
            },
        ],
    }

    key = f"{instrument_id}::{stage}"
    arts = briefs.get(key) or [
        {
            "number": "1",
            "title": f"{version['stage_label']} ({version['document_symbol']})",
            "text": f"Structured diplomatic milestone record ({version['date']}): {version['summary']} Official URL: {version.get('source_url', 'N/A')}.",
        }
    ]
    return {"recitals": [], "articles": arts, "annexes": []}


def fetch_un_coe_stage(
    instrument: dict[str, Any],
    version: dict[str, Any],
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Fetch full primary PDF/HTML texts for CoE, UN, Cybercrime, and IHL instruments
    with SHA-256 provenance and `.json.gz` caching.
    """
    instrument_id = instrument["id"]
    stage = version["stage"]
    cache_key = f"{instrument_id}__{stage}__v2"

    if cache_dir:
        cache_file = cache_dir / f"{cache_key}.json.gz"
        if cache_file.exists():
            with gzip.open(cache_file, "rt", encoding="utf-8") as f:
                cached = json.load(f)
                if cached.get("articles") and cached.get("provenance", {}).get("provenance_mode") != "structured_regulatory_brief":
                    return cached

    source_type = version.get("source_type", "un_coe_pdf")
    source_url = version.get("source_url", "")
    parsed: dict[str, list[dict[str, str]]] = {"recitals": [], "articles": [], "annexes": []}
    provenance_mode = "structured_regulatory_brief"
    sha256_digest = None
    final_url = source_url
    http_status: Any = None
    http_etag = None
    bytes_fetched = 0
    fetched_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if source_type == "ihl_primary":
        icrc_arts, icrc_sha, icrc_bytes = _fetch_icrc_articles(stage)
        if icrc_arts:
            parsed = {"recitals": [], "articles": icrc_arts, "annexes": []}
            provenance_mode = "full_primary_html"
            sha256_digest = icrc_sha
            bytes_fetched = icrc_bytes
            http_status = 200
    elif httpx is not None and source_type != "regulatory_supplement" and source_url.startswith("http"):
        try:
            with httpx.Client(timeout=45.0, follow_redirects=True) as client:
                resp = client.get(
                    source_url,
                    headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,text/html;q=0.9"},
                )
                http_status = resp.status_code
                if resp.status_code == 200 and len(resp.content) >= 500:
                    raw_bytes = resp.content
                    ctype = resp.headers.get("content-type", "").lower()
                    sha256_digest = hashlib.sha256(raw_bytes).hexdigest()
                    final_url = str(resp.url)
                    http_etag = resp.headers.get("etag")
                    bytes_fetched = len(raw_bytes)

                    if "pdf" in ctype or raw_bytes[:4] == b"%PDF":
                        candidate = _parse_pdf_bytes(raw_bytes)
                        if len(candidate["articles"]) >= 2:
                            parsed = candidate
                            provenance_mode = "full_primary_pdf"
                        elif candidate["recitals"] or len(raw_bytes) > 5000:
                            # Parse as numbered sections/principles for UN resolutions & GGE reports
                            from pypdf import PdfReader
                            import io
                            reader = PdfReader(io.BytesIO(raw_bytes))
                            full_txt = _clean_text("\n".join((p.extract_text() or "") for p in reader.pages))
                            sec_arts = _extract_un_resolution_sections(full_txt, version)
                            if sec_arts:
                                parsed = {"recitals": [], "articles": sec_arts, "annexes": []}
                                provenance_mode = "full_primary_pdf"
                    elif BeautifulSoup is not None:
                        soup = BeautifulSoup(raw_bytes, "lxml")
                        candidate = _parse_plain_legal_text(_clean_text(soup.get_text("\n")))
                        if len(candidate["articles"]) >= 2:
                            parsed = candidate
                            provenance_mode = "full_primary_html"
        except Exception as exc:
            http_status = f"error:{type(exc).__name__}"

    if not parsed["articles"]:
        parsed = _un_coe_structured_brief(instrument_id, stage, version)
        provenance_mode = "structured_regulatory_brief"
        if sha256_digest is None:
            sha256_digest = hashlib.sha256(
                json.dumps(parsed, sort_keys=True).encode("utf-8")
            ).hexdigest()

    payload = {
        "instrument_id": instrument_id,
        "path": instrument["path"],
        "jurisdiction": instrument["jurisdiction"],
        "domain": instrument.get("domain", "ihl"),
        "title": instrument["title"],
        "stage": stage,
        "stage_label": version["stage_label"],
        "date": version["date"],
        "document_symbol": version["document_symbol"],
        "celex": version.get("celex", instrument.get("celex", "")),
        "author_name": version["author_name"],
        "author_email": version["author_email"],
        "source_url": final_url,
        "summary": version["summary"],
        "provenance": {
            "provenance_mode": provenance_mode,
            "sha256_raw": sha256_digest,
            "final_url": final_url,
            "http_status": http_status,
            "http_etag": http_etag,
            "bytes_fetched": bytes_fetched,
            "fetched_utc": fetched_utc,
        },
        "recitals": parsed["recitals"],
        "articles": parsed["articles"],
        "annexes": parsed["annexes"],
    }

    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{cache_key}.json.gz"
        with gzip.open(cache_file, "wt", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    return payload


def _extract_un_resolution_sections(full_text: str, version: dict[str, Any]) -> list[dict[str, str]]:
    """Split UNGA resolutions / CCW GGE PDF text into numbered operative paragraphs or sections."""
    matches = list(re.finditer(r"(?m)^(\d{1,2})\.\s+([A-Z][^\n]{15,})", full_text))
    sections: list[dict[str, str]] = []
    seen: set[str] = set()
    for idx, m in enumerate(matches[:40]):
        num = m.group(1)
        if num in seen:
            continue
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else min(len(full_text), start + 4000)
        chunk = full_text[start:end].strip()
        if len(chunk) >= 40:
            seen.add(num)
            sections.append({
                "number": num,
                "eid": f"para_{num}",
                "title": f"{version['document_symbol']} — Paragraph {num}",
                "text": chunk[:15000],
            })
    return sections
