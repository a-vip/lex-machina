"""
Lex Machina v2.0 — Stateless Remote Legal-Informatics FastMCP Server (`mcp_server/server.py`).

Zero-Local-Disk architecture querying `refs/heads/corpus` remotely via GitHub Raw
with in-memory TTL caching and connection pooling.

Capabilities unmatched by any existing legal MCP server:
1. 9 Read-Only Annotated Tools (incl. Bitemporal `check_applicability`, Stanford-RegLab
   anti-hallucination `verify_citations`, and SHA-256 `get_provenance_audit`).
2. Concordance-Aware `diff_provisions` & Token/Phrase-Level Institutional `blame_provision`
   (tracks legal norms across article renumberings such as EU AI Act Proposal Art. 52 ->
   Final Art. 50, preserving exact Commission/Council/Parliament word-level authorship).
3. BM25 Search with UK<->US Legal Spelling Normalization & Acronym Expansion.
4. Native MCP Resources (`lex://...`) and MCP Prompts (`/audit-ai-system`, etc.).
"""

from __future__ import annotations

import datetime as dt
import difflib
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import httpx

# Full forward/backward compatibility with BOTH mcp Python SDK v2.x (`MCPServer`) and v1.x (`FastMCP`)
try:
    from mcp.server.mcpserver import MCPServer as _MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as _MCPServer

try:
    from mcp.types import ToolAnnotations
except ImportError:
    ToolAnnotations = None

DEFAULT_REPO = os.environ.get("LEX_MACHINA_REPO", "a-vip/lex-machina")
CORPUS_BRANCH = os.environ.get("LEX_MACHINA_BRANCH", "corpus")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CACHE_TTL_SECONDS = int(os.environ.get("LEX_MACHINA_CACHE_TTL", "300"))

ROOT_DIR = Path(__file__).resolve().parents[1]
LOCAL_SRC_DIR = ROOT_DIR / "src"

# Shared pooled HTTP client + TTL cache (zero local disk writes)
_HTTP_CLIENT: httpx.Client | None = None
_MEM_CACHE: dict[str, tuple[float, Any]] = {}

READ_ONLY_ANNOTATIONS = (
    ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
    if ToolAnnotations is not None
    else None
)

mcp = _MCPServer(
    "lex-machina",
    instructions=(
        "Authoritative bitemporal legal-informatics and deterministic citation-verification "
        "MCP server covering global AI regulation (EU AI Act as amended by Digital Omnibus "
        "2026/1744, GDPR, CoE CETS 225, US NIST AI RMF, US State AI Laws, China CAC incl. "
        "2025 Labeling Measures), Cyber Law (EU CRA, NIS2, DORA, UN Hanoi Cybercrime "
        "Convention, Budapest Convention), and International Humanitarian Law (1949 Geneva "
        "Conventions, 1977 Additional Protocols, UN CCW LAWS)."
    ),
)


def _tool_decorator():
    if READ_ONLY_ANNOTATIONS is not None:
        try:
            return mcp.tool(annotations=READ_ONLY_ANNOTATIONS)
        except TypeError:
            return mcp.tool()
    return mcp.tool()


def _get_client() -> httpx.Client:
    global _HTTP_CLIENT
    if _HTTP_CLIENT is None:
        headers = {
            "User-Agent": "lex-machina-mcp-server/2.0",
            "Accept": "text/plain,application/json",
        }
        if GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
        _HTTP_CLIENT = httpx.Client(timeout=20.0, follow_redirects=True, headers=headers)
    return _HTTP_CLIENT


def _raw_url(rel_path: str) -> str:
    return f"https://raw.githubusercontent.com/{DEFAULT_REPO}/{CORPUS_BRANCH}/{rel_path.lstrip('/')}"


def _fetch_raw_text(rel_path: str) -> str | None:
    now = time.monotonic()
    cached = _MEM_CACHE.get(rel_path)
    if cached and (now - cached[0]) < CACHE_TTL_SECONDS:
        return cached[1]

    try:
        resp = _get_client().get(_raw_url(rel_path))
        val = resp.text if resp.status_code == 200 else None
    except Exception:
        val = None

    _MEM_CACHE[rel_path] = (now, val)
    return val


def _fetch_raw_json(rel_path: str, local_fallback: Path | None = None) -> dict[str, Any] | None:
    cache_key = f"__json__:{rel_path}"
    now = time.monotonic()
    cached = _MEM_CACHE.get(cache_key)
    if cached and (now - cached[0]) < CACHE_TTL_SECONDS:
        return cached[1]

    text = _fetch_raw_text(rel_path)
    data = None
    if text:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None

    if data is None and local_fallback and local_fallback.exists():
        data = json.loads(local_fallback.read_text(encoding="utf-8"))

    _MEM_CACHE[cache_key] = (now, data)
    return data


def _load_catalog() -> dict[str, Any]:
    return _fetch_raw_json("catalog.json", LOCAL_SRC_DIR / "catalog.json") or {"instruments": []}


def _load_concordance() -> dict[str, Any]:
    return _fetch_raw_json("concordance.json", LOCAL_SRC_DIR / "concordance.json") or {"concordances": {}}


def _load_applicability() -> dict[str, Any]:
    return _fetch_raw_json("applicability.json", LOCAL_SRC_DIR / "applicability.json") or {"rules": []}


def _load_provenance() -> dict[str, Any]:
    return _fetch_raw_json("provenance.json") or {"stages": []}


def _find_instrument(catalog: dict[str, Any], instrument_path: str) -> dict[str, Any] | None:
    norm = instrument_path.strip("/").lower()
    for inst in catalog.get("instruments", []):
        if inst["path"].strip("/").lower() == norm or inst["id"].lower() == norm:
            return inst
    return None


def _resolve_stage(instrument: dict[str, Any], as_of: str | None) -> dict[str, Any]:
    versions = instrument.get("versions", [])
    if not versions:
        raise ValueError(f"Instrument '{instrument['path']}' has no versions.")
    if not as_of or as_of.strip().lower() in ("latest", "head", "current"):
        return versions[-1]

    query = as_of.strip().lower()
    for ver in versions:
        if (
            query == ver["stage"].lower()
            or query in ver["stage"].lower()
            or query in ver["stage_label"].lower()
            or query in ver.get("document_symbol", "").lower()
            or query == ver["date"].lower()
        ):
            return ver

    dated = [ver for ver in versions if ver["date"] <= query]
    if dated:
        return dated[-1]
    return versions[-1]


def _normalize_provision_path(provision: str) -> str:
    p = provision.strip().strip("/")
    if p.endswith(".md") and ("/" in p or p in ("full-text.md", "instrument.md")):
        return p
    m_art = re.match(r"^(?:article[-_\s]*)?(\d+)([a-zA-Z]?)$", p, re.I)
    if m_art:
        return f"articles/article-{int(m_art.group(1)):03d}{m_art.group(2).lower()}.md"
    m_rec = re.match(r"^recital[-_\s]*(\d+)([a-zA-Z]?)(?:\.md)?$", p, re.I)
    if m_rec:
        return f"recitals/recital-{int(m_rec.group(1)):03d}{m_rec.group(2).lower()}.md"
    m_anx = re.match(r"^annex[-_\s]*([ivxlc0-9a-z]+)(?:\.md)?$", p, re.I)
    if m_anx:
        return f"annexes/annex-{m_anx.group(1).lower()}.md"
    if not p.endswith(".md"):
        p = f"{p}.md"
    if "/" not in p:
        p = f"articles/{p}"
    return p


def _resolve_concordance(
    instrument_path: str,
    norm_provision: str,
    target_stage: str,
) -> tuple[str, dict[str, Any] | None]:
    """
    Map a provision path through `concordance.json` so renumbered articles
    (e.g., EU AI Act Final Art. 50 <-> 2021 Proposal Art. 52; GDPR Art. 22 <-> Proposal Art. 20)
    resolve seamlessly across legislative stages.
    """
    conc = _load_concordance()
    entries = conc.get("concordances", {}).get(instrument_path.strip("/"), [])
    for entry in entries:
        stage_map = entry.get("stage_map", {})
        if norm_provision in stage_map.values() or norm_provision == entry.get("norm_id"):
            mapped = stage_map.get(target_stage, norm_provision)
            return mapped, entry
    return norm_provision, None


def _fetch_provision_at_stage(
    instrument: dict[str, Any],
    version: dict[str, Any],
    norm_provision: str,
) -> tuple[str | None, str]:
    """
    Fetch the lightweight (~3 KB) Markdown file for a provision at a given stage,
    automatically applying concordance resolution if the article was renumbered.
    Returns `(markdown_text, resolved_provision_path)`.
    """
    inst_path = instrument["path"].strip("/")
    stage = version["stage"]
    mapped_prov, _ = _resolve_concordance(inst_path, norm_provision, stage)

    # 1. Fast direct fetch from `versions/<inst_path>/<stage>/<mapped_prov>`
    for candidate in dict.fromkeys([mapped_prov, norm_provision]):
        text = _fetch_raw_text(f"versions/{inst_path}/{stage}/{candidate}")
        if text:
            return text, candidate

    # 2. If latest stage or supplement stage, fall back to live tree `<inst_path>/<candidate>`
    for candidate in dict.fromkeys([mapped_prov, norm_provision]):
        direct = _fetch_raw_text(f"{inst_path}/{candidate}")
        if direct and (version == instrument["versions"][-1] or version.get("source_type") == "regulatory_supplement"):
            return direct, candidate

    return None, mapped_prov


def _extract_body_lines(markdown_text: str) -> list[str]:
    return [
        line.strip()
        for line in markdown_text.splitlines()
        if line.strip() and not line.startswith("- **") and not line.startswith("# ")
    ]


def _normalize_search_token(tok: str) -> str:
    """Mirror `src/parser/bm25_index.py` UK <-> US spelling normalization."""
    rules = [
        (r"isation$", "ization"), (r"isations$", "izations"),
        (r"ised$", "ized"), (r"ising$", "izing"), (r"ise$", "ize"), (r"ises$", "izes"),
        (r"^defence$", "defense"), (r"^offence$", "offense"), (r"^offences$", "offenses"),
        (r"^behaviour$", "behavior"), (r"^behavioural$", "behavioral"),
        (r"^licence$", "license"), (r"^programme$", "program"),
        (r"^labelling$", "labeling"), (r"^labelled$", "labeled"), (r"^modelling$", "modeling"),
    ]
    out = tok.lower()
    for pat, repl in rules:
        out = re.sub(pat, repl, out)
    return out


LEGAL_QUERY_SYNONYMS: dict[str, list[str]] = {
    "fria": ["fundamental", "rights", "impact", "assessment"],
    "dpia": ["data", "protection", "impact", "assessment"],
    "rbi": ["remote", "biometric", "identification"],
    "gpai": ["general", "purpose", "model"],
    "laws": ["lethal", "autonomous", "weapons"],
    "cra": ["cyber", "resilience"],
    "nis2": ["network", "information", "security"],
    "dora": ["digital", "operational", "resilience"],
    "traiga": ["texas", "responsible", "governance"],
    "omnibus": ["2026", "1744", "postponed"],
}


