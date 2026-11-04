"""
Stateless Remote MCP Server for `lex-machina` (`mcp_server/server.py`).

Requires **0 MB of local legal data**. Queries the repository's `corpus` orphan
branch remotely via `raw.githubusercontent.com` and the GitHub REST API (with
optional `GITHUB_TOKEN` support for higher rate limits), and falls back
gracefully to the local declarative `src/catalog.json` if `corpus` is still
building on GitHub Actions.

Implements 6 MCP tools:
1. `list_instruments(jurisdiction: str | None = None)`
2. `get_provision(instrument_path: str, provision: str, as_of: str | None = None)`
3. `diff_provisions(instrument_path: str, provision: str, stage_a: str, stage_b: str)`
4. `blame_provision(instrument_path: str, provision: str)`
5. `search_corpus(query: str, jurisdiction: str | None = None)`
6. `get_citation_graph(instrument_path: str)`
"""

from __future__ import annotations

import difflib
import json
import os
from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

DEFAULT_REPO = os.environ.get("LEX_MACHINA_REPO", "a-vip/lex-machina")
CORPUS_BRANCH = os.environ.get("LEX_MACHINA_BRANCH", "corpus")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

LOCAL_CATALOG_PATH = Path(__file__).resolve().parents[1] / "src" / "catalog.json"

mcp = FastMCP(
    "lex-machina",
    instructions=(
        "Stateless legal history and institutional git-blame MCP server for global AI "
        "regulation (EU AI Act, GDPR, CoE AI Convention CETS 225, UNGA/CCW LAWS, NIST AI RMF, "
        "China CAC) and International Humanitarian Law (1949 Geneva Conventions & 1977 Additional Protocols)."
    ),
)


