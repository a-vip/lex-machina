"""
Comparative Global National, Sub-National & Technical Standard AI Governance Fetcher
(`src/ingest/national_fetcher.py` — v3.0).

Ingests official verbatim primary texts where available (with cryptographic SHA-256 digests)
and transparent `structured_regulatory_brief` records for WAF-gated / non-XML milestones:
1. United States Federal: NIST AI RMF 1.0 (`NIST.AI.100-1.pdf`), NIST AI 600-1 GenAI Profile
   (`NIST.AI.600-1.pdf`), and Jan 20, 2025 EO 14110 revocation.
2. United States Binding State Statutes: Texas TRAIGA (`HB 149` verbatim enrolled HTML from
   `capitol.texas.gov`), Colorado AI Act (`SB 24-205` / `SB 26-189`), California `AB 2013` & `SB 53` (TFAIA).
3. People's Republic of China CAC: Official verbatim HTML from `www.cac.gov.cn` parsed by
   Chinese statutory article markers (`第一条`..`第三十五条`) across Order No. 9, Order No. 12,
   Order No. 15 (GenAI), and the Sept 1, 2025 Mandatory AI Labeling Measures (`GB 45438-2025`).
4. United Kingdom: Official GOV.UK PDFs (`A Pro-Innovation Approach to AI Regulation` White Paper,
   `Introducing the AI Safety Institute`, and `Data (Use and Access) Act 2025` c. 18 record).
5. Singapore: Official IMDA `Model AI Governance Framework for Agentic AI` (2026 PDF).
6. South Korea: `AI Basic Act` (Act No. 20676 & Presidential Decree No. 36053, effective Jan 22, 2026).
7. Japan: `AI Promotion Act` (Act No. 53 of 2025, promulgated June 4, 2025, fully in force Sept 1, 2025).
8. Brazil: `PL 2338/2023` AI Regulatory Framework (Senate-approved Dec 2024; Chamber review 2025–2026).
9. ISO/IEC 42001:2023 AI Management System Standard normative crosswalk.
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
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


_CN_DIGITS = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def _cn_num_to_int(s: str) -> int | None:
    """Convert Chinese statutory article numerals (e.g. `第一条`, `第十四条`, `第三十五条`) to Arabic int."""
    s = s.strip()
    if s.isdigit():
        return int(s)
    total = 0
    if "百" in s:
        parts = s.split("百", 1)
        total += (_CN_DIGITS.get(parts[0], 1) if parts[0] else 1) * 100
        s = parts[1]
    if "十" in s:
        parts = s.split("十", 1)
        total += (_CN_DIGITS.get(parts[0], 1) if parts[0] else 1) * 10
        s = parts[1]
    s = s.replace("零", "")
    if s:
        if s not in _CN_DIGITS:
            return None
        total += _CN_DIGITS[s]
    return total if total > 0 else None


def _parse_cn_cac_html(raw_bytes: bytes, version: dict[str, Any]) -> list[dict[str, str]]:
    """
    Parse official Cyberspace Administration of China (`www.cac.gov.cn`) statutory HTML
    into individual verbatim articles (`第一条`..`第三十五条`), preserving exact official Chinese
    text alongside English stage/article metadata for bilingual BM25 search and verification.
    """
    if BeautifulSoup is None:
        return []
    soup = BeautifulSoup(raw_bytes, "lxml")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    lines = []
    for el in soup.find_all(["p", "div", "li"]):
        if el.find(["p", "div", "li"]):
            continue
        t = _clean_text(el.get_text(" "))
        if t:
            lines.append(t)
    full_txt = "\n".join(lines) if len(lines) > 8 else _clean_text(soup.get_text("\n"))

    # Match Chinese statutory article starts (`第一条 ...`)
    art_re = re.compile(r"(?m)^\s*第([一二三四五六七八九十百零\d]+)条[\s　：:]*")
    hits = list(art_re.finditer(full_txt))
    if len(hits) < 3:
        return []

    articles: list[dict[str, str]] = []
    seen: set[int] = set()
    sym = version.get("document_symbol", "CAC Measure")
    for idx, m in enumerate(hits):
        num = _cn_num_to_int(m.group(1))
        if num is None or num in seen or num > 150:
            continue
        start = m.start()
        end = hits[idx + 1].start() if idx + 1 < len(hits) else min(len(full_txt), start + 6000)
        body = full_txt[start:end].strip()
        if len(body) >= 15:
            seen.add(num)
            articles.append({
                "number": str(num),
                "eid": f"cn_art_{num}",
                "title": f"{sym} — Article {num} (第{m.group(1)}条)",
                "text": body[:12000],
            })
    return articles


def _parse_us_texas_hb149_html(raw_bytes: bytes, version: dict[str, Any]) -> list[dict[str, str]]:
    """
    Parse official Texas Legislature Online enrolled HTML (`HB00149F.htm` — Texas Responsible
    Artificial Intelligence Governance Act / TRAIGA) into clean statutory sections.
    """
    if BeautifulSoup is None:
        return []
    soup = BeautifulSoup(raw_bytes, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    full_txt = _clean_text(soup.get_text("\n"))

    # Prefer `Sec. 551.xxx` / `Sec. 503.xxx` codified sections; also capture top-level `SECTION N.`
    sec_re = re.compile(r"(?m)^(?:Sec\.\s*(\d+\.\d+)\.\s*([^\n]{0,140})|SECTION\s+(\d+)\.\s*([^\n]{0,140}))$")
    hits = list(sec_re.finditer(full_txt))
    if len(hits) < 3:
        # Try inline split when table cells put `SECTION 1.` with leading whitespace
        hits = list(re.finditer(r"(?m)(?:^|\s)(SECTION\s+(\d+)\.)", full_txt))
        if len(hits) < 2:
            return []
        articles: list[dict[str, str]] = []
        seen: set[str] = set()
        for idx, m in enumerate(hits):
            num = m.group(2)
            if num in seen:
                continue
            start = m.start()
            end = hits[idx + 1].start() if idx + 1 < len(hits) else len(full_txt)
            body = full_txt[start:end].strip()
            if len(body) >= 30:
                seen.add(num)
                articles.append({
                    "number": num,
                    "eid": f"tx_sec_{num}",
                    "title": f"Texas TRAIGA (HB 149) — Section {num}",
                    "text": body[:20000],
                })
        return articles

    articles = []
    seen_nums: set[str] = set()
    counter = 0
    for idx, m in enumerate(hits):
        code_sec, code_title, bill_sec, bill_title = m.groups()
        start = m.start()
        end = hits[idx + 1].start() if idx + 1 < len(hits) else len(full_txt)
        body = full_txt[start:end].strip()
        if len(body) < 30:
            continue
        counter += 1
        num_str = str(counter)
        if num_str in seen_nums:
            continue
        seen_nums.add(num_str)
        label = f"Tex. Bus. & Com. Code Sec. {code_sec} — {code_title.strip()}" if code_sec else f"HB 149 SECTION {bill_sec} — {bill_title.strip()[:80]}"
        articles.append({
            "number": num_str,
            "eid": f"tx_hb149_{code_sec or bill_sec}".replace(".", "_"),
            "title": label[:160],
            "text": body[:20000],
        })
    return articles


def _parse_nist_pdf(raw_bytes: bytes, stage: str) -> list[dict[str, str]]:
    """Extract NIST AI RMF Core Functions (GOVERN, MAP, MEASURE, MANAGE) from official PDF."""
    if PdfReader is None:
        return []
    reader = PdfReader(io.BytesIO(raw_bytes))
    full_text = _clean_text("\n".join((p.extract_text() or "") for p in reader.pages))
    if len(full_text) < 500:
        return []

    targets = [
        ("1", "GOVERN", r"(?m)(?:^|\s)(?:GOVERN\s+1(?:\.1)?|5\.1\s+Govern)\b"),
        ("2", "MAP", r"(?m)(?:^|\s)(?:MAP\s+1(?:\.1)?|5\.2\s+Map)\b"),
        ("3", "MEASURE", r"(?m)(?:^|\s)(?:MEASURE\s+1(?:\.1)?|5\.3\s+Measure)\b"),
        ("4", "MANAGE", r"(?m)(?:^|\s)(?:MANAGE\s+1(?:\.1)?|5\.4\s+Manage)\b"),
    ]
    found: list[tuple[int, str, str]] = []
    for num, label, pat in targets:
        hits = list(re.finditer(pat, full_text))
        if hits:
            chosen = hits[-1] if len(hits) > 1 and hits[0].start() < len(full_text) * 0.15 else hits[0]
            found.append((chosen.start(), num, label))
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


def _parse_framework_pdf(raw_bytes: bytes, version: dict[str, Any]) -> list[dict[str, str]]:
    """
    Parse official national AI governance framework PDFs (Singapore IMDA Agentic AI MGF,
    UK DSIT AI Regulation White Paper, UK AISI Paper, UK DUAA IA) into numbered sections.
    """
    if PdfReader is None:
        return []
    reader = PdfReader(io.BytesIO(raw_bytes))
    pages_text = []
    for page in reader.pages:
        try:
            t = page.extract_text() or ""
            if t.strip():
                pages_text.append(t)
        except Exception:
            continue
    full_text = _clean_text("\n".join(pages_text))
    if len(full_text) < 500:
        return []

    # Try top-level numbered sections (`1. ...`, `2. ...` or `Section 1 ...`)
    sec_re = re.compile(r"(?m)^(?:Section\s+|Chapter\s+|Dimension\s+)?(\d{1,2})\.?\s+([A-Z][^\n]{4,130})$")
    raw_hits = [m for m in sec_re.finditer(full_text) if not re.search(r"\.{3,}\s*\d+$", m.group(2))]
    sec1_hits = [m for m in raw_hits if m.group(1) == "1" and m.start() < len(full_text) * 0.30]
    start_pos = sec1_hits[-1].start() if sec1_hits else 0
    hits = [m for m in raw_hits if m.start() >= start_pos]

    articles: list[dict[str, str]] = []
    seen: set[str] = set()
    for idx, m in enumerate(hits):
        num = m.group(1)
        if num in seen or int(num) > 25:
            continue
        start = m.end()
        end = hits[idx + 1].start() if idx + 1 < len(hits) else len(full_text)
        body = full_text[start:end].strip()
        if len(body) >= 150:
            seen.add(num)
            articles.append({
                "number": num,
                "eid": f"sec_{num}",
                "title": m.group(2).strip()[:160],
                "text": body[:25000],
            })

    if len(articles) >= 2:
        return articles

    chunk_size = 12000
    return [
        {
            "number": str(i + 1),
            "eid": f"sec_{i + 1}",
            "title": f"{version.get('stage_label', 'Framework')} — Part {i + 1}",
            "text": full_text[i * chunk_size : (i + 1) * chunk_size].strip(),
        }
        for i in range(min(12, (len(full_text) + chunk_size - 1) // chunk_size))
    ]


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
                "title": "Colorado Artificial Intelligence Act (SB 24-205 -> Revised by SB 26-189)",
                "text": "Structured statutory record (enacted May 17, 2024; later amended/replaced via SB 26-189 following xAI v. Weiser): Established a reasonable-care duty for developers and deployers of high-risk AI / automated decision-making technology (ADMT) in consequential decisions (employment, education, lending, housing, healthcare, insurance, legal services) to prevent algorithmic discrimination, providing a rebuttable presumption of reasonable care when aligned with NIST AI RMF or ISO/IEC 42001.",
            },
            {
                "number": "2",
                "title": "California AB 2013 & SB 53 (Transparency in Frontier AI Act — TFAIA)",
                "text": "Structured statutory record (2024-2026): AB 2013 (effective Jan 1, 2026) mandates high-level generative AI training dataset transparency disclosures; SB 53 (TFAIA) targets frontier foundation models exceeding 10^26 FLOPs with public catastrophic risk frameworks, critical safety incident reporting to California OES, and frontier lab whistleblower protections.",
            },
        ],
        "national-kr-ai-basic-act::ai_basic_act_enacted_2025": [
            {
                "number": "1",
                "title": "Purpose & Scope — Framework Act on the Development of AI and Creation of a Foundation for Trust (Act No. 20676)",
                "text": "Structured statutory record (promulgated Jan 21, 2025; effective Jan 22, 2026): Asia's first comprehensive statutory AI law combining pro-innovation infrastructure promotion with risk-based oversight under the Ministry of Science and ICT (MSIT) and Presidential Council on National AI Strategy.",
            },
            {
                "number": "2",
                "title": "High-Impact AI Governance & Safety Obligations (Act No. 20676)",
                "text": "Structured statutory record (effective Jan 22, 2026): Imposes lifecycle risk management, human oversight, impact assessment, and user-explanation duties on 'High-Impact AI' deployed in critical domains (energy, drinking water, healthcare, nuclear safety, biometrics, criminal justice, credit/lending, recruitment, transportation).",
            },
            {
                "number": "3",
                "title": "Generative AI Advance Notice, Synthetic Watermarking & Extraterritorial Domestic Agent",
                "text": "Structured statutory record (effective Jan 22, 2026; Presidential Decree No. 36053): Mandates advance disclosure when services utilize high-impact or generative AI, visible/machine-readable synthetic content labeling for deepfakes, safety evaluations for cumulative compute frontier models, and mandatory designation of a Korean domestic representative by large foreign AI operators.",
            },
        ],
        "national-jp-ai-promotion-act::ai_promotion_act_2025": [
            {
                "number": "1",
                "title": "Enactment & Innovation-First Architecture — Japan AI Promotion Act (Act No. 53 of 2025)",
                "text": "Structured statutory record (enacted May 28, 2025; promulgated June 4, 2025; fully in force Sept 1, 2025): Establishes Japan's statutory 'Act on Promotion of Research, Development, and Utilization of Artificial Intelligence-Related Technologies' prioritizing R&D acceleration, compute/data infrastructure, and international regulatory interoperability without EU-style upfront administrative fines.",
            },
            {
                "number": "2",
                "title": "AI Strategy Headquarters, AI Basic Plan & Misuse Investigation Powers",
                "text": "Structured statutory record (effective Sept 1, 2025): Establishes the Prime Minister-led AI Strategy Headquarters and mandatory national AI Basic Plan, obligating private AI businesses to cooperate with government investigations into rights-infringing AI incidents and authorizing public naming/guidance for serious non-compliance.",
            },
        ],
        "national-br-ai-bill-pl2338::senate_approved_2024": [
            {
                "number": "1",
                "title": "Brazil AI Regulatory Framework (PL 2338/2023) — Risk-Based Architecture & SIA",
                "text": "Structured legislative record (approved by Brazilian Federal Senate Dec 10, 2024; under Chamber of Deputies Special Committee PL233823 review in 2025-2026; NOT YET ENACTED): Establishes EU-inspired excessive-risk prohibitions, high-risk algorithmic impact assessments, copyright remuneration/opt-out rights for AI training data, and the National System for Regulation and Governance of AI (SIA) coordinated by the ANPD.",
            },
        ],
        "national-uk-ai-governance::duaa_2025_c18": [
            {
                "number": "1",
                "title": "UK Data (Use and Access) Act 2025 (2025 c. 18) — Automated Decision-Making & Smart Data",
                "text": "Structured statutory record (Royal Assent 2025; 2025 c. 18): Reforms UK GDPR Article 22 automated decision-making rules (permitting ADM beyond special-category data subject to mandatory transparency, contestability, and human-intervention safeguards), establishes Smart Data schemes, modernizes ICO governance, and mandates statutory copyright/AI transparency reporting.",
            },
        ],
        "standards-iso-iec-42001::iso_42001_2023_crosswalk": [
            {
                "number": "1",
                "title": "ISO/IEC 42001:2023 AI Management System (AIMS) — Global Statutory Crosswalk",
                "text": "Structured standards crosswalk record (published Dec 2023; widely adopted as statutory safe harbor 2024-2026): International certifiable management-system standard (Clauses 4-10 + Annex A 38 controls covering AI risk assessment, data provenance, system impact assessments, human oversight, third-party supply chain, and incident logging). Cross-maps directly to EU AI Act Articles 9 & 17 QMS, Colorado AI Act safe harbor, NIST AI RMF 1.0/600-1, South Korea AI Basic Act, and Singapore Agentic AI MGF.",
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


BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


def _parse_govuk_html(raw_bytes: bytes, version: dict[str, Any]) -> list[dict[str, str]]:
    """Parse official GOV.UK HTML publications (UK AISI Overview, UK Data Use & Access Act 2025 Guidance)."""
    if BeautifulSoup is None:
        return []
    soup = BeautifulSoup(raw_bytes, "lxml")
    main = soup.find("main") or soup.find("article") or soup
    for tag in main(["script", "style", "nav", "aside", "footer"]):
        tag.decompose()

    sections: list[dict[str, str]] = []
    cur_title = version.get("stage_label", "UK Government Publication")
    cur_lines: list[str] = []

    def _flush() -> None:
        nonlocal cur_lines
        body = "\n".join(cur_lines).strip()
        if len(body) >= 80:
            sec_num = str(len(sections) + 1)
            sections.append({
                "number": sec_num,
                "eid": f"govuk_sec_{sec_num}",
                "title": cur_title[:160],
                "text": body[:20000],
            })
        cur_lines = []

    for el in main.find_all(["h2", "h3", "p", "li"]):
        txt = _clean_text(el.get_text(" "))
        if not txt:
            continue
        if el.name == "h2":
            _flush()
            cur_title = txt
        else:
            cur_lines.append(txt)
    _flush()
    return sections


def fetch_national_stage(
    instrument: dict[str, Any],
    version: dict[str, Any],
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Fetch national/sub-national AI governance texts (US NIST PDFs, US TX HB 149 HTML,
    China CAC official HTML, Singapore IMDA Agentic AI PDF, UK GOV.UK PDFs/HTML, and
    Korea/Japan/Brazil/ISO 42001 records) with SHA-256 provenance and v8 caching.
    """
    instrument_id = instrument["id"]
    stage = version["stage"]
    cache_key = f"{instrument_id}__{stage}__v8"

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

    if httpx is not None and source_type != "regulatory_supplement" and source_url.startswith("http"):
        try:
            with httpx.Client(timeout=45.0, follow_redirects=True) as client:
                accept = "application/pdf,*/*;q=0.8" if source_type in ("national_pdf", "framework_pdf") else "text/html,application/xhtml+xml;q=0.9"
                ua = BROWSER_UA if source_type in ("framework_pdf", "govuk_html", "us_tx_html") else USER_AGENT
                resp = client.get(source_url, headers={"User-Agent": ua, "Accept": accept})
                http_status = resp.status_code
                if resp.status_code == 200 and len(resp.content) >= 500:
                    raw_bytes = resp.content
                    sha256_digest = hashlib.sha256(raw_bytes).hexdigest()
                    final_url = str(resp.url)
                    http_etag = resp.headers.get("etag")
                    bytes_fetched = len(raw_bytes)

                    if source_type == "national_pdf" and raw_bytes[:4] == b"%PDF":
                        nist_arts = _parse_nist_pdf(raw_bytes, stage)
                        if nist_arts:
                            parsed = {"recitals": [], "articles": nist_arts, "annexes": []}
                            provenance_mode = "full_primary_pdf"
                    elif source_type == "framework_pdf" and raw_bytes[:4] == b"%PDF":
                        fw_arts = _parse_framework_pdf(raw_bytes, version)
                        if fw_arts:
                            parsed = {"recitals": [], "articles": fw_arts, "annexes": []}
                            provenance_mode = "full_primary_pdf"
                    elif source_type == "cn_cac_html":
                        cn_arts = _parse_cn_cac_html(raw_bytes, version)
                        if cn_arts:
                            parsed = {"recitals": [], "articles": cn_arts, "annexes": []}
                            provenance_mode = "full_primary_html"
                    elif source_type == "us_tx_html":
                        tx_arts = _parse_us_texas_hb149_html(raw_bytes, version)
                        if tx_arts:
                            parsed = {"recitals": [], "articles": tx_arts, "annexes": []}
                            provenance_mode = "full_primary_html"
                    elif source_type == "govuk_html":
                        uk_arts = _parse_govuk_html(raw_bytes, version)
                        if uk_arts:
                            parsed = {"recitals": [], "articles": uk_arts, "annexes": []}
                            provenance_mode = "full_primary_html"
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