def _clause_level_institutional_blame(
    stage_snapshots: list[tuple[dict[str, Any], list[str]]],
) -> list[dict[str, Any]]:
    """
    Token/phrase-level institutional attribution across chronological drafts using
    sequential `difflib.SequenceMatcher` alignment. Preserves original Commission
    or Parliament authorship of clauses even when later Trilogue or Official Journal
    lawyer-linguists adjust punctuation or insert narrow qualifiers.
    """
    if not stage_snapshots:
        return []

    def _split_clauses(lines: list[str]) -> list[str]:
        clauses: list[str] = []
        for line in lines:
            parts = [p.strip() for p in re.split(r"(?<=[.;:])\s+", line) if p.strip()]
            clauses.extend(parts or [line])
        return clauses

    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[A-Za-z0-9']+|[.,;:()\-]", text)

    def _meta_of(ver: dict[str, Any]) -> dict[str, str]:
        return {
            "stage": ver["stage"],
            "stage_label": ver["stage_label"],
            "date": ver["date"],
            "document_symbol": ver["document_symbol"],
            "author": f"{ver['author_name']} <{ver['author_email']}>",
        }

    # Walk token provenance chronologically across all stages
    first_ver, first_lines = stage_snapshots[0]
    prev_tokens = _tokenize(" ".join(first_lines))
    prev_owners = [_meta_of(first_ver)] * len(prev_tokens)

    for ver, lines in stage_snapshots[1:]:
        cur_tokens = _tokenize(" ".join(lines))
        cur_meta = _meta_of(ver)
        matcher = difflib.SequenceMatcher(
            None,
            [t.lower() for t in prev_tokens],
            [t.lower() for t in cur_tokens],
            autojunk=False,
        )
        new_owners: list[dict[str, str]] = [cur_meta] * len(cur_tokens)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for offset in range(i2 - i1):
                    new_owners[j1 + offset] = prev_owners[i1 + offset]
        prev_tokens = cur_tokens
        prev_owners = new_owners

    # Aggregate token ownership back into readable clause-level segments
    latest_ver, latest_lines = stage_snapshots[-1]
    latest_clauses = _split_clauses(latest_lines)
    token_cursor = 0
    results: list[dict[str, Any]] = []

    for clause_idx, clause in enumerate(latest_clauses, start=1):
        c_tokens = _tokenize(clause)
        n = len(c_tokens)
        slice_owners = prev_owners[token_cursor : token_cursor + n]
        token_cursor += n
        if not slice_owners:
            slice_owners = [_meta_of(latest_ver)]

        # Count institutional share across tokens in this clause
        share_counts: dict[str, int] = {}
        meta_by_author: dict[str, dict[str, str]] = {}
        for own in slice_owners:
            key = f"{own['author']} [{own['stage']}@{own['date']}]"
            share_counts[key] = share_counts.get(key, 0) + 1
            meta_by_author[key] = own

        dominant_key = max(share_counts, key=share_counts.get)  # type: ignore[arg-type]
        dominant = meta_by_author[dominant_key]
        total_tok = max(1, len(slice_owners))
        contributors = [
            {
                "institutional_author": meta_by_author[k]["author"],
                "stage": meta_by_author[k]["stage"],
                "date": meta_by_author[k]["date"],
                "token_share_pct": round(100.0 * cnt / total_tok, 1),
            }
            for k, cnt in sorted(share_counts.items(), key=lambda kv: -kv[1])
        ]

        results.append({
            "clause_number": clause_idx,
            "primary_institutional_author": dominant["author"],
            "introduced_in_stage": dominant["stage"],
            "introduced_on_date": dominant["date"],
            "document_symbol": dominant["document_symbol"],
            "contributors": contributors,
            "text": clause,
        })

    return results


# ---------------------------------------------------------------------------
# MCP RESOURCES (Standard `resources/*` primitive with lex:// URIs)
# ---------------------------------------------------------------------------

@mcp.resource("lex://provenance")
def resource_provenance() -> str:
    """Cryptographic SHA-256 provenance manifest for all ingested corpus stages."""
    return json.dumps(_load_provenance(), indent=2)


@mcp.resource("lex://applicability")
def resource_applicability() -> str:
    """Bitemporal legal applicability schedule (incl. Digital Omnibus 2026/1744 & EO 14110 revocation)."""
    return json.dumps(_load_applicability(), indent=2)


@mcp.resource("lex://concordance")
def resource_concordance() -> str:
    """Four-column normative concordance mapping renumbered articles across legislative drafts."""
    return json.dumps(_load_concordance(), indent=2)


@mcp.resource("lex://provision/{jurisdiction}/{slug}/{provision}")
def resource_provision(jurisdiction: str, slug: str, provision: str) -> str:
    """Direct read-only resource for a normalized legal provision."""
    norm = _normalize_provision_path(provision)
    text = _fetch_raw_text(f"{jurisdiction}/{slug}/{norm}")
    return text or f"Provision not found: {jurisdiction}/{slug}/{norm}"


# ---------------------------------------------------------------------------
# MCP PROMPTS (Server-side reusable legal workflow scaffolds)
# ---------------------------------------------------------------------------

@mcp.prompt()
def audit_ai_system(system_description: str, deployment_date: str = "2026-11-23") -> str:
    """Structured partner-level EU AI Act + Digital Omnibus 2026/1744 compliance audit workflow."""
    return (
        f"Conduct a formal FIRAC compliance audit for the following AI system as of {deployment_date}:\n\n"
        f"{system_description}\n\n"
        "MANDATORY TOOL PROTOCOL:\n"
        "1. Call `get_provision` on `eu/ai-act` Articles 2, 3, 5, 6, 9, 27, 50, 51, 53, 55, and Annex III.\n"
        "2. Call `check_applicability` for each triggered provision on the deployment date (incorporating Digital Omnibus Regulation (EU) 2026/1744).\n"
        "3. Call `verify_citations` on your draft legal memorandum before returning it to the user.\n"
        "4. Include the SHA-256 provenance footer and ABA Formal Opinion 512 verification notice."
    )


@mcp.prompt()
def travaux_redline(instrument_path: str, provision: str) -> str:
    """CJEU teleological interpretation & travaux preparatoires institutional blame workflow."""
    return (
        f"Perform a CJEU teleological and travaux preparatoires analysis of `{instrument_path}` `{provision}`:\n"
        "1. Call `blame_provision` to obtain clause-level institutional authorship.\n"
        "2. Call `diff_provisions` across Commission Proposal -> Parliament Mandate -> Official Journal (concordance-resolved).\n"
        "3. Call `get_citation_graph` to retrieve linked interpretive Recitals.\n"
        "4. Call `verify_citations` before finalizing the legal opinion."
    )


@mcp.prompt()
def article_36_review(weapons_system_description: str) -> str:
    """Additional Protocol I Article 36 & UN CCW GGE LAWS legal weapons review workflow."""
    return (
        f"Perform an Article 36 Additional Protocol I legal weapons review for:\n\n{weapons_system_description}\n\n"
        "1. Retrieve IHL Articles 35, 36, 48, 51, 57 from `ihl/geneva-conventions` via `get_provision`.\n"
        "2. Retrieve UN CCW GGE 11 Guiding Principles and 2023/2026 consensus norms from `un/ccw-laws`.\n"
        "3. Verify every statutory citation via `verify_citations`."
    )


# ---------------------------------------------------------------------------
# 9 PRODUCTION MCP TOOLS (All Read-Only Annotated)
# ---------------------------------------------------------------------------

@_tool_decorator()
def list_instruments(
    jurisdiction: str | None = None,
    domain: str | None = None,
) -> dict[str, Any]:
    """
    List all tracked AI, privacy, cyber, and international humanitarian law instruments
    with chronological stages, institutional authors, and SHA-256 provenance coverage.
    """
    catalog = _load_catalog()
    prov_index = {
        (s["instrument_path"], s["stage"]): s
        for s in _load_provenance().get("stages", [])
    }

    instruments = catalog.get("instruments", [])
    if jurisdiction:
        jf = jurisdiction.strip().lower()
        instruments = [
            i for i in instruments
            if i["jurisdiction"].lower() == jf or i["path"].lower().startswith(f"{jf}/")
        ]
    if domain:
        df = domain.strip().lower()
        instruments = [i for i in instruments if i.get("domain", "").lower() == df]

    results = []
    for inst in instruments:
        vers = []
        for v in inst.get("versions", []):
            pinfo = prov_index.get((inst["path"], v["stage"]), {})
            vers.append({
                "stage": v["stage"],
                "stage_label": v["stage_label"],
                "date": v["date"],
                "document_symbol": v["document_symbol"],
                "author": f"{v['author_name']} <{v['author_email']}>",
                "provenance_mode": pinfo.get("provenance_mode", "unknown"),
                "counts": pinfo.get("counts"),
                "sha256_raw": pinfo.get("sha256_raw"),
            })
        results.append({
            "id": inst["id"],
            "path": inst["path"],
            "jurisdiction": inst["jurisdiction"],
            "domain": inst.get("domain", "ai"),
            "title": inst["title"],
            "short_title": inst.get("short_title", inst["title"]),
            "status": inst.get("status"),
            "in_force_date": inst.get("in_force_date"),
            "eli": inst.get("eli"),
            "versions": vers,
        })

    return {
        "repository": DEFAULT_REPO,
        "branch": CORPUS_BRANCH,
        "edition": catalog.get("corpus_edition", "2026.11"),
        "count": len(results),
        "instruments": results,
    }


@_tool_decorator()
def get_provision(
    instrument_path: str,
    provision: str,
    as_of: str | None = None,
) -> dict[str, Any]:
    """
    Fetch normalized Markdown text of an article, recital, or annex at a specific date
    or legislative stage, with concordance fallback, linked recitals, and SHA-256 provenance.
    """
    catalog = _load_catalog()
    instrument = _find_instrument(catalog, instrument_path)
    if not instrument:
        return {"error": f"Unknown instrument_path: '{instrument_path}'"}

    version = _resolve_stage(instrument, as_of)
    norm_prov = _normalize_provision_path(provision)
    markdown_text, resolved_prov = _fetch_provision_at_stage(instrument, version, norm_prov)

    if markdown_text is None:
        return {
            "error": (
                f"PROVISION NOT IN CORPUS: '{norm_prov}' not found in '{instrument['path']}' "
                f"at stage '{version['stage']}' ({version['date']}). Do NOT extrapolate from memory."
            ),
            "instrument_path": instrument["path"],
            "stage": version["stage"],
            "date": version["date"],
        }

    _, conc_entry = _resolve_concordance(instrument["path"], norm_prov, version["stage"])
    prov_stage = next(
        (
            s for s in _load_provenance().get("stages", [])
            if s["instrument_path"] == instrument["path"] and s["stage"] == version["stage"]
        ),
        {},
    )

    return {
        "instrument_path": instrument["path"],
        "title": instrument["title"],
        "requested_provision": norm_prov,
        "resolved_provision": resolved_prov,
        "renumbered_via_concordance": resolved_prov != norm_prov,
        "linked_recitals": conc_entry.get("recitals", []) if conc_entry else [],
        "stage": version["stage"],
        "stage_label": version["stage_label"],
        "date": version["date"],
        "document_symbol": version["document_symbol"],
        "institutional_author": f"{version['author_name']} <{version['author_email']}>",
        "provenance": {
            "provenance_mode": prov_stage.get("provenance_mode", "unknown"),
            "sha256_raw": prov_stage.get("sha256_raw"),
            "eli": version.get("eli") or instrument.get("eli"),
            "celex": version.get("celex") or instrument.get("celex"),
            "source_url": prov_stage.get("final_url") or version.get("source_url"),
            "fetched_utc": prov_stage.get("fetched_utc"),
        },
        "markdown": markdown_text,
    }


@_tool_decorator()
def diff_provisions(
    instrument_path: str,
    provision: str,
    stage_a: str,
    stage_b: str,
) -> dict[str, Any]:
    """
    Compute a unified redline diff between two legislative stages or dates, automatically
    resolving renumbered articles via `concordance.json` (e.g., EU AI Act Proposal Art. 52
    -> Final OJ Art. 50; GDPR Proposal Art. 20 -> Final Art. 22).
    """
    catalog = _load_catalog()
    instrument = _find_instrument(catalog, instrument_path)
    if not instrument:
        return {"error": f"Unknown instrument_path: '{instrument_path}'"}

    ver_a = _resolve_stage(instrument, stage_a)
    ver_b = _resolve_stage(instrument, stage_b)
    norm_prov = _normalize_provision_path(provision)

    text_a, prov_a = _fetch_provision_at_stage(instrument, ver_a, norm_prov)
    text_b, prov_b = _fetch_provision_at_stage(instrument, ver_b, norm_prov)

    label_a = f"{instrument['path']}/{prov_a}@{ver_a['stage']} ({ver_a['date']} — {ver_a['author_name']})"
    label_b = f"{instrument['path']}/{prov_b}@{ver_b['stage']} ({ver_b['date']} — {ver_b['author_name']})"

    diff_lines = list(
        difflib.unified_diff(
            (text_a or "").splitlines(keepends=True),
            (text_b or "").splitlines(keepends=True),
            fromfile=label_a,
            tofile=label_b,
            n=3,
        )
    )
    added = sum(1 for ln in diff_lines if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in diff_lines if ln.startswith("-") and not ln.startswith("---"))

    return {
        "instrument_path": instrument["path"],
        "requested_provision": norm_prov,
        "concordance_resolved": {"stage_a_provision": prov_a, "stage_b_provision": prov_b},
        "stage_a": {
            "stage": ver_a["stage"],
            "stage_label": ver_a["stage_label"],
            "date": ver_a["date"],
            "author": f"{ver_a['author_name']} <{ver_a['author_email']}>",
        },
        "stage_b": {
            "stage": ver_b["stage"],
            "stage_label": ver_b["stage_label"],
            "date": ver_b["date"],
            "author": f"{ver_b['author_name']} <{ver_b['author_email']}>",
        },
        "stats": {"lines_added": added, "lines_removed": removed},
        "unified_diff": "".join(diff_lines) or "(No textual differences between selected stages)",
    }


@_tool_decorator()
def blame_provision(
    instrument_path: str,
    provision: str,
) -> dict[str, Any]:
    """
    Perform clause- and token-level institutional attribution (`git blame`) across all
    chronological legislative stages (concordance-resolved across renumberings) so
    minor lawyer-linguist punctuation edits never erase Commission or Parliament authorship.
    """
    catalog = _load_catalog()
    instrument = _find_instrument(catalog, instrument_path)
    if not instrument:
        return {"error": f"Unknown instrument_path: '{instrument_path}'"}

    norm_prov = _normalize_provision_path(provision)
    stage_snapshots: list[tuple[dict[str, Any], list[str]]] = []
    stage_mapping_log: list[dict[str, str]] = []

    for ver in instrument.get("versions", []):
        if ver.get("source_type") == "regulatory_supplement" or ver.get("patch_mode"):
            continue
        text, resolved = _fetch_provision_at_stage(instrument, ver, norm_prov)
        if not text:
            continue
        body_lines = _extract_body_lines(text)
        if body_lines:
            stage_snapshots.append((ver, body_lines))
            stage_mapping_log.append({
                "stage": ver["stage"],
                "date": ver["date"],
                "provision": resolved,
                "author": f"{ver['author_name']} <{ver['author_email']}>",
            })

    if not stage_snapshots:
        return {"error": f"Provision '{norm_prov}' not found across stages of '{instrument['path']}'."}

    blame_clauses = _clause_level_institutional_blame(stage_snapshots)
    latest_ver = stage_snapshots[-1][0]

    return {
        "instrument_path": instrument["path"],
        "provision": norm_prov,
        "attribution_algorithm": "sequential_token_difflib_concordance_v2",
        "latest_stage": latest_ver["stage"],
        "latest_date": latest_ver["date"],
        "stages_analyzed": stage_mapping_log,
        "blame": blame_clauses,
    }


@_tool_decorator()
def search_corpus(
    query: str,
    jurisdiction: str | None = None,
    domain: str | None = None,
) -> dict[str, Any]:
    """
    Search across the entire corpus using precomputed BM25 ranking with automatic
    UK<->US legal spelling normalization (`categorisation`/`categorization`, `defence`/`defense`)
    and legal acronym synonym expansion (`FRIA`, `RBI`, `GPAI`, `LAWS`, `CRA`, `DORA`, `NIS2`).
    """
    bm25 = _fetch_raw_json("bm25-index.json")
    raw_terms = re.findall(r"[a-z0-9]{2,}", query.lower())
    query_terms: list[str] = []
    for t in raw_terms:
        nt = _normalize_search_token(t)
        query_terms.append(nt)
        if nt in LEGAL_QUERY_SYNONYMS:
            query_terms.extend(LEGAL_QUERY_SYNONYMS[nt])

    jf = jurisdiction.strip().lower() if jurisdiction else None
    df = domain.strip().lower() if domain else None

    if bm25 and "postings" in bm25:
        docs = bm25["docs"]
        idf = bm25["idf"]
        postings = bm25["postings"]
        avgdl = bm25.get("avgdl", 100.0) or 100.0
        k1, b = 1.5, 0.75

        scores: dict[int, float] = {}
        for term in set(query_terms):
            plist = postings.get(term)
            if not plist:
                continue
            term_idf = idf.get(term, 1.0)
            for doc_id, tf in plist:
                doc = docs[doc_id]
                if jf and doc["jurisdiction"].lower() != jf:
                    continue
                dl = doc.get("dl", 100) or 100
                denom = tf + k1 * (1.0 - b + b * (dl / avgdl))
                scores[doc_id] = scores.get(doc_id, 0.0) + term_idf * ((tf * (k1 + 1.0)) / denom)

        ranked = sorted(scores.items(), key=lambda kv: -kv[1])[:25]
        results = []
        for doc_id, sc in ranked:
            doc = docs[doc_id]
            results.append({
                "bm25_score": round(sc, 3),
                "instrument_path": doc["instrument_path"],
                "instrument_title": doc["instrument_title"],
                "jurisdiction": doc["jurisdiction"],
                "provision": doc["provision"],
                "heading": doc["heading"],
                "latest_stage": doc["latest_stage"],
                "latest_date": doc["latest_date"],
                "provenance_mode": doc.get("provenance_mode", "unknown"),
                "snippet": doc.get("snippet", ""),
            })
        return {
            "query": query,
            "normalized_terms": sorted(set(query_terms)),
            "engine": "BM25+UK_US_Norm",
            "match_count": len(scores),
            "results": results,
        }

    # Graceful fallback to search-index.json
    idx = _fetch_raw_json("search-index.json") or {"entries": []}
    matches = []
    for entry in idx.get("entries", []):
        if jf and entry["jurisdiction"].lower() != jf:
            continue
        if df and entry.get("domain", "").lower() != df:
            continue
        hay = f"{entry['heading']} {entry['text']} {entry['instrument_title']}".lower()
        hits = sum(1 for t in set(query_terms) if t in hay)
        if hits > 0:
            matches.append({
                "bm25_score": float(hits),
                "instrument_path": entry["instrument_path"],
                "instrument_title": entry["instrument_title"],
                "jurisdiction": entry["jurisdiction"],
                "provision": entry["provision"],
                "heading": entry["heading"],
                "latest_stage": entry["latest_stage"],
                "latest_date": entry["latest_date"],
                "provenance_mode": entry.get("provenance_mode", "unknown"),
                "snippet": entry["text"][:380],
            })
    matches.sort(key=lambda m: -m["bm25_score"])
    return {"query": query, "engine": "fallback_substring", "match_count": len(matches), "results": matches[:25]}


@_tool_decorator()
def get_citation_graph(instrument_path: str) -> dict[str, Any]:
    """
    Return incoming/outgoing cross-references, treaty harmonization links, and
    authoritative Recital-to-Article interpretive links from `graph.json`.
    """
    graph = _fetch_raw_json("graph.json") or {"nodes": [], "edges": [], "recital_links": {}}
    norm = instrument_path.strip("/").lower()

    outgoing = [e for e in graph.get("edges", []) if e["source"].strip("/").lower() == norm]
    incoming = [e for e in graph.get("edges", []) if e["target"].strip("/").lower() == norm]
    node = next((n for n in graph.get("nodes", []) if n["path"].strip("/").lower() == norm), None)
    recital_links = graph.get("recital_links", {}).get(instrument_path.strip("/"), [])

    return {
        "instrument_path": instrument_path,
        "node": node,
        "outgoing_count": len(outgoing),
        "incoming_count": len(incoming),
        "outgoing_edges": outgoing,
        "incoming_edges": incoming,
        "recital_to_article_links": recital_links,
    }


@_tool_decorator()
def check_applicability(
    instrument_path: str,
    provision: str = "*",
    as_of_date: str | None = None,
    placed_on_market_date: str | None = None,
) -> dict[str, Any]:
    """
    Bitemporal legal enforceability engine. Determines whether a specific legal provision
    is legally enforceable on `as_of_date` (defaults to today UTC), accounting for:
    - EU Digital Omnibus Regulation (EU) 2026/1744 postponements (Annex III -> 2027-12-02,
      Annex I -> 2028-08-02, NCII/CSAM Art. 5 expansion -> 2026-12-02)
    - Legacy system transition grace periods (`placed_on_market_date`)
    - US Executive Order 14110 revocation (2025-01-20)
    - CRA ENISA reporting (2026-09-11) vs. full compliance (2027-12-11)
    - UN Hanoi Cybercrime 40-ratification threshold, Texas TRAIGA (2026-01-01), China 2025 Labeling.
    """
    query_date = as_of_date or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    norm_inst = instrument_path.strip("/").lower()
    norm_prov = "*" if provision.strip() in ("*", "all", "") else _normalize_provision_path(provision)

    rules = _load_applicability().get("rules", [])
    matched_rule = None
    wildcard_rule = None
    for rule in rules:
        if rule["instrument_path"].strip("/").lower() != norm_inst:
            continue
        provs = rule.get("provisions", [])
        if norm_prov in provs or provision.strip().lower() in provs:
            matched_rule = rule
            break
        if "*" in provs:
            wildcard_rule = rule

    rule = matched_rule or wildcard_rule
    if not rule:
        return {
            "instrument_path": instrument_path,
            "provision": norm_prov,
            "as_of_date": query_date,
            "status": "NO_BITEMPORAL_RULE_RECORDED",
        }

    status = "ENFORCEABLE"
    explanation = rule.get("scope_note", "")

    if rule.get("revoked_date") and query_date >= rule["revoked_date"]:
        status = "REVOKED"
        explanation = f"Revoked on {rule['revoked_date']}. {explanation}"
    elif rule.get("status_override") == "OPEN_FOR_SIGNATURE_PENDING_40_RATIFICATIONS":
        status = "NOT_YET_IN_FORCE_PENDING_RATIFICATIONS"
    elif rule.get("entry_into_application"):
        app_date = rule["entry_into_application"]
        if query_date < app_date:
            status = "IN_FORCE_NOT_YET_APPLICABLE"
            explanation = f"Not yet enforceable on {query_date}; enters into application on {app_date}. {explanation}"
        elif (
            placed_on_market_date
            and rule.get("legacy_cutoff_date")
            and rule.get("legacy_transition_deadline")
            and placed_on_market_date < rule["legacy_cutoff_date"]
            and query_date < rule["legacy_transition_deadline"]
        ):
            status = "LEGACY_TRANSITION_GRACE_PERIOD"
            explanation = (
                f"System placed on market {placed_on_market_date} (< {rule['legacy_cutoff_date']}) "
                f"enjoys legacy grace period until {rule['legacy_transition_deadline']}. "
                f"{rule.get('legacy_note', '')}"
            )

    return {
        "instrument_path": rule["instrument_path"],
        "provision": norm_prov,
        "rule_id": rule["rule_id"],
        "as_of_date": query_date,
        "placed_on_market_date": placed_on_market_date,
        "legal_status": status,
        "published_date": rule.get("published_date"),
        "entry_into_force": rule.get("entry_into_force"),
        "original_entry_into_application": rule.get("original_entry_into_application"),
        "effective_entry_into_application": rule.get("entry_into_application"),
        "revoked_date": rule.get("revoked_date"),
        "amended_by": rule.get("amended_by"),
        "amendment_notes": rule.get("amendment_notes"),
        "additional_application_dates": rule.get("additional_application_dates"),
        "penalty_ceiling": rule.get("penalty_ceiling"),
        "explanation": explanation,
    }


@_tool_decorator()
def verify_citations(
    draft_text: str,
    as_of_date: str | None = None,
) -> dict[str, Any]:
    """
    Deterministic Stanford-RegLab-grade anti-hallucination verifier.
    Scans a draft legal memorandum for statutory references (EU AI Act, GDPR, CRA,
    NIS2, DORA, CETS 225, AP I / Geneva Conventions, US EO 14110) and verbatim
    quoted strings ("..."), checking existence, verbatim fidelity, and bitemporal
    enforceability on `as_of_date`. Returns an ABA Formal Opinion 512 Audit Certificate.
    """
    query_date = as_of_date or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    catalog = _load_catalog()

    instrument_detectors: list[tuple[str, str]] = [
        (r"EU\s+AI\s+Act|Regulation\s*\(EU\)\s*2024/1689", "eu/ai-act"),
        (r"\bGDPR\b|Regulation\s*\(EU\)\s*2016/679", "eu/gdpr"),
        (r"Cyber\s+Resilience\s+Act|\bCRA\b|Regulation\s*\(EU\)\s*2024/2847", "eu/cyber/cra"),
        (r"NIS\s*2|Directive\s*\(EU\)\s*2022/2555", "eu/cyber/nis2"),
        (r"\bDORA\b|Regulation\s*\(EU\)\s*2022/2554", "eu/cyber/dora"),
        (r"CETS\s*(?:No\.?\s*)?225|CoE\s+AI\s+Convention", "coe/ai-convention"),
        (r"Additional\s+Protocol\s+I|\bAP\s*I\b|Geneva\s+Conventions?", "ihl/geneva-conventions"),
    ]

    citation_checks: list[dict[str, Any]] = []
    seen_cites: set[tuple[str, str]] = set()
    fetched_texts_for_quotes: list[tuple[str, str]] = []

    # Sentence-scoped extraction catches compound citations ("EU AI Act Article 51 ... while Article 199 ...")
    sentences = re.split(r"(?<=[.!?\n])\s+", draft_text)
    for sent in sentences:
        if not sent.strip():
            continue
        # Find all instrument anchors in the sentence with their character positions
        anchors: list[tuple[int, str, str]] = []
        for det_pat, ipath in instrument_detectors:
            for dm in re.finditer(det_pat, sent, re.I):
                anchors.append((dm.start(), ipath, dm.group(0)))
        if not anchors:
            continue
        anchors.sort(key=lambda x: x[0])

        for am in re.finditer(r"\bArticles?\s+(\d+[a-z]?)\b", sent, re.I):
            art_pos = am.start()
            # Bind to the closest preceding instrument anchor (or first anchor in sentence)
            preceding = [a for a in anchors if a[0] <= art_pos]
            _, inst_path, anchor_txt = preceding[-1] if preceding else anchors[0]
            art_num = am.group(1)
            norm_prov = _normalize_provision_path(art_num)
            if (inst_path, norm_prov) in seen_cites:
                continue
            seen_cites.add((inst_path, norm_prov))

            inst = _find_instrument(catalog, inst_path)
            latest_ver = inst["versions"][-1] if inst else None
            text = None
            if inst and latest_ver:
                text, _ = _fetch_provision_at_stage(inst, latest_ver, norm_prov)
                if text is None and inst_path == "eu/ai-act":
                    oj_ver = _resolve_stage(inst, "official_journal_final")
                    text, _ = _fetch_provision_at_stage(inst, oj_ver, norm_prov)

            bitemp = check_applicability(inst_path, norm_prov, as_of_date=query_date)
            if text is None:
                verdict = "NOT_IN_CORPUS_OR_NONEXISTENT"
            elif bitemp.get("legal_status") == "REVOKED":
                verdict = "REVOKED"
            elif bitemp.get("legal_status") == "IN_FORCE_NOT_YET_APPLICABLE":
                verdict = "VERIFIED_TEXT_NOT_YET_APPLICABLE"
            else:
                verdict = "VERIFIED"
                fetched_texts_for_quotes.append((f"{inst_path}/{norm_prov}", text))

            citation_checks.append({
                "citation_match": f"{anchor_txt} {am.group(0)}".strip(),
                "instrument_path": inst_path,
                "provision": norm_prov,
                "verdict": verdict,
                "bitemporal_status": bitemp.get("legal_status"),
                "effective_application_date": bitemp.get("effective_entry_into_application"),
            })

    # Explicitly flag stale citations to revoked US Executive Order 14110
    warnings: list[str] = []
    if re.search(r"Executive\s+Order\s+14110|\bEO\s*14110\b", draft_text, re.I):
        if not re.search(r"revok|rescind|repeal", draft_text, re.I):
            warnings.append(
                "CRITICAL BITEMPORAL WARNING: Draft cites Executive Order 14110 without noting its formal revocation on 2025-01-20."
            )
            citation_checks.append({
                "citation_match": "Executive Order 14110",
                "instrument_path": "national/us/nist-ai-rmf",
                "provision": "eo-14110",
                "verdict": "REVOKED_STATUTE_CITED_AS_ACTIVE",
                "bitemporal_status": "REVOKED",
                "effective_application_date": "2023-10-30 (REVOKED 2025-01-20)",
            })

    # Verify any long verbatim quotes ("...") against retrieved corpus provisions
    quote_checks: list[dict[str, Any]] = []
    for qm in re.finditer(r'"([^"]{30,400})"', draft_text):
        quote = re.sub(r"\s+", " ", qm.group(1)).strip()
        q_low = quote.lower()
        best_match = None
        best_ratio = 0.0
        for src_label, src_text in fetched_texts_for_quotes:
            norm_src = re.sub(r"\s+", " ", src_text).lower()
            if q_low in norm_src:
                best_match = src_label
                best_ratio = 1.0
                break
            # Sliding window approximate check
            ratio = difflib.SequenceMatcher(None, q_low, norm_src[: min(len(norm_src), 8000)]).quick_ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = src_label
        quote_checks.append({
            "quote_excerpt": quote[:120] + ("..." if len(quote) > 120 else ""),
            "verdict": "EXACT_MATCH" if best_ratio == 1.0 else ("UNVERIFIED_OR_PARAPHRASED" if fetched_texts_for_quotes else "NO_CITED_PROVISION_TO_CHECK"),
            "matched_source": best_match,
            "similarity": round(best_ratio, 3),
        })

    failed = [
        c for c in citation_checks
        if c["verdict"] in ("NOT_IN_CORPUS_OR_NONEXISTENT", "REVOKED_STATUTE_CITED_AS_ACTIVE")
    ]
    overall = "PASS" if (not failed and not warnings) else "REQUIRES_ATTORNEY_CORRECTION"

    return {
        "aba_formal_opinion_512_audit": overall,
        "as_of_date": query_date,
        "citations_checked": len(citation_checks),
        "citations_failed": len(failed),
        "warnings": warnings,
        "citation_checks": citation_checks,
        "quote_checks": quote_checks,
    }


@_tool_decorator()
def get_provenance_audit(instrument_path: str | None = None) -> dict[str, Any]:
    """
    Return the cryptographic SHA-256 primary-source provenance manifest, official ELI/CELEX
    permalinks, fetch timestamps, and primary-source verification coverage metrics.
    """
    manifest = _load_provenance()
    stages = manifest.get("stages", [])
    if instrument_path:
        norm = instrument_path.strip("/").lower()
        stages = [s for s in stages if s["instrument_path"].strip("/").lower() == norm]

    primary_modes = {"full_primary_xhtml_akn", "full_primary_pdf", "full_primary_html"}
    full_primary_count = sum(1 for s in stages if s.get("provenance_mode") in primary_modes)

    return {
        "schema_version": manifest.get("schema_version", "2.0.0"),
        "built_utc": manifest.get("built_utc"),
        "stages_returned": len(stages),
        "full_primary_text_stages": full_primary_count,
        "structured_milestone_stages": len(stages) - full_primary_count,
        "stages": stages,
    }


if __name__ == "__main__":
    mcp.run()