def _github_headers(accept: str = "application/vnd.github+json") -> dict[str, str]:
    headers = {
        "User-Agent": "lex-machina-mcp-server/1.0",
        "Accept": accept,
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def _raw_url(rel_path: str) -> str:
    clean = rel_path.lstrip("/")
    return f"https://raw.githubusercontent.com/{DEFAULT_REPO}/{CORPUS_BRANCH}/{clean}"


def _fetch_raw_text(rel_path: str) -> str | None:
    """Fetch a raw file from the remote `corpus` branch on GitHub."""
    url = _raw_url(rel_path)
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        resp = client.get(url, headers=_github_headers("text/plain"))
        if resp.status_code == 200:
            return resp.text
    return None


def _fetch_raw_json(rel_path: str) -> dict[str, Any] | None:
    text = _fetch_raw_text(rel_path)
    if text:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    return None


def _load_catalog() -> dict[str, Any]:
    """Load catalog from remote `corpus` branch or local `src/catalog.json`."""
    remote = _fetch_raw_json("catalog.json")
    if remote:
        return remote
    if LOCAL_CATALOG_PATH.exists():
        return json.loads(LOCAL_CATALOG_PATH.read_text(encoding="utf-8"))
    return {"instruments": []}


def _find_instrument(catalog: dict[str, Any], instrument_path: str) -> dict[str, Any] | None:
    norm = instrument_path.strip("/").lower()
    for inst in catalog.get("instruments", []):
        if inst["path"].strip("/").lower() == norm or inst["id"].lower() == norm:
            return inst
    return None


def _resolve_stage(instrument: dict[str, Any], as_of: str | None) -> dict[str, Any]:
    """
    Resolve a `stage` identifier, human label, or `YYYY-MM-DD` date string to
    a specific chronological version entry in `instrument['versions']`.
    """
    versions = instrument.get("versions", [])
    if not versions:
        raise ValueError(f"Instrument '{instrument['path']}' has no versions.")
    if not as_of or as_of.strip().lower() in ("latest", "head", "current"):
        return versions[-1]

    query = as_of.strip().lower()
    # 1. Exact or substring match on stage or stage_label or document_symbol
    for ver in versions:
        if (
            query == ver["stage"].lower()
            or query in ver["stage"].lower()
            or query in ver["stage_label"].lower()
            or query in ver.get("document_symbol", "").lower()
            or query == ver["date"].lower()
        ):
            return ver

    # 2. Date comparison (as_of <= date)
    dated_candidates = [ver for ver in versions if ver["date"] <= query]
    if dated_candidates:
        return dated_candidates[-1]

    return versions[-1]


def _normalize_provision_path(provision: str) -> str:
    """
    Normalize shorthand provision inputs such as `'5'`, `'article-5'`,
    `'article-005'`, or `'articles/article-005.md'` into `'articles/article-005.md'`.
    """
    p = provision.strip().strip("/")
    if p.endswith(".md") and ("/" in p or p in ("full-text.md", "instrument.md")):
        return p
    if p.isdigit():
        return f"articles/article-{int(p):03d}.md"
    if p.lower().startswith("article-") and not p.endswith(".md"):
        suffix = p[len("article-") :]
        if suffix.isdigit():
            return f"articles/article-{int(suffix):03d}.md"
        return f"articles/article-{suffix}.md"
    if p.lower().startswith("recital-"):
        suffix = p[len("recital-") :].removesuffix(".md")
        if suffix.isdigit():
            return f"recitals/recital-{int(suffix):03d}.md"
        return f"recitals/recital-{suffix}.md"
    if p.lower().startswith("annex-"):
        suffix = p[len("annex-") :].removesuffix(".md").lower()
        return f"annexes/annex-{suffix}.md"
    if not p.endswith(".md"):
        p = f"{p}.md"
    if "/" not in p:
        p = f"articles/{p}"
    return p


def _fetch_provision_at_stage(
    instrument: dict[str, Any],
    version: dict[str, Any],
    norm_provision: str,
) -> str | None:
    """
    Fetch the exact Markdown of `norm_provision` for a given `version` stage from
    `snapshots/<instrument_path>/<stage>.json` on the remote `corpus` branch, or
    directly from `<instrument_path>/<norm_provision>` if querying the latest stage.
    """
    inst_path = instrument["path"].strip("/")
    stage = version["stage"]
    snapshot = _fetch_raw_json(f"snapshots/{inst_path}/{stage}.json")
    full_rel_path = f"{inst_path}/{norm_provision}"

    if snapshot and "files" in snapshot:
        files_map = snapshot["files"]
        if full_rel_path in files_map:
            return files_map[full_rel_path]

    # Fallback: if querying the latest stage, fetch the direct raw file
    if version == instrument["versions"][-1]:
        direct = _fetch_raw_text(full_rel_path)
        if direct:
            return direct

    return None


@mcp.tool()
def list_instruments(jurisdiction: str | None = None) -> dict[str, Any]:
    """
    List all tracked treaties, regulations, and national AI frameworks with their
    available chronological version dates, legislative stages, and institutional authors.
    """
    catalog = _load_catalog()
    instruments = catalog.get("instruments", [])
    if jurisdiction:
        j_filter = jurisdiction.strip().lower()
        instruments = [
            inst
            for inst in instruments
            if inst["jurisdiction"].lower() == j_filter
            or inst["path"].lower().startswith(f"{j_filter}/")
        ]

    results = []
    for inst in instruments:
        results.append(
            {
                "id": inst["id"],
                "path": inst["path"],
                "jurisdiction": inst["jurisdiction"],
                "title": inst["title"],
                "short_title": inst.get("short_title", inst["title"]),
                "status": inst.get("status"),
                "in_force_date": inst.get("in_force_date"),
                "versions": [
                    {
                        "stage": v["stage"],
                        "stage_label": v["stage_label"],
                        "date": v["date"],
                        "document_symbol": v["document_symbol"],
                        "author": f"{v['author_name']} <{v['author_email']}>",
                    }
                    for v in inst.get("versions", [])
                ],
            }
        )

    return {
        "repository": DEFAULT_REPO,
        "branch": CORPUS_BRANCH,
        "count": len(results),
        "instruments": results,
    }


@mcp.tool()
def get_provision(
    instrument_path: str,
    provision: str,
    as_of: str | None = None,
) -> dict[str, Any]:
    """
    Fetch the exact normalized Markdown text of an article, recital, or annex
    (e.g., `instrument_path='eu/ai-act'`, `provision='articles/article-005.md'`)
    at a specific date (`'2023-06-14'`) or legislative stage (`'parliament_mandate'`,
    `'commission_proposal'`, `'council_general_approach'`, `'trilogue_provisional_agreement'`,
    `'official_journal_final'`).
    """
    catalog = _load_catalog()
    instrument = _find_instrument(catalog, instrument_path)
    if not instrument:
        return {"error": f"Unknown instrument_path: '{instrument_path}'"}

    version = _resolve_stage(instrument, as_of)
    norm_prov = _normalize_provision_path(provision)
    markdown_text = _fetch_provision_at_stage(instrument, version, norm_prov)

    if markdown_text is None:
        return {
            "error": (
                f"Provision '{norm_prov}' not found in '{instrument['path']}' "
                f"at stage '{version['stage']}' ({version['date']})."
            ),
            "instrument_path": instrument["path"],
            "stage": version["stage"],
            "date": version["date"],
        }

    return {
        "instrument_path": instrument["path"],
        "title": instrument["title"],
        "provision": norm_prov,
        "stage": version["stage"],
        "stage_label": version["stage_label"],
        "date": version["date"],
        "document_symbol": version["document_symbol"],
        "institutional_author": f"{version['author_name']} <{version['author_email']}>",
        "markdown": markdown_text,
    }


@mcp.tool()
def diff_provisions(
    instrument_path: str,
    provision: str,
    stage_a: str,
    stage_b: str,
) -> dict[str, Any]:
    """
    Compute and return a unified redline diff showing exact wording additions (`+`)
    and deletions (`-`) for a provision between two legislative stages or dates
    (e.g., `stage_a='commission_proposal'`, `stage_b='parliament_mandate'`).
    """
    catalog = _load_catalog()
    instrument = _find_instrument(catalog, instrument_path)
    if not instrument:
        return {"error": f"Unknown instrument_path: '{instrument_path}'"}

    ver_a = _resolve_stage(instrument, stage_a)
    ver_b = _resolve_stage(instrument, stage_b)
    norm_prov = _normalize_provision_path(provision)

    text_a = _fetch_provision_at_stage(instrument, ver_a, norm_prov) or ""
    text_b = _fetch_provision_at_stage(instrument, ver_b, norm_prov) or ""

    label_a = f"{instrument['path']}/{norm_prov}@{ver_a['stage']} ({ver_a['date']} — {ver_a['author_name']})"
    label_b = f"{instrument['path']}/{norm_prov}@{ver_b['stage']} ({ver_b['date']} — {ver_b['author_name']})"

    diff_lines = list(
        difflib.unified_diff(
            text_a.splitlines(keepends=True),
            text_b.splitlines(keepends=True),
            fromfile=label_a,
            tofile=label_b,
            n=3,
        )
    )
    unified_diff_str = "".join(diff_lines)

    added = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))

    return {
        "instrument_path": instrument["path"],
        "provision": norm_prov,
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
        "stats": {
            "lines_added": added,
            "lines_removed": removed,
        },
        "unified_diff": unified_diff_str or "(No textual differences between selected stages)",
    }


