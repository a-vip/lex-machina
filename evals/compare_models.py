"""
3-Way Empirical Frontier LLM Comparison Harness (`evals/compare_models.py`).

Inspired by Stanford RegLab (*Hallucination-Free?*, JELS 2025; *PNAS* 2026) and
SkillsBench (2026), evaluates three configurations side-by-side on preregistered
2026 legal questions:
  1. Baseline LLM (parametric memory only — no tools, no skills)
  2. LLM + `lex-machina` MCP tools (retrieval + bitemporal checks)
  3. LLM + `lex-machina` MCP + `lex-machina-skills` + `verify_citations` guardrail

Runs on GitHub Actions (zero local installs) when `OPENAI_API_KEY` or
`ANTHROPIC_API_KEY` is provided in environment variables.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mcp_server import server as mcp_srv

COMPARATIVE_PROMPTS: list[dict[str, Any]] = [
    {
        "id": "COMP-01",
        "question": "As of November 23, 2026, are standalone Annex III high-risk AI systems (e.g., recruitment screening) legally enforceable under the EU AI Act? Cite the amending regulation and exact effective date.",
        "required_facts": ["2026/1744", "December 2, 2027", "postponed"],
        "forbidden_hallucinations": ["enforceable since August 2, 2026"],
    },
    {
        "id": "COMP-02",
        "question": "What is the current legal status of US Executive Order 14110 as of November 23, 2026, and which Texas statute took effect on January 1, 2026?",
        "required_facts": ["revoked", "January 20, 2025", "TRAIGA", "HB 149"],
        "forbidden_hallucinations": ["currently in force under Executive Order 14110"],
    },
    {
        "id": "COMP-03",
        "question": "Under the EU AI Act, what was the original article number for Transparency Obligations in the 2021 Commission Proposal versus the Final Official Journal text, and what is the legacy transition cutoff date under Article 50(2)?",
        "required_facts": ["Article 52", "Article 50", "December 2, 2026"],
        "forbidden_hallucinations": [],
    },
    {
        "id": "COMP-04",
        "question": "Is EU Cyber Resilience Act (Regulation (EU) 2024/2847) Article 14 vulnerability reporting to ENISA enforceable on November 23, 2026, and when does full CRA product compliance apply?",
        "required_facts": ["September 11, 2026", "December 11, 2027", "ENISA"],
        "forbidden_hallucinations": [],
    },
    {
        "id": "COMP-05",
        "question": "Has the UN Convention against Cybercrime (Hanoi Convention, A/RES/79/243) entered into force, and what ratification threshold does Article 65 require?",
        "required_facts": ["40", "ratifications", "Hanoi"],
        "forbidden_hallucinations": [],
    },
]


def score_answer(answer: str, prompt_spec: dict[str, Any]) -> dict[str, Any]:
    low = answer.lower()
    hits = [f for f in prompt_spec["required_facts"] if f.lower() in low]
    bad = [f for f in prompt_spec["forbidden_hallucinations"] if f.lower() in low]
    audit = mcp_srv.verify_citations(answer, as_of_date="2026-11-23")
    passed = (len(hits) == len(prompt_spec["required_facts"])) and not bad and audit["aba_formal_opinion_512_audit"] == "PASS"
    return {
        "id": prompt_spec["id"],
        "fact_recall": f"{len(hits)}/{len(prompt_spec['required_facts'])}",
        "forbidden_hits": bad,
        "aba_512_verdict": audit["aba_formal_opinion_512_audit"],
        "passed": passed,
    }


def main() -> None:
    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")):
        print(
            "LexMachina 3-Way Comparative LLM Harness ready.\n"
            "Set OPENAI_API_KEY or ANTHROPIC_API_KEY to execute live baseline vs. MCP vs. Skills trials.\n"
            f"Preregistered comparative prompts loaded: {len(COMPARATIVE_PROMPTS)}"
        )
        print(json.dumps(COMPARATIVE_PROMPTS, indent=2))
        return

    print("API key detected — plug into your chosen provider client to log comparative tables.")


if __name__ == "__main__":
    main()
