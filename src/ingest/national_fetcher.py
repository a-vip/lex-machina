"""
Comparative National & Sub-National AI Governance Fetcher (`src/ingest/national_fetcher.py`).

Covers:
1. US Federal AI Trajectory: NIST AI RMF 1.0 (NIST AI 100-1) -> NIST AI 600-1 GenAI
   Profile -> January 20, 2025 Revocation of Executive Order 14110.
2. US Binding State AI Statutes: Colorado AI Act (SB 24-205 / SB 26-189), Texas TRAIGA
   (HB 149, effective Jan 1, 2026), California AB 2013 & SB 53 (TFAIA).
3. China CAC AI Regulatory Architecture: Algorithmic Recommendation (2022) -> Deep
   Synthesis (2022) -> Generative AI Interim Measures (2023) -> Mandatory AI-Generated
   Synthetic Content Labeling Measures (effective Sept 1, 2025).
"""

from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import io
import json
import re
from pathlib import Path
from typing import Any

from src.ingest.eurlex_fetcher import USER_AGENT, _clean_text

try:
    import httpx
except ImportError:
    httpx = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


def _parse_nist_pdf(raw_bytes: bytes, stage: str) -> list[dict[str, str]]:
    """Extract NIST AI RMF Core Functions (GOVERN, MAP, MEASURE, MANAGE) from official PDF."""
    if PdfReader is None:
        return []
    reader = PdfReader(io.BytesIO(raw_bytes))
    full_text = _clean_text("\n".join((p.extract_text() or "") for p in reader.pages))
    if len(full_text) < 500:
        return []

    targets = [
        ("1", "GOVERN", r"\bGOVERN\s+1\b|\b5\.1\s+Govern\b"),
        ("2", "MAP", r"\bMAP\s+1\b|\b5\.2\s+Map\b"),
        ("3", "MEASURE", r"\bMEASURE\s+1\b|\b5\.3\s+Measure\b"),
        ("4", "MANAGE", r"\bMANAGE\s+1\b|\b5\.4\s+Manage\b"),
    ]
    found: list[tuple[int, str, str]] = []
    for num, label, pat in targets:
        m = re.search(pat, full_text)
        if m:
            found.append((m.start(), num, label))
    found.sort()

    articles: list[dict[str, str]] = []
    for idx, (pos, num, label) in enumerate(found):
        end = found[idx + 1][0] if idx + 1 < len(found) else min(len(full_text), pos + 18000)
        chunk = full_text[pos:end].strip()[:18000]
        if len(chunk) >= 100:
            articles.append({
                "number": num,
                "eid": f"nist_{label.lower()}",
                "title": f"Core Function {num} — {label} ({stage})",
                "text": chunk,
            })
    return articles