@mcp.tool()
def blame_provision(
    instrument_path: str,
    provision: str,
) -> dict[str, Any]:
    """
    Run line-by-line institutional attribution (`git blame` across legislative
    stages) on a provision to show which institutional actor (European Commission,
    Council of the EU, European Parliament, EU Trilogue Negotiators, etc.)
    introduced or last modified each paragraph or sub-clause.
    """
    catalog = _load_catalog()
    instrument = _find_instrument(catalog, instrument_path)
    if not instrument:
        return {"error": f"Unknown instrument_path: '{instrument_path}'"}

    norm_prov = _normalize_provision_path(provision)
    versions = instrument.get("versions", [])

    # Track the earliest version stage in which each normalized line appeared or changed
    line_attribution: dict[str, dict[str, str]] = {}
    stage_snapshots: list[tuple[dict[str, Any], list[str]]] = []

    for ver in versions:
        text = _fetch_provision_at_stage(instrument, ver, norm_prov)
        if not text:
            continue
        body_lines = [
            line
            for line in text.splitlines()
            if line.strip() and not line.startswith("- **") and not line.startswith("# ")
        ]
        stage_snapshots.append((ver, body_lines))
        for line in body_lines:
            if line not in line_attribution:
                line_attribution[line] = {
                    "stage": ver["stage"],
                    "stage_label": ver["stage_label"],
                    "date": ver["date"],
                    "document_symbol": ver["document_symbol"],
                    "author_name": ver["author_name"],
                    "author_email": ver["author_email"],
                }

    if not stage_snapshots:
        return {
            "error": f"Provision '{norm_prov}' not found across any stages of '{instrument['path']}'.",
        }

    latest_ver, latest_lines = stage_snapshots[-1]
    attributed_lines = []
    for line_no, line in enumerate(latest_lines, start=1):
        origin = line_attribution.get(
            line,
            {
                "stage": latest_ver["stage"],
                "stage_label": latest_ver["stage_label"],
                "date": latest_ver["date"],
                "document_symbol": latest_ver["document_symbol"],
                "author_name": latest_ver["author_name"],
                "author_email": latest_ver["author_email"],
            },
        )
        attributed_lines.append(
            {
                "line_number": line_no,
                "introduced_in_stage": origin["stage"],
                "introduced_on_date": origin["date"],
                "document_symbol": origin["document_symbol"],
                "institutional_author": f"{origin['author_name']} <{origin['author_email']}>",
                "text": line,
            }
        )

    return {
        "instrument_path": instrument["path"],
        "provision": norm_prov,
        "latest_stage": latest_ver["stage"],
        "latest_date": latest_ver["date"],
        "stages_analyzed": len(stage_snapshots),
        "blame": attributed_lines,
    }


