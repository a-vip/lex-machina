"""
BM25 Inverted Search Index with UK/US Legal Spelling Normalization (`src/parser/bm25_index.py`).

Solves the critical cross-dialect recall failure in international legal search:
EU/UN/ICRC texts use British spelling (`categorisation`, `harmonised`, `defence`,
`offence`, `authorisation`, `behaviour`), whereas US attorneys query American
spelling (`categorization`, `harmonized`, `defense`, `offense`, `authorization`,
`behavior`). Also expands domain acronyms (`FRIA`, `RBI`, `GPAI`, `LAWS`, `CRA`,
`DPIA`, `DORA`, `NIS2`, `TRAIGA`).
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

STOPWORDS = frozenset({
    "the", "and", "for", "that", "with", "this", "from", "are", "was", "were",
    "shall", "may", "not", "any", "such", "under", "into", "their", "which",
    "have", "has", "been", "other", "more", "than", "also", "all", "its",
    "where", "when", "who", "they", "them", "these", "those", "within",
})

# Canonicalize UK <-> US spelling variants to a single index stem
SPELLING_NORMALIZATION: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"isation\b"), "ization"),
    (re.compile(r"isations\b"), "izations"),
    (re.compile(r"ised\b"), "ized"),
    (re.compile(r"ising\b"), "izing"),
    (re.compile(r"ise\b"), "ize"),
    (re.compile(r"ises\b"), "izes"),
    (re.compile(r"\bdefence\b"), "defense"),
    (re.compile(r"\boffence\b"), "offense"),
    (re.compile(r"\boffences\b"), "offenses"),
    (re.compile(r"\bbehaviour\b"), "behavior"),
    (re.compile(r"\bbehaviours\b"), "behaviors"),
    (re.compile(r"\bbehavioural\b"), "behavioral"),
    (re.compile(r"\blicence\b"), "license"),
    (re.compile(r"\blicences\b"), "licenses"),
    (re.compile(r"\bprogramme\b"), "program"),
    (re.compile(r"\bprogrammes\b"), "programs"),
    (re.compile(r"\bcentre\b"), "center"),
    (re.compile(r"\bcolour\b"), "color"),
    (re.compile(r"\blabelling\b"), "labeling"),
    (re.compile(r"\blabelled\b"), "labeled"),
    (re.compile(r"\bmodelling\b"), "modeling"),
    (re.compile(r"\bfulfil\b"), "fulfill"),
    (re.compile(r"\bjudgement\b"), "judgment"),
]

LEGAL_SYNONYMS: dict[str, list[str]] = {
    "fria": ["fundamental", "rights", "impact", "assessment"],
    "dpia": ["data", "protection", "impact", "assessment"],
    "rbi": ["remote", "biometric", "identification"],
    "gpai": ["general", "purpose", "model"],
    "laws": ["lethal", "autonomous", "weapons"],
    "cra": ["cyber", "resilience", "digital", "elements"],
    "nis2": ["network", "information", "security", "directive"],
    "dora": ["digital", "operational", "resilience", "financial"],
    "traiga": ["texas", "responsible", "governance"],
    "omnibus": ["2026", "1744", "postponed", "december", "2027"],
    "ihl": ["humanitarian", "geneva", "protocol", "armed", "conflict"],
    "schufa": ["automated", "decision", "scoring", "article", "22", "634"],
    "schrems": ["transfer", "adequacy", "surveillance", "standard", "contractual"],
    "cjeu": ["court", "justice", "preliminary", "ruling", "operative"],
    "icj": ["international", "court", "justice", "martens", "intransgressible"],
    "duaa": ["data", "use", "access", "2025", "automated"],
    "imda": ["singapore", "agentic", "governance", "framework"],
    "iso42001": ["42001", "management", "system", "aims"],
}


def tokenize_legal_text(text: str, expand_synonyms: bool = False) -> list[str]:
    """Tokenize and UK/US-normalize legal text into clean BM25 terms."""
    lower = text.lower()
    raw_tokens = re.findall(r"[a-z0-9]{2,}", lower)
    out: list[str] = []
    for tok in raw_tokens:
        if tok in STOPWORDS:
            continue
        norm = tok
        for pattern, repl in SPELLING_NORMALIZATION:
            norm = pattern.sub(repl, norm)
        out.append(norm)
        if expand_synonyms and norm in LEGAL_SYNONYMS:
            out.extend(LEGAL_SYNONYMS[norm])
    return out


def build_bm25_index(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Build a compact inverted BM25 index (`k1=1.5, b=0.75`) over all corpus
    provisions for sub-50ms edge retrieval in Cloudflare Workers and FastMCP.
    """
    docs_meta: list[dict[str, Any]] = []
    postings: dict[str, list[list[int]]] = {}  # term -> [[doc_id, tf], ...]
    doc_lengths: list[int] = []

    for doc_id, entry in enumerate(entries):
        combined = f"{entry.get('heading', '')} {entry.get('instrument_title', '')} {entry.get('text', '')}"
        tokens = tokenize_legal_text(combined, expand_synonyms=False)
        doc_len = len(tokens)
        doc_lengths.append(doc_len)

        tf = Counter(tokens)
        for term, freq in tf.items():
            postings.setdefault(term, []).append([doc_id, freq])

        docs_meta.append({
            "id": doc_id,
            "instrument_path": entry["instrument_path"],
            "instrument_title": entry["instrument_title"],
            "jurisdiction": entry["jurisdiction"],
            "provision": entry["provision"],
            "heading": entry["heading"],
            "latest_stage": entry["latest_stage"],
            "latest_date": entry["latest_date"],
            "latest_author": entry["latest_author"],
            "provenance_mode": entry.get("provenance_mode", "unknown"),
            "dl": doc_len,
            "snippet": entry.get("text", "")[:380],
        })

    n_docs = len(docs_meta)
    avgdl = (sum(doc_lengths) / n_docs) if n_docs else 1.0

    # Precompute IDF per term
    idf: dict[str, float] = {}
    for term, plist in postings.items():
        df = len(plist)
        idf[term] = round(math.log(((n_docs - df + 0.5) / (df + 0.5)) + 1.0), 4)

    return {
        "schema_version": "2.0.0",
        "algorithm": "BM25(k1=1.5,b=0.75)+UK_US_Norm",
        "doc_count": n_docs,
        "avgdl": round(avgdl, 2),
        "docs": docs_meta,
        "idf": idf,
        "postings": postings,
    }
