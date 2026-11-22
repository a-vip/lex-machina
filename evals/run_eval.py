"""
LexMachina-Eval Harness (`evals/run_eval.py`).

Executes the 100-case preregistered legal-informatics benchmark directly inside
GitHub Actions against the live `refs/heads/corpus` branch and `mcp_server/server.py`,
measuring:
- Category A: Full-Text Verbatim Grounding (25 cases)
- Category B: Concordance-Aware Travaux Preparatoires & Institutional Blame (20 cases)
- Category C: Bitemporal Enforceability Traps (20 cases)
- Category D: Adversarial Anti-Hallucination & Citation Verification (20 cases)
- Category E: Cross-Dialect BM25 Search, Cyber Pillar & Provenance Audit (15 cases)

Emits `eval-scorecard.json` and `EVAL_REPORT.md` for transparent, reproducible
public verification modeled on Stanford RegLab & SkillsBench standards.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mcp_server import server as mcp_srv


TOOLS = {
    "list_instruments": mcp_srv.list_instruments,
    "get_provision": mcp_srv.get_provision,
    "diff_provisions": mcp_srv.diff_provisions,
    "blame_provision": mcp_srv.blame_provision,
    "search_corpus": mcp_srv.search_corpus,
    "get_citation_graph": mcp_srv.get_citation_graph,
    "check_applicability": mcp_srv.check_applicability,
    "verify_citations": mcp_srv.verify_citations,
    "get_provenance_audit": mcp_srv.get_provenance_audit,
}


def evaluate_case(case: dict[str, Any]) -> tuple[bool, str]:
    tool_fn = TOOLS[case["tool"]]
    res = tool_fn(**case["args"])
    exp = case["expect"]

    if exp.get("expect_error"):
        ok = "error" in res
        return ok, ("Correctly abstained with error" if ok else f"Expected error, got keys {list(res.keys())}")

    if exp.get("no_error") and "error" in res:
        return False, f"Unexpected error: {res['error']}"

    if "must_contain_any" in exp:
        md = (res.get("markdown") or "").lower()
        if not any(tok.lower() in md for tok in exp["must_contain_any"]):
            return False, f"None of {exp['must_contain_any']} found in provision text"

    if "resolved_provision" in exp:
        got = res.get("resolved_provision")
        if got != exp["resolved_provision"]:
            return False, f"Expected resolved_provision={exp['resolved_provision']}, got {got}"

    if "min_changes" in exp:
        stats = res.get("stats", {})
        total_chg = stats.get("lines_added", 0) + stats.get("lines_removed", 0)
        if total_chg < exp["min_changes"]:
            return False, f"Expected >= {exp['min_changes']} diff lines, got {total_chg}"

    if "min_clauses" in exp:
        clauses = res.get("blame", [])
        if len(clauses) < exp["min_clauses"]:
            return False, f"Expected >= {exp['min_clauses']} blamed clauses, got {len(clauses)}"

    if "min_stages" in exp:
        st = res.get("stages_analyzed", [])
        if len(st) < exp["min_stages"]:
            return False, f"Expected >= {exp['min_stages']} stages analyzed, got {len(st)}"

    if "min_linked_recitals" in exp:
        recs = res.get("linked_recitals", [])
        if len(recs) < exp["min_linked_recitals"]:
            return False, f"Expected >= {exp['min_linked_recitals']} linked recitals, got {len(recs)}"

    if "legal_status" in exp:
        got = res.get("legal_status")
        if got != exp["legal_status"]:
            return False, f"Expected legal_status={exp['legal_status']}, got {got}"

    if "effective_entry_into_application" in exp:
        got = res.get("effective_entry_into_application")
        if got != exp["effective_entry_into_application"]:
            return False, f"Expected effective_entry_into_application={exp['effective_entry_into_application']}, got {got}"

    if "aba_formal_opinion_512_audit" in exp:
        got = res.get("aba_formal_opinion_512_audit")
        if got != exp["aba_formal_opinion_512_audit"]:
            return False, f"Expected audit={exp['aba_formal_opinion_512_audit']}, got {got} (checks={res.get('citation_checks')})"

    if "min_matches" in exp:
        mc = res.get("match_count", 0)
        if mc < exp["min_matches"]:
            return False, f"Expected >= {exp['min_matches']} search matches, got {mc}"

    if "min_outgoing" in exp:
        oc = res.get("outgoing_count", 0)
        if oc < exp["min_outgoing"]:
            return False, f"Expected >= {exp['min_outgoing']} outgoing graph edges, got {oc}"

    if "min_count" in exp:
        c = res.get("count", 0)
        if c < exp["min_count"]:
            return False, f"Expected count >= {exp['min_count']}, got {c}"

    if "min_full_primary_stages" in exp:
        fp = res.get("full_primary_text_stages", 0)
        if fp < exp["min_full_primary_stages"]:
            return False, f"Expected full_primary_text_stages >= {exp['min_full_primary_stages']}, got {fp}"

    return True, "PASS"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LexMachina-Eval 100-case benchmark.")
    parser.add_argument("--bench", type=Path, default=ROOT_DIR / "evals" / "lexmachina_bench.jsonl")
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-md", type=Path, default=None)
    parser.add_argument("--min-pass-rate", type=float, default=0.85)
    args = parser.parse_args()

    cases = [
        json.loads(line)
        for line in args.bench.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    by_category: dict[str, dict[str, int]] = {}
    details: list[dict[str, Any]] = []
    passed_total = 0

    for case in cases:
        ok, detail = evaluate_case(case)
        cat = case["category"]
        bucket = by_category.setdefault(cat, {"passed": 0, "total": 0})
        bucket["total"] += 1
        if ok:
            bucket["passed"] += 1
            passed_total += 1
        details.append({
            "id": case["id"],
            "category": cat,
            "tool": case["tool"],
            "passed": ok,
            "detail": detail,
        })

    pass_rate = passed_total / max(1, len(cases))
    scorecard = {
        "benchmark": "LexMachina-Eval v2.0",
        "executed_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_cases": len(cases),
        "passed": passed_total,
        "failed": len(cases) - passed_total,
        "pass_rate_pct": round(pass_rate * 100.0, 2),
        "by_category": {
            cat: {
                **counts,
                "pass_rate_pct": round(100.0 * counts["passed"] / max(1, counts["total"]), 2),
            }
            for cat, counts in by_category.items()
        },
        "failures": [d for d in details if not d["passed"]],
    }

    md_lines = [
        "# LexMachina-Eval v2.0 — Empirical Verification Scorecard",
        "",
        f"- **Executed (UTC)**: `{scorecard['executed_utc']}`",
        f"- **Overall Score**: **{scorecard['passed']} / {scorecard['total_cases']} ({scorecard['pass_rate_pct']}%)**",
        "",
        "| Benchmark Category | Passed | Total | Pass Rate |",
        "| :--- | ---: | ---: | ---: |",
    ]
    for cat, stats in scorecard["by_category"].items():
        md_lines.append(f"| `{cat}` | {stats['passed']} | {stats['total']} | **{stats['pass_rate_pct']}%** |")

    if scorecard["failures"]:
        md_lines.extend(["", "## Failures", ""])
        for f in scorecard["failures"]:
            md_lines.append(f"- `{f['id']}` (`{f['tool']}`): {f['detail']}")

    md_text = "\n".join(md_lines) + "\n"
    print(md_text)

    if args.output_json:
        args.output_json.write_text(json.dumps(scorecard, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        args.output_md.write_text(md_text, encoding="utf-8")

    if pass_rate < args.min_pass_rate:
        print(
            f"ERROR: Pass rate {pass_rate:.2%} below minimum threshold {args.min_pass_rate:.2%}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