@mcp.tool()
def search_corpus(
    query: str,
    jurisdiction: str | None = None,
) -> dict[str, Any]:
    """
    Search across the remote `search-index.json` generated on the `corpus` branch
    for matching articles, recitals, and annexes by keyword or phrase.
    """
    index_data = _fetch_raw_json("search-index.json")
    if not index_data:
        return {
            "error": "Remote search-index.json could not be fetched from refs/heads/corpus.",
            "repository": DEFAULT_REPO,
            "branch": CORPUS_BRANCH,
        }

    terms = [t.lower() for t in query.strip().split() if t.strip()]
    j_filter = jurisdiction.strip().lower() if jurisdiction else None

    matches = []
    for entry in index_data.get("entries", []):
        if j_filter and entry["jurisdiction"].lower() != j_filter:
            continue
        haystack = f"{entry['heading']} {entry['text']} {entry['instrument_title']}".lower()
        if all(term in haystack for term in terms):
            score = sum(haystack.count(term) for term in terms)
            matches.append(
                {
                    "score": score,
                    "instrument_path": entry["instrument_path"],
                    "instrument_title": entry["instrument_title"],
                    "jurisdiction": entry["jurisdiction"],
                    "provision": entry["provision"],
                    "heading": entry["heading"],
                    "latest_stage": entry["latest_stage"],
                    "latest_date": entry["latest_date"],
                    "latest_author": entry["latest_author"],
                    "snippet": entry["text"][:450],
                }
            )

    matches.sort(key=lambda m: (-m["score"], m["instrument_path"], m["provision"]))
    return {
        "query": query,
        "jurisdiction": jurisdiction,
        "match_count": len(matches),
        "results": matches[:25],
    }


@mcp.tool()
def get_citation_graph(instrument_path: str) -> dict[str, Any]:
    """
    Return incoming and outgoing cross-references, treaty harmonization links,
    and amending relationships for an instrument from `graph.json` on the `corpus` branch.
    """
    graph = _fetch_raw_json("graph.json")
    norm = instrument_path.strip("/").lower()

    if not graph:
        # Fallback to local catalog cross-references if remote graph.json isn't reachable yet
        catalog = _load_catalog()
        inst = _find_instrument(catalog, instrument_path)
        if not inst:
            return {"error": f"Unknown instrument_path: '{instrument_path}'"}
        return {
            "instrument_path": inst["path"],
            "outgoing_edges": inst.get("cross_references", []),
            "incoming_edges": [],
        }

    outgoing = [
        e for e in graph.get("edges", []) if e["source"].strip("/").lower() == norm
    ]
    incoming = [
        e for e in graph.get("edges", []) if e["target"].strip("/").lower() == norm
    ]
    node = next(
        (n for n in graph.get("nodes", []) if n["path"].strip("/").lower() == norm),
        None,
    )

    return {
        "instrument_path": instrument_path,
        "node": node,
        "outgoing_count": len(outgoing),
        "incoming_count": len(incoming),
        "outgoing_edges": outgoing,
        "incoming_edges": incoming,
    }


if __name__ == "__main__":
    mcp.run()
