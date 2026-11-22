"""
Cross-Reference & Citation Graph Builder (`src/parser/diff_graph.py` — v2.0).

Combines declarative cross-references from `catalog.json`, inline regex-extracted
statutory citations across AI, privacy, cyber (CRA, NIS2, DORA, Hanoi Cybercrime,
Budapest Convention), and IHL provisions, plus recital-to-article mappings from
`concordance.json`.
"""

from __future__ import annotations

import re
from typing import Any


INLINE_CITATION_PATTERNS: list[tuple[str, str, str]] = [
    (r"Regulation\s*\(EU\)\s*2016/679", "eu/gdpr", "cites_regulation"),
    (r"Regulation\s*\(EU\)\s*2024/1689", "eu/ai-act", "cites_regulation"),
    (r"Regulation\s*\(EU\)\s*2026/1744", "eu/ai-act", "cites_amending_regulation"),
    (r"Regulation\s*\(EU\)\s*2024/2847|Cyber\s+Resilience\s+Act", "eu/cyber/cra", "cites_cyber_regulation"),
    (r"Directive\s*\(EU\)\s*2022/2555|NIS\s*2", "eu/cyber/nis2", "cites_cyber_directive"),
    (r"Regulation\s*\(EU\)\s*2022/2554|\bDORA\b", "eu/cyber/dora", "cites_cyber_regulation"),
    (r"CETS\s*(?:No\.?\s*)?225", "coe/ai-convention", "cites_treaty"),
    (r"ETS\s*(?:No\.?\s*)?185|Budapest\s+Convention", "coe/budapest-convention", "cites_cyber_treaty"),
    (r"A/RES/79/243|Hanoi\s+Convention", "un/cybercrime-convention", "cites_cyber_treaty"),
    (r"Article\s+36", "ihl/geneva-conventions", "cites_weapons_review_norm"),
    (r"Additional\s+Protocol\s+I", "ihl/geneva-conventions", "cites_ihl_protocol"),
    (r"Geneva\s+Conventions", "ihl/geneva-conventions", "cites_ihl_convention"),
    (r"NIST\s+AI\s+(?:100-1|600-1|RMF)", "national/us/nist-ai-rmf", "cites_standard"),
    (r"TRAIGA|HB\s*149|SB\s*24-205|AB\s*2013|SB\s*53", "national/us/state-ai-laws", "cites_us_state_statute"),
    (r"Algorithmic\s+Recommendation|Deep\s+Synthesis|GB\s*45438", "national/cn/cac-ai-measures", "cites_national_measure"),
    (r"A/RES/78/265|Global\s+Digital\s+Compact", "un/ai-governance", "cites_un_resolution"),
]


def build_citation_graph(
    catalog: dict[str, Any],
    latest_stage_files: dict[str, str],
    concordance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build `graph.json` with instrument nodes, directed citation edges, and recital links."""
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str, str]] = set()

    for inst in catalog.get("instruments", []):
        inst_path = inst["path"]
        nodes.append({
            "id": inst["id"],
            "path": inst_path,
            "title": inst["title"],
            "short_title": inst.get("short_title", inst["title"]),
            "jurisdiction": inst["jurisdiction"],
            "domain": inst.get("domain", "ai"),
            "type": inst.get("type", "instrument"),
            "status": inst.get("status"),
            "versions_count": len(inst.get("versions", [])),
        })

        for ref in inst.get("cross_references", []):
            target = ref["target"]
            rel = ref["relationship"]
            provs = ", ".join(ref.get("provisions", []))
            key = (inst_path, target, rel, provs)
            if key not in seen_edges:
                seen_edges.add(key)
                edges.append({
                    "source": inst_path,
                    "target": target,
                    "relationship": rel,
                    "provisions": ref.get("provisions", []),
                    "note": ref.get("note", ""),
                    "origin": "catalog_declarative",
                })

    for file_path, content in sorted(latest_stage_files.items()):
        if not file_path.endswith(".md") or "/articles/" not in file_path:
            continue
        parts = file_path.split("/articles/")
        source_instrument = parts[0]
        article_file = f"articles/{parts[1]}"

        for pattern, target_instrument, rel_type in INLINE_CITATION_PATTERNS:
            if source_instrument == target_instrument:
                continue
            if re.search(pattern, content, flags=re.IGNORECASE):
                key = (source_instrument, target_instrument, rel_type, article_file)
                if key not in seen_edges:
                    seen_edges.add(key)
                    edges.append({
                        "source": source_instrument,
                        "target": target_instrument,
                        "relationship": rel_type,
                        "provisions": [article_file],
                        "note": f"Inline statutory citation extracted from {file_path}",
                        "origin": "inline_text_extraction",
                    })

    # Include recital-to-article mapping index from concordance.json
    recital_links: dict[str, list[dict[str, Any]]] = {}
    if concordance:
        for inst_path, norms in concordance.get("concordances", {}).items():
            recital_links[inst_path] = [
                {
                    "norm_id": n["norm_id"],
                    "label": n["label"],
                    "recitals": n.get("recitals", []),
                    "stage_map": n.get("stage_map", {}),
                }
                for n in norms
            ]

    return {
        "schema_version": "2.0.0",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "recital_links": recital_links,
    }