def _national_structured_brief(instrument_id: str, stage: str, version: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    """Concise, original analytical regulatory records transparently marked as structured briefs."""
    briefs: dict[str, list[dict[str, str]]] = {
        "national-us-nist-ai-rmf::eo_14110_revocation_2025": [
            {
                "number": "5",
                "title": "Revocation of Executive Order 14110 & Federal Deregulatory Pivot (2025-01-20)",
                "text": "Structured regulatory milestone record (2025-01-20): President Donald Trump formally revoked Executive Order 14110 (Oct 30, 2023) on January 20, 2025 and replaced it with 'Removing Barriers to American Leadership in Artificial Intelligence'. Federal DPA mandatory frontier-model safety disclosures were rescinded. NIST AI RMF 1.0 (NIST AI 100-1) and NIST AI 600-1 persist as voluntary enterprise governance standards alongside FTC Section 5 consumer protection enforcement and binding US state AI statutes.",
            },
        ],
        "national-us-state-ai-laws::colorado_sb24_205_2024": [
            {
                "number": "1",
                "title": "Colorado Artificial Intelligence Act (SB 24-205) — High-Risk Algorithmic Discrimination Duty",
                "text": "Structured statutory record (enacted May 17, 2024): Establishes a reasonable-care duty for developers and deployers of high-risk AI systems making consequential decisions (employment, education, lending, housing, healthcare, insurance, legal services) to protect consumers from algorithmic discrimination, providing a rebuttable presumption of reasonable care when aligned with NIST AI RMF or ISO/IEC 42001.",
            },
            {
                "number": "2",
                "title": "California AB 2013 — Generative AI Training Data Transparency",
                "text": "Structured statutory record (enacted 2024, effective Jan 1, 2026): Requires developers of publicly available generative AI systems to post high-level documentation on training dataset sources, ownership/licensing, personal information inclusion, synthetic data usage, and data collection timeframes.",
            },
        ],
        "national-us-state-ai-laws::texas_traiga_effective_2026": [
            {
                "number": "1",
                "title": "Texas Responsible Artificial Intelligence Governance Act (HB 149 / TRAIGA)",
                "text": "Structured statutory record (effective January 1, 2026): Binding Texas statute enforced exclusively by the Texas Attorney General prohibiting intentional deployment of AI systems designed to encourage self-harm or unlawful violence, government social scoring, unconstitutional infringement of rights, unlawful biometric capture without informed consent, and unlawful intentional discrimination. Includes a 60-day cure period for curable violations and a Texas AI Regulatory Sandbox.",
            },
            {
                "number": "2",
                "title": "California Frontier AI Transparency (SB 53 / TFAIA) & Colorado Amendments (SB 26-189)",
                "text": "Structured statutory record (2025-2026): Tracks California's Transparency in Frontier Artificial Intelligence Act framework establishing public safety framework disclosures, critical safety incident reporting, and whistleblower protections for frontier foundation model developers, alongside Colorado's legislative timeline and scope refinements (SB 26-189).",
            },
        ],
        "national-cn-cac-ai-measures::ai_labeling_measures_2025": [
            {
                "number": "12",
                "title": "Mandatory Explicit & Implicit AI-Generated Synthetic Content Labeling (2025)",
                "text": "Structured regulatory milestone record (effective September 1, 2025): Jointly issued by CAC, MIIT, MPS, and NRTA alongside mandatory national technical standard GB 45438-2025. Mandates both explicit user-facing labels (text notices, audio/visual watermarks) and implicit file-metadata provenance markers (provider ID, content ID, synthesis attribute) across AI generators, distribution platforms, and app stores, with strict bans on tampering or stripping labels.",
            },
            {
                "number": "18",
                "title": "Supply-Chain Liability & Platform Verification Obligations (2025)",
                "text": "Structured regulatory milestone record (effective September 1, 2025): Assigns direct administrative liability across upstream model providers, downstream app developers, and distribution platforms to verify implicit metadata markers and apply conspicuous warning labels when synthetic content lacks compliant provenance.",
            },
        ],
    }

    key = f"{instrument_id}::{stage}"
    arts = briefs.get(key) or [
        {
            "number": "1",
            "title": f"{version['stage_label']} ({version['document_symbol']})",
            "text": f"Structured national regulatory milestone record ({version['date']}): {version['summary']} Official URL: {version.get('source_url', 'N/A')}.",
        }
    ]
    return {"recitals": [], "articles": arts, "annexes": []}


def fetch_national_stage(
    instrument: dict[str, Any],
    version: dict[str, Any],
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Fetch national/sub-national AI governance texts (US NIST PDFs, US state laws,
    China CAC measures) with SHA-256 provenance and `.json.gz` caching.
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

    source_type = version.get("source_type", "national_pdf")
    source_url = version.get("source_url", "")
    parsed: dict[str, list[dict[str, str]]] = {"recitals": [], "articles": [], "annexes": []}
    provenance_mode = "structured_regulatory_brief"
    sha256_digest = None
    final_url = source_url
    http_status: Any = None
    http_etag = None
    bytes_fetched = 0
    fetched_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if httpx is not None and source_type == "national_pdf" and source_url.startswith("http"):
        try:
            with httpx.Client(timeout=45.0, follow_redirects=True) as client:
                resp = client.get(source_url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf"})
                http_status = resp.status_code
                if resp.status_code == 200 and resp.content[:4] == b"%PDF":
                    raw_bytes = resp.content
                    sha256_digest = hashlib.sha256(raw_bytes).hexdigest()
                    final_url = str(resp.url)
                    http_etag = resp.headers.get("etag")
                    bytes_fetched = len(raw_bytes)
                    nist_arts = _parse_nist_pdf(raw_bytes, stage)
                    if nist_arts:
                        parsed = {"recitals": [], "articles": nist_arts, "annexes": []}
                        provenance_mode = "full_primary_pdf"
        except Exception as exc:
            http_status = f"error:{type(exc).__name__}"

    if not parsed["articles"]:
        parsed = _national_structured_brief(instrument_id, stage, version)
        provenance_mode = "structured_regulatory_brief"
        if sha256_digest is None:
            sha256_digest = hashlib.sha256(
                json.dumps(parsed, sort_keys=True).encode("utf-8")
            ).hexdigest()

    payload = {
        "instrument_id": instrument_id,
        "path": instrument["path"],
        "jurisdiction": instrument["jurisdiction"],
        "domain": instrument.get("domain", "ai"),
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
