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
    (r"Additional\s+Protocol\s+I\b", "ihl/geneva-conventions", "cites_ihl_protocol"),
    (r"Additional\s+Protocol\s+II\b", "ihl/additional-protocol-ii", "cites_ihl_protocol"),
    (r"Geneva\s+Conventions", "ihl/geneva-conventions", "cites_ihl_convention"),
    (r"NIST\s+AI\s+(?:100-1|600-1|RMF)", "national/us/nist-ai-rmf", "cites_standard"),
    (r"TRAIGA|HB\s*149|SB\s*24-205|AB\s*2013|SB\s*53", "national/us/state-ai-laws", "cites_us_state_statute"),
    (r"Algorithmic\s+Recommendation|Deep\s+Synthesis|GB\s*45438", "national/cn/cac-ai-measures", "cites_national_measure"),
    (r"A/RES/78/265|Global\s+Digital\s+Compact", "un/ai-governance", "cites_un_resolution"),
    (r"C-634/21|\bSCHUFA\b", "caselaw/cjeu/schufa-c-634-21", "cites_cjeu_precedent"),
    (r"C-311/18|Schrems\s*II", "caselaw/cjeu/schrems-ii-c-311-18", "cites_cjeu_precedent"),
    (r"C-252/21|Bundeskartellamt", "caselaw/cjeu/meta-bundeskartellamt-c-252-21", "cites_cjeu_precedent"),
    (r"C-511/18|La\s+Quadrature\s+du\s+Net", "caselaw/cjeu/la-quadrature-du-net-c-511-18", "cites_cjeu_precedent"),
    (r"Nuclear\s+Weapons\s+Advisory\s+Opinion|Martens\s+Clause|A/51/218", "caselaw/icj/nuclear-weapons-1996", "cites_icj_precedent"),
    (r"ISO/IEC\s*42001", "standards/iso-iec-42001", "cites_technical_standard"),
    (r"Data\s*\(Use\s+and\s+Access\)\s*Act|UK\s+AI\s+Safety\s+Institute", "national/uk/ai-governance", "cites_national_statute"),
    (r"Act\s+No\.\s*20676|AI\s+Basic\s+Act", "national/kr/ai-basic-act", "cites_national_statute"),
    (r"Act\s+No\.\s*53\s+of\s+2025|AI\s+Promotion\s+Act", "national/jp/ai-promotion-act", "cites_national_statute"),
    (r"PL\s*2338", "national/br/ai-bill-pl2338", "cites_legislative_bill"),
    (r"IMDA|Agentic\s+AI", "national/sg/agentic-ai-governance", "cites_governance_framework"),
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
