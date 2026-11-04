"""
Cross-Reference & Citation Graph Builder (`src/parser/diff_graph.py`).

Extracts explicit declarative relationships from `src/catalog.json` as well as
inline textual citations (e.g., references to Regulation (EU) 2016/679, Directive
(EU) 2019/790, Framework Decision 2002/584/JHA, Article 36 of Additional Protocol I,
Executive Order 14110, or CETS No. 225) across all provisions, producing `graph.json`
for the `corpus` branch.
"""

from __future__ import annotations

import re
from typing import Any


INLINE_CITATION_PATTERNS: list[tuple[str, str, str]] = [
    (r"Regulation\s*\(EU\)\s*2016/679", "eu/gdpr", "cites_regulation"),
    (r"Regulation\s*\(EU\)\s*2024/1689", "eu/ai-act", "cites_regulation"),
    (r"CETS\s*(?:No\.?\s*)?225", "coe/ai-convention", "cites_treaty"),
    (r"Article\s+36", "ihl/geneva-conventions", "cites_weapons_review_norm"),
    (r"Additional\s+Protocol\s+I", "ihl/geneva-conventions", "cites_ihl_protocol"),
    (r"Geneva\s+Conventions", "ihl/geneva-conventions", "cites_ihl_convention"),
    (r"NIST\s+AI\s+100-1", "national/us/nist-ai-rmf", "cites_standard"),
    (r"Algorithmic\s+Recommendation\s+Management\s+Provisions", "national/cn/cac-ai-measures", "cites_national_measure"),
    (r"Deep\s+Synthesis\s+Management\s+Provisions", "national/cn/cac-ai-measures", "cites_national_measure"),
    (r"A/RES/78/265", "un/ai-governance", "cites_un_resolution"),
]


def build_citation_graph(
    catalog: dict[str, Any],
    latest_stage_files: dict[str, str],
) -> dict[str, Any]:
    """
    Build `graph.json` containing nodes (instruments) and directed edges
    (declarative cross-references + regex-extracted provision-level citations).
    """
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str, str]] = set()

    for inst in catalog.get("instruments", []):
        inst_path = inst["path"]
        nodes.append(
            {
                "id": inst["id"],
                "path": inst_path,
                "title": inst["title"],
                "short_title": inst.get("short_title", inst["title"]),
                "jurisdiction": inst["jurisdiction"],
                "type": inst.get("type", "instrument"),
                "status": inst.get("status"),
                "versions_count": len(inst.get("versions", [])),
            }
        )

        for ref in inst.get("cross_references", []):
            target = ref["target"]
            rel = ref["relationship"]
            provs = ", ".join(ref.get("provisions", []))
            key = (inst_path, target, rel, provs)
            if key not in seen_edges:
                seen_edges.add(key)
                edges.append(
                    {
                        "source": inst_path,
                        "target": target,
                        "relationship": rel,
                        "provisions": ref.get("provisions", []),
                        "note": ref.get("note", ""),
                        "origin": "catalog_declarative",
                    }
                )

    # Scan normalized Markdown files for inline cross-references
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
                    edges.append(
                        {
                            "source": source_instrument,
                            "target": target_instrument,
                            "relationship": rel_type,
                            "provisions": [article_file],
                            "note": f"Automated inline citation match ({pattern}) in {file_path}",
                            "origin": "inline_text_extraction",
                        }
                    )

    return {
        "schema_version": "1.0.0",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }
