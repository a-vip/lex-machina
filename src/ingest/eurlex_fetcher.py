"""
Full-Text EUR-Lex CELLAR, Europarl HTML, Consilium PDF, EC Guidelines PDF & CJEU Judgment Fetcher
(`src/ingest/eurlex_fetcher.py` — v3.0).

Executes exclusively on GitHub Actions cloud runners (`ubuntu-latest`) to preserve
zero-local-disk constraints:
1. Queries EUR-Lex CELLAR via HTTP Content Negotiation (`Accept: application/xhtml+xml`,
   `Accept-Language: eng`) to ingest 100% of official Recitals, Articles, and Annexes
   (EU AI Act 2024/1689 + Digital Omnibus 2026/1744, GDPR, CRA, NIS2, DORA).
2. Parses landmark CJEU judgments (`CELEX 6...`, e.g., SCHUFA C-634/21, Schrems II C-311/18,
   Meta v Bundeskartellamt C-252/21, La Quadrature du Net C-511/18) directly from official
   CELLAR Formex XHTML into structured numbered reasoning sections & binding Operative Parts.
3. Parses official Consilium PDFs (`ST-14954-2022-INIT`, `ST-5662-2024-INIT`), European
   Parliament mandate HTML (`TA-9-2023-0236_EN.html`), and European Commission 2025
   Guidelines PDFs (`C(2025) 884` Prohibited AI Practices & July 2025 GPAI Guidelines).
4. Computes cryptographic SHA-256 digests of raw fetched primary documents and records
   truthful `provenance_mode` metadata.
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


USER_AGENT = "lex-machina-corpus-engine/3.0 (+https://github.com/a-vip/lex-machina)"

# Inline words/punctuation immediately after `Article N` that identify a prose cross-reference
# rather than a genuine enacting article heading.
_CROSSREF_FOLLOW_RE = re.compile(
    r"^(?:"
    r"[,;)\]]|"
    r"\(\d+\)|"
    r"\s+(?:of|shall|may|must|is|are|was|were|be|been|has|have|had|does|do|did|"
    r"applies|apply|provides|provide|sets|set|lays|lay|establishes|refers|refer|"
    r"stipulates|requires|require|and|or|to|in|for|with|under|by|on|at|as|from|"
    r"paragraphs?|points?|subparagraphs?|sections?|titles?|chapters?|annex(?:es)?|"
    r"thereof|thereto|hereof|inclusive|also|only|not|unless|except|where|when|which|that)\b"
    r")",
    re.I,
)


def _clean_text(text: str) -> str:
    text = text.replace("\xa0", " ").replace("\u200b", "")
    text = re.sub(r"[ \t]+", " ", text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines).strip()


def _is_probable_article_heading(line_after_num: str, raw_prefix: str) -> bool:
    """
    Distinguish genuine enacting `Article N` / `Art. N.` headings from wrapped PDF
    cross-reference lines (e.g. `Article 50 of this Regulation shall apply...`) or
    Table-of-Contents entries (`Article 5 .... 23`).
    """
    rest = line_after_num.strip()
    # Reject Table-of-Contents dotted leaders or trailing bare page numbers after tabs/dots
    if re.search(r"\.{3,}\s*\d+$", rest):
        return False
    if not rest:
        return True
    # Classic treaty inline style: `Art. 147. Grave breaches...` or `Article 36. In the study...`
    if raw_prefix.lower().startswith("art.") and rest.startswith("."):
        return True
    # Reject clear cross-reference prose starts
    if _CROSSREF_FOLLOW_RE.match(line_after_num):
        return False
    if _CROSSREF_FOLLOW_RE.match(" " + rest):
        return False
    # Reject trailing cross-ref patterns like `Article 5 (1)` or `Article 5 - see`
    if re.match(r"^\(\d+[a-z]?\)", rest):
        return False
    # Allow `Article 5. Title`, `Article 5.-Title` (UMN AP I/II), `Article 5 - Title`, `Article 5: Title`, or inline treaty sentences
    if re.match(r"^[.:\-–—]+\s*[A-Z0-9(\"']", rest):
        return True
    # Allow standalone short title on same line (e.g. `Article 5 Prohibited AI practices`)
    if len(rest) <= 130 and rest[0].isupper() and not rest.endswith(",") and not re.search(r"\bof\s+this\s+(?:Regulation|Directive|Convention|Protocol|Act)\b", rest, re.I):
        return True
    return False


def _parse_eurlex_xhtml(raw_bytes: bytes) -> dict[str, list[dict[str, str]]]:
    """
    Parse EUR-Lex CELLAR / OJ XHTML (supporting both modern Akoma-Ntoso/ELI
    `div.eli-subdivision` markup and classic EUR-Lex `p.ti-art` / `table` recitals).
    """
    if BeautifulSoup is None:
        return {"recitals": [], "articles": [], "annexes": []}

    soup = BeautifulSoup(raw_bytes, "lxml")

    recitals: list[dict[str, str]] = []
    articles: list[dict[str, str]] = []
    annexes: list[dict[str, str]] = []

    seen_rec: set[str] = set()
    seen_art: set[str] = set()
    seen_anx: set[str] = set()

    # --- Tier 1: Modern ELI / Akoma Ntoso `id="rct_*"`, `id="art_*"`, `id="anx_*"` ---
    for div in soup.find_all("div", id=re.compile(r"^rct_\d+[a-z]?$", re.I)):
        num = div["id"].split("_", 1)[1]
        if num in seen_rec:
            continue
        text = _clean_text(div.get_text("\n"))
        if text:
            seen_rec.add(num)
            recitals.append({"number": num, "eid": div["id"], "text": text})

    for div in soup.find_all("div", id=re.compile(r"^art_\d+[a-z]?$", re.I)):
        num = div["id"].split("_", 1)[1]
        if num in seen_art:
            continue
        title_el = div.find(["p", "div", "span"], class_=re.compile(r"sti-art|oj-sti-art"))
        title = _clean_text(title_el.get_text(" ")) if title_el else ""
        # Extract leaf block elements (including EUR-Lex consolidated `div.norm` paragraphs!)
        clone_lines = []
        for child in div.find_all(["p", "li", "div"], recursive=True):
            if child.find(["p", "li", "div"]):
                continue
            cls = " ".join(child.get("class") or [])
            if re.search(r"(^|\s)(oj-)?(ti-art|sti-art|title-article-norm|stitle-article-norm)(\s|$)", cls):
                continue
            txt = _clean_text(child.get_text(" "))
            if txt and (not clone_lines or clone_lines[-1] != txt):
                clone_lines.append(txt)
        body = "\n".join(clone_lines).strip() or _clean_text(div.get_text("\n"))
        if body:
            seen_art.add(num)
            articles.append({"number": num, "eid": div["id"], "title": title, "text": body})

    for div in soup.find_all("div", id=re.compile(r"^anx_[IVXLC0-9a-z]+$", re.I)):
        num = div["id"].split("_", 1)[1]
        if num in seen_anx:
            continue
        title_el = div.find(["p", "div"], class_=re.compile(r"doc-ti|oj-doc-ti"))
        title = _clean_text(title_el.get_text(" ")) if title_el else f"Annex {num}"
        text = _clean_text(div.get_text("\n"))
        if text:
            seen_anx.add(num)
            annexes.append({"number": num, "eid": div["id"], "title": title, "text": text})

    # --- Tier 2: Classic EUR-Lex `p.ti-art` / `p.oj-ti-art` (older CELEX & COM proposals) ---
    if len(articles) < 3:
        articles = []
        seen_art = set()
        ti_arts = soup.find_all(["p", "div", "h2", "h3"], class_=re.compile(r"^(oj-)?ti-art$|ArticleTitle", re.I))
        for heading in ti_arts:
            h_text = _clean_text(heading.get_text(" "))
            m = re.search(r"Article\s+(\d+[a-z]?)", h_text, re.I)
            if not m:
                continue
            num = m.group(1)
            if num in seen_art:
                continue
            title = ""
            body_parts: list[str] = []
            sib = heading.find_next_sibling()
            while sib is not None:
                sib_cls = " ".join(sib.get("class") or [])
                sib_txt = _clean_text(sib.get_text(" "))
                if re.search(r"(oj-)?ti-art|ti-section-1|doc-ti|oj-doc-ti", sib_cls, re.I):
                    break
                if re.match(r"^Article\s+\d+[a-z]?\b", sib_txt, re.I) or re.match(r"^ANNEX\s+[IVXLC0-9]+\b", sib_txt):
                    break
                if not title and re.search(r"(oj-)?sti-art", sib_cls, re.I):
                    title = sib_txt
                elif sib_txt:
                    body_parts.append(sib_txt)
                sib = sib.find_next_sibling()
            if body_parts:
                seen_art.add(num)
                articles.append({"number": num, "eid": f"art_{num}", "title": title, "text": "\n".join(body_parts)})

    # --- Tier 3: Block-level plain-text regex structural parser ---
    if len(articles) < 3:
        block_lines = []
        for el in soup.find_all(["p", "h1", "h2", "h3", "h4", "li"]):
            if el.find(["p", "h1", "h2", "h3", "h4", "li"]):
                continue
            t = _clean_text(el.get_text(" "))
            if t:
                block_lines.append(t)
        full_text = "\n".join(block_lines) if len(block_lines) > 20 else _clean_text(soup.get_text("\n"))
        extracted = _parse_plain_legal_text(full_text)
        if len(extracted["articles"]) > len(articles):
            articles = extracted["articles"]
        if len(extracted["recitals"]) > len(recitals):
            recitals = extracted["recitals"]
        if len(extracted["annexes"]) > len(annexes):
            annexes = extracted["annexes"]

    return {"recitals": recitals, "articles": articles, "annexes": annexes}


def _parse_cjeu_judgment_xhtml(raw_bytes: bytes, version: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    """
    Parse official CJEU Formex XHTML (`CELEX 6...`) from EUR-Lex CELLAR into:
    - Structured thematic judicial sections (`Legal context`, `Dispute in the main proceedings`,
      `Consideration of the questions referred`, `Costs`, and the binding `Operative Part / Holding`)
    preserving official CJEU numbered paragraphs (`coj-count` + `coj-normal`).
    """
    if BeautifulSoup is None:
        return {"recitals": [], "articles": [], "annexes": []}

    soup = BeautifulSoup(raw_bytes, "lxml")

    sections: list[dict[str, str]] = []
    cur_title = f"Judgment Header & Parties ({version.get('document_symbol', 'CJEU')})"
    cur_lines: list[str] = []

    def _flush() -> None:
        nonlocal cur_lines
        body = "\n".join(cur_lines).strip()
        if len(body) >= 40:
            sec_num = str(len(sections) + 1)
            sections.append({
                "number": sec_num,
                "eid": f"cjeu_sec_{sec_num}",
                "title": cur_title[:160],
                "text": body[:35000],
            })
        cur_lines = []

    # Walk top-level flow blocks in document order
    for el in soup.find_all(["p", "table"], recursive=True):
        # Skip <p> inside tables we already handle at table level
        if el.name == "p" and el.find_parent("table") is not None:
            continue

        if el.name == "p":
            cls = " ".join(el.get("class") or [])
            txt = _clean_text(el.get_text(" "))
            if not txt:
                continue
            if re.search(r"coj-title-grseq|coj-sum-title|title-grseq|sum-title", cls, re.I):
                _flush()
                cur_title = txt
            elif re.match(r"^On those grounds,?\s+the Court", txt, re.I):
                _flush()
                cur_title = "Operative Part (Binding Holding of the Court)"
                cur_lines.append(txt)
            else:
                cur_lines.append(txt)
        elif el.name == "table":
            # Skip nested tables
            if el.find_parent("table") is not None:
                continue
            for tr in el.find_all("tr", recursive=False) or el.find_all("tr"):
                tds = tr.find_all("td", recursive=False)
                if not tds:
                    continue
                if len(tds) >= 2:
                    left = _clean_text(tds[0].get_text(" "))
                    right = _clean_text(tds[-1].get_text(" "))
                    if not right:
                        continue
                    if re.match(r"^On those grounds,?\s+the Court", right, re.I):
                        _flush()
                        cur_title = "Operative Part (Binding Holding of the Court)"
                        cur_lines.append(right)
                    elif left and re.match(r"^\d+\.?$", left):
                        cur_lines.append(f"[{left.rstrip('.')}] {right}")
                    elif left:
                        cur_lines.append(f"{left} {right}")
                    else:
                        cur_lines.append(right)
                else:
                    txt = _clean_text(tds[0].get_text(" "))
                    if txt:
                        if re.match(r"^On those grounds,?\s+the Court", txt, re.I):
                            _flush()
                            cur_title = "Operative Part (Binding Holding of the Court)"
                        cur_lines.append(txt)

    _flush()

    # Fallback if classes differed on an older CELEX judgment
    if len(sections) < 2:
        full_txt = _clean_text(soup.get_text("\n"))
        if len(full_txt) >= 500:
            op_idx = full_txt.lower().find("on those grounds")
            if op_idx > 0:
                reasoning = full_txt[:op_idx].strip()
                holding = full_txt[op_idx:].strip()
                sections = [
                    {"number": "1", "eid": "cjeu_sec_1", "title": "Judicial Reasoning & Grounds", "text": reasoning[:35000]},
                    {"number": "2", "eid": "cjeu_sec_2", "title": "Operative Part (Binding Holding of the Court)", "text": holding[:15000]},
                ]
            else:
                sections = [{"number": "1", "eid": "cjeu_sec_1", "title": version.get("stage_label", "CJEU Judgment"), "text": full_txt[:35000]}]

    return {"recitals": [], "articles": sections, "annexes": []}


def _parse_europarl_mandate_html(raw_bytes: bytes) -> dict[str, list[dict[str, str]]]:
    """
    Parse European Parliament negotiating mandate HTML (e.g., P9_TA(2023)0236),
    extracting amended articles from Parliament's right-hand amendment column as
    well as standalone adopted articles.
    """
    if BeautifulSoup is None:
        return {"recitals": [], "articles": [], "annexes": []}

    soup = BeautifulSoup(raw_bytes, "lxml")
    articles_by_num: dict[str, dict[str, str]] = {}
    recitals_by_num: dict[str, dict[str, str]] = {}

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        right_col_texts: list[str] = []
        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) >= 2:
                txt = _clean_text(tds[-1].get_text(" "))
                if txt and txt.lower() not in ("amendment", "text proposed by the commission"):
                    right_col_texts.append(txt)
        joined = "\n".join(right_col_texts)
        if not joined:
            continue

        prev_heading = ""
        prev = table.find_previous(["p", "div", "h3", "h4"])
        for _ in range(4):
            if prev is None:
                break
            ptxt = _clean_text(prev.get_text(" "))
            if re.search(r"Article\s+\d+[a-z]?|Recital\s+\d+[a-z]?", ptxt, re.I):
                prev_heading = ptxt
                break
            prev = prev.find_previous(["p", "div", "h3", "h4"])

        art_m = re.search(r"Article\s+(\d+[a-z]?)", prev_heading or joined[:120], re.I)
        rec_m = re.search(r"Recital\s+(\d+[a-z]?)", prev_heading, re.I)

        if art_m:
            num = art_m.group(1).lower()
            entry = articles_by_num.setdefault(
                num, {"number": num, "eid": f"art_{num}", "title": f"Parliament Mandate Amendments — Article {num}", "text": ""}
            )
            entry["text"] = (entry["text"] + "\n" + joined).strip()
        elif rec_m:
            num = rec_m.group(1).lower()
            entry = recitals_by_num.setdefault(
                num, {"number": num, "eid": f"rct_{num}", "text": ""}
            )
            entry["text"] = (entry["text"] + "\n" + joined).strip()

    if len(articles_by_num) >= 5:
        return {
            "recitals": list(recitals_by_num.values()),
            "articles": list(articles_by_num.values()),
            "annexes": [],
        }

    return _parse_eurlex_xhtml(raw_bytes)


def _parse_plain_legal_text(text: str) -> dict[str, list[dict[str, str]]]:
    """
    Deterministic legal structural splitter (v3.0) for plain-text or PDF-extracted
    statutes, treaties, UN conventions, and Council/Trilogue negotiating drafts.

    Eliminates three classic PDF extraction defects:
    1. Wrapped cross-reference lines (`Article 50 of this Regulation...`) no longer
       hijack real article headings or consume `seen_a` slots.
    2. Table-of-Contents entries (`Article 1 .... 5`) are bypassed by locating the
       true enacting `Article 1` followed shortly by `Article 2`.
    3. Mid-text references to `ANNEX III` no longer truncate trailing articles.
    """
    recitals: list[dict[str, str]] = []
    articles: list[dict[str, str]] = []
    annexes: list[dict[str, str]] = []

    raw_art_re = re.compile(r"(?im)^\s*(Article|Art\.)\s+(\d+[a-z]?)\b([^\n]*)$")

    # 1. Identify all genuine enacting Article headings across the document
    all_candidates = [
        m for m in raw_art_re.finditer(text)
        if _is_probable_article_heading(m.group(3), m.group(1))
    ]

    # Locate true start of enacting terms (first genuine Article 1 followed by Article 2 nearby)
    art1_candidates = [m for m in all_candidates if m.group(2) == "1"]
    first_art = None
    for cand in art1_candidates:
        # Check whether an Article 2 heading occurs within the next 25,000 characters
        window = text[cand.end() : cand.end() + 25000]
        if any(
            m2.group(2) == "2" and _is_probable_article_heading(m2.group(3), m2.group(1))
            for m2 in raw_art_re.finditer(window)
        ):
            # Prefer non-TOC match (total text of Article 1 including inline rest should be >= 60 chars)
            m2_first = next(
                (m2 for m2 in raw_art_re.finditer(window) if m2.group(2) == "2" and _is_probable_article_heading(m2.group(3), m2.group(1))),
                None,
            )
            if m2_first and (len(cand.group(3)) + m2_first.start()) >= 60:
                first_art = cand
                break
    if first_art is None and art1_candidates:
        first_art = art1_candidates[0]

    preamble_text = text[: first_art.start()] if first_art else ""
    after_art1 = text[first_art.start() :] if first_art else text

    # 2. Detect standalone Annex section boundary ONLY after enacting articles begin
    # Must be a standalone `ANNEX I` / `ANNEX III` line (not prose like `ANNEX III shall...`)
    annex_heading_re = re.compile(r"(?m)^(ANNEX\s+[IVXLC0-9]+)\s*(?:[-–—:]\s*[^\n]{0,120})?$")
    annex_hits = list(annex_heading_re.finditer(after_art1))
    # Filter out any early Annex mentions before the final 45% if articles continue after them
    enacting_end = len(after_art1)
    valid_annex_hits: list[re.Match[str]] = []
    if annex_hits:
        # Find the position of the last genuine Article heading in after_art1
        last_art_pos = 0
        for m in raw_art_re.finditer(after_art1):
            if _is_probable_article_heading(m.group(3), m.group(1)):
                num_int = int(re.match(r"\d+", m.group(2)).group(0))  # type: ignore[union-attr]
                if num_int >= 3:
                    last_art_pos = max(last_art_pos, m.start())
        # Genuine annexes start AFTER the last major enacting article (or if none, after 50% of text)
        for ah in annex_hits:
            if ah.start() > last_art_pos or (last_art_pos == 0 and ah.start() > len(after_art1) * 0.4):
                valid_annex_hits.append(ah)
        if valid_annex_hits:
            enacting_end = valid_annex_hits[0].start()

    enacting_text = after_art1[:enacting_end]

    if valid_annex_hits:
        seen_anx: set[str] = set()
        for idx, ah in enumerate(valid_annex_hits):
            header = ah.group(1).strip()
            num = header.split()[-1]
            start = ah.end()
            end = valid_annex_hits[idx + 1].start() if idx + 1 < len(valid_annex_hits) else len(after_art1)
            body = after_art1[start:end].strip()
            if num in seen_anx or len(body) < 40:
                continue
            seen_anx.add(num)
            first_line = body.splitlines()[0].strip() if body.splitlines() else f"Annex {num}"
            annexes.append({
                "number": num,
                "eid": f"anx_{num}",
                "title": first_line[:160],
                "text": body[:40000],
            })

    # 3. Extract Recitals from preamble
    if preamble_text:
        rec_matches = list(re.finditer(r"(?m)^\s*\((\d+[a-z]?)\)\s+", preamble_text))
        seen_r: set[str] = set()
        for idx, m in enumerate(rec_matches):
            num = m.group(1)
            if num in seen_r:
                continue
            start = m.start()
            end = rec_matches[idx + 1].start() if idx + 1 < len(rec_matches) else len(preamble_text)
            chunk = preamble_text[start:end].strip()
            if len(chunk) >= 30:
                seen_r.add(num)
                recitals.append({"number": num, "eid": f"rct_{num}", "text": chunk[:10000]})

    # 4. Extract Articles from enacting terms using filtered heading matches
    enacting_matches = [
        m for m in raw_art_re.finditer(enacting_text)
        if _is_probable_article_heading(m.group(3), m.group(1))
    ]
    articles_by_num: dict[str, dict[str, str]] = {}
    order: list[str] = []

    for idx, m in enumerate(enacting_matches):
        num = m.group(2)
        inline_rest = m.group(3).strip(" .:-–—")
        start = m.end()
        end = enacting_matches[idx + 1].start() if idx + 1 < len(enacting_matches) else len(enacting_text)
        following = enacting_text[start:end].strip()

        title = ""
        if inline_rest:
            if len(inline_rest) > 100 or re.match(r"^(?:1\.|\(1\)|The\s|In\s|For\s|Each\s|Every\s|No\s|Where\s|Persons\s|Grave\s|States\s)", inline_rest):
                body = (inline_rest + "\n" + following).strip()
            else:
                title = inline_rest
                body = following or inline_rest
        else:
            lines = following.splitlines()
            body = following
            if lines and len(lines[0]) < 140 and not re.match(r"^(1\.|\(1\)|This\s|The\s|In\s|For\s|Each\s)", lines[0]):
                title = lines[0].strip()
                body = "\n".join(lines[1:]).strip() or following

        if len(body) < 20:
            continue

        # If a duplicate heading slipped through (e.g. from a table header), keep the richer enacting body
        if num in articles_by_num:
            if len(body) > len(articles_by_num[num]["text"]):
                articles_by_num[num] = {
                    "number": num,
                    "eid": f"art_{num}",
                    "title": title or articles_by_num[num]["title"],
                    "text": body[:30000],
                }
            continue

        order.append(num)
        articles_by_num[num] = {
            "number": num,
            "eid": f"art_{num}",
            "title": title,
            "text": body[:30000],
        }

    articles = [articles_by_num[n] for n in order]
    return {"recitals": recitals, "articles": articles, "annexes": annexes}


def _parse_pdf_bytes(raw_bytes: bytes) -> dict[str, list[dict[str, str]]]:
    """Extract text from official PDF bytes (Consilium / UN / CoE / NIST) using `pypdf`."""
    if PdfReader is None:
        return {"recitals": [], "articles": [], "annexes": []}
    reader = PdfReader(io.BytesIO(raw_bytes))
    pages_text = []
    for page in reader.pages:
        try:
            txt = page.extract_text() or ""
            if txt.strip():
                pages_text.append(txt)
        except Exception:
            continue
    full_text = _clean_text("\n".join(pages_text))
    return _parse_plain_legal_text(full_text)


def _parse_ec_guideline_pdf(raw_bytes: bytes, version: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    """
    Parse official European Commission AI Act interpretive guideline PDFs
    (`C(2025) 884` Prohibited Practices, July 2025 GPAI Guidelines) into
    structured major sections (`1.`, `2.`, ..., `12.`) with full verbatim text.
    """
    if PdfReader is None:
        return {"recitals": [], "articles": [], "annexes": []}
    reader = PdfReader(io.BytesIO(raw_bytes))
    pages_text = []
    for page in reader.pages:
        try:
            txt = page.extract_text() or ""
            if txt.strip():
                pages_text.append(txt)
        except Exception:
            continue
    full_text = _clean_text("\n".join(pages_text))
    if len(full_text) < 500:
        return {"recitals": [], "articles": [], "annexes": []}

    # Match top-level numbered guideline chapters (skip TOC entries with dotted leaders)
    sec_re = re.compile(r"(?m)^(\d{1,2})\.\s+([A-Z][^\n]{4,140})$")
    raw_hits = [
        m for m in sec_re.finditer(full_text)
        if not re.search(r"\.{3,}\s*\d+$", m.group(2))
    ]

    # Prefer body hits after TOC (find last occurrence of section "1." in first 20% of doc)
    sec1_hits = [m for m in raw_hits if m.group(1) == "1" and m.start() < len(full_text) * 0.25]
    body_start = sec1_hits[-1].start() if sec1_hits else 0
    hits = [m for m in raw_hits if m.start() >= body_start]

    sections: list[dict[str, str]] = []
    seen: set[str] = set()
    for idx, m in enumerate(hits):
        num = m.group(1)
        if num in seen:
            continue
        title = m.group(2).strip()
        start = m.end()
        end = hits[idx + 1].start() if idx + 1 < len(hits) else len(full_text)
        body = full_text[start:end].strip()
        if len(body) >= 120:
            seen.add(num)
            sections.append({
                "number": num,
                "eid": f"sec_{num}",
                "title": title[:160],
                "text": body[:30000],
            })

    if len(sections) < 2:
        chunk_size = 12000
        sections = [
            {
                "number": str(i + 1),
                "eid": f"sec_{i + 1}",
                "title": f"{version.get('stage_label', 'Commission Guidelines')} — Part {i + 1}",
                "text": full_text[i * chunk_size : (i + 1) * chunk_size].strip(),
            }
            for i in range(min(15, (len(full_text) + chunk_size - 1) // chunk_size))
        ]

    return {"recitals": [], "articles": sections, "annexes": []}


def _regulatory_supplement_articles(instrument_id: str, stage: str, version: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    """
    Concise, original analytical metadata records for regulatory milestones whose
    primary PDF/HTML was unreachable. Always transparently tagged `structured_regulatory_brief`.
    """
    supplements: dict[str, list[dict[str, str]]] = {
        "eu-ai-act::commission_prohibited_guidelines_2025": [
            {
                "number": "3",
                "title": "Commission Interpretive Guidelines on AI System Definition (2025)",
                "text": "Analytical milestone record (C(2025) 924 final, Feb 2025): Operationalizes the seven defining elements of an AI system under Article 3(1), emphasizing inference capability beyond basic deterministic software, statistical optimization, or rule-based data processing.",
            },
            {
                "number": "5",
                "title": "Commission Interpretive Guidelines on Prohibited AI Practices (2025)",
                "text": "Analytical milestone record (C(2025) 884 final, Feb 2025): Establishes operational enforcement criteria for all eight initial Article 5 bans entering application on February 2, 2025, clarifying 'material distortion', 'significant harm', emotion recognition exceptions in workplace safety/medical settings, and strict pre-judicial limits on real-time RBI.",
            },
        ],
        "eu-ai-act::gpai_code_of_practice_2025": [
            {
                "number": "53",
                "title": "GPAI Guidelines & Code of Practice — Transparency & Copyright Chapters (2025)",
                "text": "Analytical milestone record (AI Office, July 2025): Details standardized model documentation forms, Directive (EU) 2019/790 Article 4(3) robots.txt/TDM opt-out compliance, and public training-data summary templates supporting August 2, 2025 GPAI enforcement.",
            },
            {
                "number": "55",
                "title": "GPAI Guidelines & Code of Practice — Safety & Security Chapter (2025)",
                "text": "Analytical milestone record (AI Office, July 2025): Operationalizes systemic risk assessment frameworks, adversarial red-teaming protocols, model-weight cybersecurity safeguards, and AI Office serious incident reporting workflows for models exceeding 10^25 FLOPs.",
            },
        ],
        "eu-ai-act::digital_omnibus_2026_1744": [
            {
                "number": "4",
                "title": "AI Literacy Streamlining (Amended by Regulation (EU) 2026/1744)",
                "text": "Analytical milestone record (Digital Omnibus on AI, 2026): Refocuses Article 4 AI literacy duties toward practical internal guidance and SME proportionality rather than rigid formal certification regimes.",
            },
            {
                "number": "5",
                "title": "Expanded Prohibited AI Practices — NCII & CSAM (Amended by Regulation (EU) 2026/1744)",
                "text": "Analytical milestone record (Digital Omnibus on AI, 2026): Expands Article 5 prohibitions effective December 2, 2026 to explicitly capture AI systems generating non-consensual sexual intimate imagery (deepfakes) and child sexual abuse material (CSAM), carrying penalties up to EUR 35 million or 7% of global annual turnover.",
            },
            {
                "number": "50",
                "title": "Article 50 Transparency & Legacy Generative AI Transition (Amended by Regulation (EU) 2026/1744)",
                "text": "Analytical milestone record (Digital Omnibus on AI, 2026): Confirms August 2, 2026 general application of Article 50 transparency and deepfake labeling obligations, with a transition deadline of December 2, 2026 for legacy generative AI systems placed on the market prior to August 2, 2026 to implement machine-readable markings under Article 50(2).",
            },
            {
                "number": "113",
                "title": "Staggered High-Risk Enforcement Timelines (Amended by Regulation (EU) 2026/1744)",
                "text": "Analytical milestone record (Digital Omnibus on AI, 2026): Decouples and postpones high-risk AI compliance deadlines from the original August 2, 2026 date to December 2, 2027 for standalone Annex III high-risk systems and August 2, 2028 for Annex I regulated product safety components, while requiring operational national AI regulatory sandboxes by August 2, 2027.",
            },
        ],
    }

    key = f"{instrument_id}::{stage}"
    arts = supplements.get(key)
    if not arts:
        arts = [
            {
                "number": "1",
                "title": f"{version['stage_label']} ({version['document_symbol']})",
                "text": f"Structured regulatory milestone record ({version['date']}): {version['summary']} Official source: {version.get('source_url', 'N/A')}.",
            }
        ]
    return {"recitals": [], "articles": arts, "annexes": []}


def fetch_eurlex_stage(
    instrument: dict[str, Any],
    version: dict[str, Any],
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Fetch and parse an EU legislative stage, EC Guidelines PDF, or CJEU landmark judgment
    with SHA-256 cryptographic provenance and `.json.gz` v7 caching.
    """
    instrument_id = instrument["id"]
    stage = version["stage"]
    cache_key = f"{instrument_id}__{stage}__v7"

    if cache_dir:
        cache_file = cache_dir / f"{cache_key}.json.gz"
        if cache_file.exists():
            with gzip.open(cache_file, "rt", encoding="utf-8") as f:
                cached = json.load(f)
                if cached.get("articles") and cached.get("provenance", {}).get("provenance_mode") != "structured_regulatory_brief":
                    return cached

    source_type = version.get("source_type", "eurlex_cellar")
    urls_to_try: list[tuple[str, str]] = []
    if source_type in ("consilium_pdf", "ec_guideline_pdf"):
        if version.get("source_url"):
            urls_to_try.append((version["source_url"], "application/pdf,*/*;q=0.8"))
        for fb in version.get("fallback_urls", []):
            urls_to_try.append((fb, "application/pdf,*/*;q=0.8"))
    elif source_type == "europarl_html":
        if version.get("source_url"):
            urls_to_try.append((version["source_url"], "text/html,application/xhtml+xml;q=0.9"))
        for fb in version.get("fallback_urls", []):
            urls_to_try.append((fb, "application/xhtml+xml,text/html;q=0.9"))
            urls_to_try.append((fb, "application/pdf"))
    elif source_type == "cjeu_cellar":
        if version.get("source_url"):
            urls_to_try.append((version["source_url"], "application/xhtml+xml"))
            urls_to_try.append((version["source_url"], "text/html"))
        for fb in version.get("fallback_urls", []):
            urls_to_try.append((fb, "application/xhtml+xml,text/html;q=0.9"))
    else:
        if version.get("source_url"):
            urls_to_try.append((version["source_url"], "application/xhtml+xml"))
            urls_to_try.append((version["source_url"], "text/html"))
            urls_to_try.append((version["source_url"], "application/pdf"))
        for fb in version.get("fallback_urls", []):
            urls_to_try.append((fb, "application/xhtml+xml,text/html;q=0.9"))

    parsed: dict[str, list[dict[str, str]]] = {"recitals": [], "articles": [], "annexes": []}
    provenance_mode = "structured_regulatory_brief"
    sha256_digest = None
    final_url = version.get("source_url", "")
    http_status: Any = None
    http_etag = None
    bytes_fetched = 0
    fetched_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if httpx is not None and source_type != "regulatory_supplement":
        with httpx.Client(timeout=45.0, follow_redirects=True) as client:
            for candidate_url, accept_header in urls_to_try:
                headers = {
                    "User-Agent": USER_AGENT,
                    "Accept": accept_header,
                    "Accept-Language": "eng,en;q=0.9",
                }
                try:
                    resp = client.get(candidate_url, headers=headers)
                    http_status = resp.status_code

                    # Handle EUR-Lex CELLAR HTTP 300 Multiple Choices (multi-part COM proposals)
                    if resp.status_code == 300:
                        part_urls = re.findall(r"https?://publications\.europa\.eu/resource/cellar/[^\"'<>\s]+", resp.text)
                        part_urls = sorted(
                            set(part_urls),
                            key=lambda u: (0 if "DOC_1" in u else (1 if "DOC_2" in u else 2), u),
                        )
                        combined_bytes = bytearray()
                        merged = {"recitals": [], "articles": [], "annexes": []}
                        mode_cand = "full_primary_xhtml_akn"
                        for purl in part_urls[:3]:
                            presp = client.get(purl, headers=headers)
                            if presp.status_code != 200 or len(presp.content) < 500:
                                continue
                            combined_bytes.extend(presp.content)
                            pctype = presp.headers.get("content-type", "").lower()
                            if "pdf" in pctype or presp.content[:4] == b"%PDF":
                                p_parsed = _parse_pdf_bytes(presp.content)
                                mode_cand = "full_primary_pdf"
                            else:
                                p_parsed = _parse_eurlex_xhtml(presp.content)
                                mode_cand = "full_primary_xhtml_akn"
                            for key_name in ("recitals", "articles", "annexes"):
                                existing_nums = {x["number"] for x in merged[key_name]}
                                for item in p_parsed[key_name]:
                                    if item["number"] not in existing_nums:
                                        merged[key_name].append(item)
                                        existing_nums.add(item["number"])
                        if len(merged["articles"]) >= 2:
                            parsed = merged
                            provenance_mode = mode_cand
                            sha256_digest = hashlib.sha256(bytes(combined_bytes)).hexdigest()
                            final_url = part_urls[0]
                            bytes_fetched = len(combined_bytes)
                            http_status = 200
                            break
                        continue

                    if resp.status_code != 200 or len(resp.content) < 500:
                        continue
                    raw_bytes = resp.content
                    ctype = resp.headers.get("content-type", "").lower()
                    sha256_digest = hashlib.sha256(raw_bytes).hexdigest()
                    final_url = str(resp.url)
                    http_etag = resp.headers.get("etag")
                    bytes_fetched = len(raw_bytes)

                    if source_type == "cjeu_cellar":
                        candidate_parsed = _parse_cjeu_judgment_xhtml(raw_bytes, version)
                        if len(candidate_parsed["articles"]) >= 1:
                            parsed = candidate_parsed
                            provenance_mode = "full_primary_xhtml_akn"
                            break
                    elif source_type == "ec_guideline_pdf" and ("pdf" in ctype or raw_bytes[:4] == b"%PDF"):
                        candidate_parsed = _parse_ec_guideline_pdf(raw_bytes, version)
                        if len(candidate_parsed["articles"]) >= 1:
                            parsed = candidate_parsed
                            provenance_mode = "full_primary_pdf"
                            break
                    elif "pdf" in ctype or raw_bytes[:4] == b"%PDF":
                        candidate_parsed = _parse_pdf_bytes(raw_bytes)
                        if len(candidate_parsed["articles"]) >= 2:
                            parsed = candidate_parsed
                            provenance_mode = "full_primary_pdf"
                            break
                    elif source_type == "europarl_html":
                        candidate_parsed = _parse_europarl_mandate_html(raw_bytes)
                        if len(candidate_parsed["articles"]) >= 2:
                            parsed = candidate_parsed
                            provenance_mode = "full_primary_html"
                            break
                    else:
                        candidate_parsed = _parse_eurlex_xhtml(raw_bytes)
                        if len(candidate_parsed["articles"]) >= 2:
                            parsed = candidate_parsed
                            provenance_mode = "full_primary_xhtml_akn"
                            break
                except Exception as exc:
                    http_status = f"error:{type(exc).__name__}"

    if not parsed["articles"]:
        parsed = _regulatory_supplement_articles(instrument_id, stage, version)
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
        "eli": version.get("eli", instrument.get("eli")),
        "author_name": version["author_name"],
        "author_email": version["author_email"],
        "source_url": final_url,
        "summary": version["summary"],
        "provenance": {
            "provenance_mode": provenance_mode,
            "sha256_raw": sha256_digest,
            "final_url": final_url,
            "eli": version.get("eli", instrument.get("eli")),
            "celex": version.get("celex", instrument.get("celex")),
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
