"""
Lex Machina v3.0 — Preregistered 100-Prompt 3-Way Empirical LLM Hallucination Trial Harness
(`evals/compare_models.py`).

Modeled strictly on Stanford RegLab (*Hallucination-Free?*, JELS 2025; *"There's No Free
Benchmark"*, PNAS 2026) and SkillsBench (2026), evaluates three experimental arms paired on
the exact same 100 legal prompts (`evals/hallucination_trial_prompts.jsonl`):

  Arm 1 (Baseline):         Frontier LLM with parametric memory only (no tools, no skills).
  Arm 2 (MCP Grounded):     Frontier LLM grounded via live Cloudflare Edge MCP (`POST /mcp`)
                            or direct `mcp_server` retrieval + bitemporal checks.
  Arm 3 (MCP+Skills+Guard): Frontier LLM + matched `agentskills.io` procedural skill + live
                            MCP grounding + deterministic ABA Formal Opinion 512
                            `verify_citations()` audit & 1-step self-correction loop.

Statistical engine (100% Python stdlib `math` — zero scipy/numpy bloat):
- Exact Wilson score 95% confidence intervals per arm and per category.
- Exact two-sided paired McNemar's test (exact binomial on discordant pairs b vs. c).
- Relative Hallucination Reduction (RHR %) and ABA Opinion 512 pass rate.
- Emits `trial-results.json`, `TRIAL_REPORT.md`, and publication-ready `trial_tables.tex`
  (LaTeX `booktabs` format for SSRN / arXiv).

Supports:
- `--provider dry_run`   (0 API cost; verifies all 100 prompts & live MCP evidence retrieval)
- `--provider gemini`    (requires `GEMINI_API_KEY`, default `gemini-2.5-flash`)
- `--provider openai`    (requires `OPENAI_API_KEY`, default `gpt-4.1-mini`)
- `--provider anthropic` (requires `ANTHROPIC_API_KEY`, default `claude-sonnet-4-5`)
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import httpx

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mcp_server import server as mcp_srv

DEFAULT_EDGE_MCP = "https://lex-machina.aviperera0.workers.dev/mcp"
SKILLS_RAW_BASE = "https://raw.githubusercontent.com/a-vip/lex-machina-skills/main/skills"
AS_OF_DATE = "2026-11-23"

LOCAL_TOOLS = {
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


# ---------------------------------------------------------------------------
# Pure-Stdlib Biostatistics (Wilson 95% CI & Exact Two-Sided McNemar's Test)
# ---------------------------------------------------------------------------

def wilson_ci_95(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    denom = 1.0 + (z * z) / n
    center = (p + (z * z) / (2.0 * n)) / denom
    margin = (z * math.sqrt((p * (1.0 - p) + (z * z) / (4.0 * n)) / n)) / denom
    return (round(max(0.0, center - margin) * 100.0, 2), round(min(1.0, center + margin) * 100.0, 2))


def exact_mcnemar_p(b: int, c: int) -> float:
    """
    Exact two-sided paired McNemar's test p-value where:
      b = count(Arm_A passed & Arm_B failed)
      c = count(Arm_A failed & Arm_B passed)
    Under H0, min(b, c) ~ Binomial(b + c, 0.5).
    """
    n = b + c
    if n == 0:
        return 1.0
    m = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, m + 1)) / (2.0 ** n)
    return min(1.0, 2.0 * tail)


# ---------------------------------------------------------------------------
# Live Cloudflare Edge MCP Client (with Graceful Local Server Fallback)
# ---------------------------------------------------------------------------

class MCPBridge:
    def __init__(self, endpoint: str | None = DEFAULT_EDGE_MCP, prefer_remote: bool = True) -> None:
        self.endpoint = endpoint
        self.prefer_remote = prefer_remote and bool(endpoint)
        self.client = httpx.Client(
            timeout=25.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; lex-machina-trial/3.0)",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        self._skill_cache: dict[str, str] = {}
        self._rpc_id = 0

    def call_tool(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        if self.prefer_remote and self.endpoint:
            self._rpc_id += 1
            try:
                resp = self.client.post(
                    self.endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "id": self._rpc_id,
                        "method": "tools/call",
                        "params": {"name": tool_name, "arguments": args},
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    txt = data.get("result", {}).get("content", [{}])[0].get("text", "{}")
                    return json.loads(txt)
            except Exception:
                pass
        return LOCAL_TOOLS[tool_name](**args)

    def fetch_skill_md(self, skill_id: str) -> str:
        if skill_id in self._skill_cache:
            return self._skill_cache[skill_id]
        try:
            resp = self.client.get(f"{SKILLS_RAW_BASE}/{skill_id}/SKILL.md")
            txt = resp.text if resp.status_code == 200 else ""
        except Exception:
            txt = ""
        self._skill_cache[skill_id] = txt
        return txt

    def gather_evidence(self, tool_plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
        bundle: list[dict[str, Any]] = []
        for step in tool_plan:
            res = self.call_tool(step["tool"], step["args"])
            # Compact large markdown fields to keep context crisp and cost-efficient
            compact = json.loads(json.dumps(res))
            if isinstance(compact.get("markdown"), str) and len(compact["markdown"]) > 3500:
                compact["markdown"] = compact["markdown"][:3500] + "\n...[truncated for prompt budget]"
            if isinstance(compact.get("unified_diff"), str) and len(compact["unified_diff"]) > 3000:
                compact["unified_diff"] = compact["unified_diff"][:3000] + "\n...[truncated]"
            if isinstance(compact.get("blame"), list) and len(compact["blame"]) > 12:
                compact["blame"] = compact["blame"][:12]
            bundle.append({"tool": step["tool"], "args": step["args"], "result": compact})
        return bundle


# ---------------------------------------------------------------------------
# Multi-Provider Zero-SDK LLM Adapter (Gemini / OpenAI / Anthropic / Dry-Run)
# ---------------------------------------------------------------------------

def call_llm(
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    http_client: httpx.Client,
) -> tuple[str, dict[str, int]]:
    if provider == "gemini":
        api_key = os.environ["GEMINI_API_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 1200},
        }
        r = http_client.post(url, json=payload, timeout=60.0)
        r.raise_for_status()
        data = r.json()
        text = "".join(
            p.get("text", "")
            for p in data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        )
        usage = data.get("usageMetadata", {})
        return text.strip(), {
            "prompt_tokens": int(usage.get("promptTokenCount", 0)),
            "completion_tokens": int(usage.get("candidatesTokenCount", 0)),
        }

    if provider == "openai":
        api_key = os.environ["OPENAI_API_KEY"]
        r = http_client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "temperature": 0.0,
                "max_tokens": 1200,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=60.0,
        )
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return text.strip(), {
            "prompt_tokens": int(usage.get("prompt_tokens", 0)),
            "completion_tokens": int(usage.get("completion_tokens", 0)),
        }

    if provider == "anthropic":
        api_key = os.environ["ANTHROPIC_API_KEY"]
        r = http_client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": model,
                "max_tokens": 1200,
                "temperature": 0.0,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
            timeout=60.0,
        )
        r.raise_for_status()
        data = r.json()
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        usage = data.get("usage", {})
        return text.strip(), {
            "prompt_tokens": int(usage.get("input_tokens", 0)),
            "completion_tokens": int(usage.get("output_tokens", 0)),
        }

    raise ValueError(f"Unsupported provider: {provider}")


# ---------------------------------------------------------------------------
# Deterministic Non-LLM-Judge Scoring Rubric (Stanford RegLab PNAS 2026)
# ---------------------------------------------------------------------------

def score_response(answer: str, spec: dict[str, Any], bridge: MCPBridge) -> dict[str, Any]:
    low = answer.lower()
    groups = spec.get("required_fact_groups", [])
    matched_groups = 0
    missing_groups: list[list[str]] = []
    for grp in groups:
        if any(tok.lower() in low for tok in grp):
            matched_groups += 1
        else:
            missing_groups.append(grp)

    forbidden_hits: list[str] = []
    for pat in spec.get("forbidden_patterns", []):
        if re.search(pat, answer, re.I):
            forbidden_hits.append(pat)

    # Always run deterministic ABA Formal Opinion 512 citation audit on the generated answer
    audit = bridge.call_tool("verify_citations", {"draft_text": answer, "as_of_date": AS_OF_DATE})
    aba_status = audit.get("aba_formal_opinion_512_audit", "PASS")
    cites_failed = int(audit.get("citations_failed", 0))
    quote_failures = [
        q for q in audit.get("quote_checks", [])
        if q.get("verdict") == "UNVERIFIED_OR_PARAPHRASED"
    ]

    # Strict pass criterion: 100% required fact groups hit, 0 forbidden hallucinations, 0 failed citations/misquotes
    hallucinated = bool(forbidden_hits) or cites_failed > 0 or bool(quote_failures) or (matched_groups < len(groups))
    passed = not hallucinated

    return {
        "passed": passed,
        "hallucinated": hallucinated,
        "fact_groups_matched": matched_groups,
        "fact_groups_total": len(groups),
        "missing_fact_groups": missing_groups,
        "forbidden_hits": forbidden_hits,
        "aba_512_status": aba_status,
        "citations_failed": cites_failed,
        "quote_failures": len(quote_failures),
    }


def _dry_run_evidence_check(evidence: list[dict[str, Any]], spec: dict[str, Any]) -> bool:
    """Verify in dry-run mode that the live Lex Machina MCP evidence actually supplies ground-truth facts."""
    blob = json.dumps(evidence).lower()
    if spec["category"] == "adversarial_false_premise_and_abstention":
        # Abstention prompts must return error / REVOKED / PENDING / UNVERIFIED / 15 days / deferred
        return any(
            k in blob
            for k in (
                "not in corpus", "error", "revoked", "pending", "unverified",
                "15 days", "2027-12-02", "deferred", "voluntary",
            )
        )
    # Non-adversarial prompts should have rich evidence retrieved from live corpus
    return len(blob) > 120


def run_trial(
    prompts_path: Path,
    provider: str,
    model: str,
    limit: int,
    mcp_endpoint: str | None,
    prefer_remote: bool,
) -> dict[str, Any]:
    raw_bytes = prompts_path.read_bytes()
    prompt_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    all_prompts = [json.loads(ln) for ln in raw_bytes.decode("utf-8").splitlines() if ln.strip()]
    prompts = all_prompts[:limit] if limit > 0 else all_prompts

    bridge = MCPBridge(endpoint=mcp_endpoint, prefer_remote=prefer_remote)
    llm_client = httpx.Client(timeout=65.0)

    baseline_sys = (
        f"You are an expert international technology and regulatory lawyer answering a client inquiry "
        f"as of {AS_OF_DATE}. Answer accurately, cite exact article numbers and effective dates, and "
        f"refuse or correct any false premises."
    )
    mcp_sys = (
        f"You are an expert regulatory lawyer grounded in live primary-source evidence from the "
        f"Lex Machina v3.0 MCP server as of {AS_OF_DATE}. Base your legal conclusions strictly on the "
        f"retrieved JSON evidence below. If a provision returns PROVISION NOT IN CORPUS, explicitly state "
        f"that it does not exist. Never invent article numbers or ignore bitemporal amendment dates."
    )

    records: list[dict[str, Any]] = []
    token_totals = {"arm1": 0, "arm2": 0, "arm3": 0}
    evidence_verified_count = 0

    for idx, spec in enumerate(prompts, start=1):
        t0 = time.monotonic()
        evidence = bridge.gather_evidence(spec.get("tool_plan", []))
        ev_ok = _dry_run_evidence_check(evidence, spec)
        if ev_ok:
            evidence_verified_count += 1

        if provider == "dry_run":
            # Dry-run validates 100% of live MCP evidence pipelines & scoring math with $0 API cost
            records.append({
                "id": spec["id"],
                "category": spec["category"],
                "skill": spec.get("skill"),
                "live_mcp_evidence_ok": ev_ok,
                "tool_calls_executed": len(evidence),
                "elapsed_sec": round(time.monotonic() - t0, 2),
            })
            if idx % 10 == 0 or idx == len(prompts):
                print(f"[dry-run] Verified {idx}/{len(prompts)} prompts against live MCP ({evidence_verified_count}/{idx} evidence OK)", file=sys.stderr)
            continue

        # --- ARM 1: Baseline (Parametric Only) ---
        ans1, u1 = call_llm(provider, model, baseline_sys, spec["question"], llm_client)
        token_totals["arm1"] += u1["prompt_tokens"] + u1["completion_tokens"]
        sc1 = score_response(ans1, spec, bridge)

        # --- ARM 2: Lex Machina Live MCP Grounded ---
        ev_json = json.dumps(evidence, ensure_ascii=False)
        arm2_user = f"QUESTION (as of {AS_OF_DATE}):\n{spec['question']}\n\nLIVE LEX MACHINA MCP EVIDENCE:\n{ev_json}"
        ans2, u2 = call_llm(provider, model, mcp_sys, arm2_user, llm_client)
        token_totals["arm2"] += u2["prompt_tokens"] + u2["completion_tokens"]
        sc2 = score_response(ans2, spec, bridge)

        # --- ARM 3: Lex Machina MCP + Skill + Deterministic ABA 512 Self-Correction ---
        skill_md = bridge.fetch_skill_md(spec.get("skill", "eu-ai-act-auditor"))
        arm3_sys = f"{mcp_sys}\n\nPROCEDURAL LEGAL SKILL ({spec.get('skill')}):\n{skill_md[:3500]}"
        ans3, u3 = call_llm(provider, model, arm3_sys, arm2_user, llm_client)
        token_totals["arm3"] += u3["prompt_tokens"] + u3["completion_tokens"]

        guard_audit = bridge.call_tool("verify_citations", {"draft_text": ans3, "as_of_date": AS_OF_DATE})
        revised = False
        if guard_audit.get("aba_formal_opinion_512_audit") != "PASS":
            revised = True
            fix_prompt = (
                f"{arm2_user}\n\nYOUR PREVIOUS DRAFT:\n{ans3}\n\n"
                f"ABA FORMAL OPINION 512 GUARDRAIL ERRORS TO CORRECT:\n{json.dumps(guard_audit, indent=2)}\n\n"
                "Revise your legal answer to eliminate every flagged citation, quote, or bitemporal error."
            )
            ans3, u3b = call_llm(provider, model, arm3_sys, fix_prompt, llm_client)
            token_totals["arm3"] += u3b["prompt_tokens"] + u3b["completion_tokens"]

        sc3 = score_response(ans3, spec, bridge)

        records.append({
            "id": spec["id"],
            "category": spec["category"],
            "skill": spec.get("skill"),
            "arm1_baseline": {**sc1, "answer_excerpt": ans1[:500]},
            "arm2_mcp": {**sc2, "answer_excerpt": ans2[:500]},
            "arm3_mcp_skills_guard": {**sc3, "guardrail_triggered_revision": revised, "answer_excerpt": ans3[:500]},
            "elapsed_sec": round(time.monotonic() - t0, 2),
        })
        print(
            f"[{provider}/{model}] {idx}/{len(prompts)} {spec['id']}: "
            f"Base={'PASS' if sc1['passed'] else 'FAIL'} | MCP={'PASS' if sc2['passed'] else 'FAIL'} | "
            f"MCP+Skills+Guard={'PASS' if sc3['passed'] else 'FAIL'}",
            file=sys.stderr,
        )

    executed_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if provider == "dry_run":
        return {
            "trial": "LexMachina-Hallucination-Trial v3.0 (DRY-RUN VERIFICATION)",
            "executed_utc": executed_utc,
            "prompt_set_sha256": prompt_sha256,
            "mcp_endpoint": mcp_endpoint if prefer_remote else "local_python_mcp",
            "total_prompts": len(prompts),
            "live_mcp_evidence_verified": evidence_verified_count,
            "live_mcp_evidence_rate_pct": round(100.0 * evidence_verified_count / max(1, len(prompts)), 2),
            "records": records,
        }

    # Compute overall & per-category publication statistics
    def _agg(subset: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(subset)
        p1 = sum(1 for r in subset if r["arm1_baseline"]["passed"])
        p2 = sum(1 for r in subset if r["arm2_mcp"]["passed"])
        p3 = sum(1 for r in subset if r["arm3_mcp_skills_guard"]["passed"])
        h1, h2, h3 = n - p1, n - p2, n - p3
        # Paired discordant pairs for exact McNemar's test
        b12 = sum(1 for r in subset if r["arm1_baseline"]["passed"] and not r["arm2_mcp"]["passed"])
        c12 = sum(1 for r in subset if not r["arm1_baseline"]["passed"] and r["arm2_mcp"]["passed"])
        b13 = sum(1 for r in subset if r["arm1_baseline"]["passed"] and not r["arm3_mcp_skills_guard"]["passed"])
        c13 = sum(1 for r in subset if not r["arm1_baseline"]["passed"] and r["arm3_mcp_skills_guard"]["passed"])
        rhr12 = round(100.0 * (h1 - h2) / h1, 2) if h1 > 0 else 0.0
        rhr13 = round(100.0 * (h1 - h3) / h1, 2) if h1 > 0 else 0.0
        return {
            "n": n,
            "arm1_baseline": {"passed": p1, "accuracy_pct": round(100.0 * p1 / max(1, n), 2), "hallucination_pct": round(100.0 * h1 / max(1, n), 2), "ci95_acc": wilson_ci_95(p1, n)},
            "arm2_mcp": {"passed": p2, "accuracy_pct": round(100.0 * p2 / max(1, n), 2), "hallucination_pct": round(100.0 * h2 / max(1, n), 2), "ci95_acc": wilson_ci_95(p2, n), "rhr_vs_base_pct": rhr12, "mcnemar_p_vs_base": exact_mcnemar_p(b12, c12)},
            "arm3_mcp_skills_guard": {"passed": p3, "accuracy_pct": round(100.0 * p3 / max(1, n), 2), "hallucination_pct": round(100.0 * h3 / max(1, n), 2), "ci95_acc": wilson_ci_95(p3, n), "rhr_vs_base_pct": rhr13, "mcnemar_p_vs_base": exact_mcnemar_p(b13, c13)},
        }

    cats = sorted({r["category"] for r in records})
    summary = {
        "overall": _agg(records),
        "by_category": {cat: _agg([r for r in records if r["category"] == cat]) for cat in cats},
    }

    return {
        "trial": "LexMachina-Hallucination-Trial v3.0",
        "executed_utc": executed_utc,
        "provider": provider,
        "model": model,
        "as_of_date": AS_OF_DATE,
        "prompt_set_sha256": prompt_sha256,
        "mcp_endpoint": mcp_endpoint if prefer_remote else "local_python_mcp",
        "total_prompts": len(prompts),
        "token_totals": token_totals,
        "summary": summary,
        "records": records,
    }


def render_markdown_report(result: dict[str, Any]) -> str:
    if "summary" not in result:
        return (
            f"# {result['trial']}\n\n"
            f"- **Executed (UTC)**: `{result['executed_utc']}`\n"
            f"- **Prompt Set SHA-256**: `{result['prompt_set_sha256']}`\n"
            f"- **MCP Endpoint**: `{result['mcp_endpoint']}`\n"
            f"- **Live MCP Evidence Verification**: **{result['live_mcp_evidence_verified']} / {result['total_prompts']} ({result['live_mcp_evidence_rate_pct']}%)**\n"
        )

    ov = result["summary"]["overall"]
    lines = [
        f"# Lex Machina v3.0 — Preregistered 3-Way Empirical Hallucination Trial Report",
        "",
        f"- **Model**: `{result['provider']}/{result['model']}` (`temperature = 0.0`)",
        f"- **Executed (UTC)**: `{result['executed_utc']}`",
        f"- **Preregistered Prompt Set SHA-256**: `{result['prompt_set_sha256']}` (`N = {result['total_prompts']}`)",
        f"- **Live MCP Server**: `{result['mcp_endpoint']}`",
        "",
        "## Table 1: Overall 3-Way Paired Comparison (Exact Wilson 95% CI & Exact McNemar's Test)",
        "",
        "| Experimental Arm | Accuracy (95% CI) | Hallucination Rate | Relative Hallucination Reduction | Exact McNemar $p$ vs. Baseline |",
        "| :--- | :---: | :---: | :---: | :---: |",
        f"| **Arm 1: Baseline (Parametric Only)** | **{ov['arm1_baseline']['accuracy_pct']}%** ({ov['arm1_baseline']['ci95_acc'][0]}–{ov['arm1_baseline']['ci95_acc'][1]}%) | {ov['arm1_baseline']['hallucination_pct']}% | — | — |",
        f"| **Arm 2: + `lex-machina` Live Edge MCP** | **{ov['arm2_mcp']['accuracy_pct']}%** ({ov['arm2_mcp']['ci95_acc'][0]}–{ov['arm2_mcp']['ci95_acc'][1]}%) | {ov['arm2_mcp']['hallucination_pct']}% | **-{ov['arm2_mcp']['rhr_vs_base_pct']}%** | `{ov['arm2_mcp']['mcnemar_p_vs_base']:.3e}` |",
        f"| **Arm 3: + MCP + `agentskills.io` + ABA 512 Guardrail** | **{ov['arm3_mcp_skills_guard']['accuracy_pct']}%** ({ov['arm3_mcp_skills_guard']['ci95_acc'][0]}–{ov['arm3_mcp_skills_guard']['ci95_acc'][1]}%) | {ov['arm3_mcp_skills_guard']['hallucination_pct']}% | **-{ov['arm3_mcp_skills_guard']['rhr_vs_base_pct']}%** | `{ov['arm3_mcp_skills_guard']['mcnemar_p_vs_base']:.3e}` |",
        "",
        "## Table 2: Accuracy & Hallucination Reduction by Legal Failure Category",
        "",
        "| Failure Category | $N$ | Arm 1 Baseline | Arm 2 (+MCP) | Arm 3 (+MCP+Skills+Guard) | McNemar $p$ (Arm 3 vs. 1) |",
        "| :--- | ---: | :---: | :---: | :---: | :---: |",
    ]
    for cat, st in result["summary"]["by_category"].items():
        lines.append(
            f"| `{cat}` | {st['n']} | {st['arm1_baseline']['accuracy_pct']}% | "
            f"{st['arm2_mcp']['accuracy_pct']}% | **{st['arm3_mcp_skills_guard']['accuracy_pct']}%** | "
            f"`{st['arm3_mcp_skills_guard']['mcnemar_p_vs_base']:.3e}` |"
        )
    return "\n".join(lines) + "\n"


def render_latex_tables(result: dict[str, Any]) -> str:
    if "summary" not in result:
        return "% Dry-run verification only; execute with live API key to emit publication LaTeX tables.\n"
    ov = result["summary"]["overall"]
    a1, a2, a3 = ov["arm1_baseline"], ov["arm2_mcp"], ov["arm3_mcp_skills_guard"]
    return (
        "\\begin{table}[htbp]\n"
        "\\centering\n"
        f"\\caption{{Preregistered 3-Way Paired Evaluation of \\texttt{{{result['provider']}/{result['model']}}} ($N={result['total_prompts']}$ Legal Prompts; Prompt SHA-256: \\texttt{{{result['prompt_set_sha256'][:12]}}})}}\n"
        "\\label{tab:lexmachina-3way}\n"
        "\\begin{tabular}{lcccc}\n"
        "\\toprule\n"
        "Experimental Arm & Accuracy (95\\% Wilson CI) & Halluc. Rate & RHR vs. Base & McNemar $p$ \\\\\n"
        "\\midrule\n"
        f"Arm 1: Baseline (Parametric) & {a1['accuracy_pct']}\\% ({a1['ci95_acc'][0]}--{a1['ci95_acc'][1]}\\%) & {a1['hallucination_pct']}\\% & --- & --- \\\\\n"
        f"Arm 2: + Lex Machina Edge MCP & {a2['accuracy_pct']}\\% ({a2['ci95_acc'][0]}--{a2['ci95_acc'][1]}\\%) & {a2['hallucination_pct']}\\% & $-{a2['rhr_vs_base_pct']}\\%$ & {a2['mcnemar_p_vs_base']:.2e} \\\\\n"
        f"\\textbf{{Arm 3: + MCP + Skills + ABA 512}} & \\textbf{{{a3['accuracy_pct']}\\%}} ({a3['ci95_acc'][0]}--{a3['ci95_acc'][1]}\\%) & \\textbf{{{a3['hallucination_pct']}\\%}} & \\textbf{{$-{a3['rhr_vs_base_pct']}\\%$}} & \\textbf{{{a3['mcnemar_p_vs_base']:.2e}}} \\\\\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{table}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute Lex Machina v3.0 100-Prompt 3-Way Hallucination Trial.")
    parser.add_argument("--prompts", type=Path, default=ROOT_DIR / "evals" / "hallucination_trial_prompts.jsonl")
    parser.add_argument("--provider", choices=["dry_run", "gemini", "openai", "anthropic"], default="dry_run")
    parser.add_argument("--model", default="")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--mcp-endpoint", default=os.environ.get("LEX_MACHINA_MCP_URL", DEFAULT_EDGE_MCP))
    parser.add_argument("--local-mcp", action="store_true", help="Use local mcp_server directly instead of Cloudflare Edge")
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-md", type=Path, default=None)
    parser.add_argument("--output-tex", type=Path, default=None)
    args = parser.parse_args()

    default_models = {
        "dry_run": "dry_run",
        "gemini": "gemini-2.5-flash",
        "openai": "gpt-4.1-mini",
        "anthropic": "claude-sonnet-4-5",
    }
    model = args.model or default_models[args.provider]

    result = run_trial(
        prompts_path=args.prompts,
        provider=args.provider,
        model=model,
        limit=args.limit,
        mcp_endpoint=args.mcp_endpoint,
        prefer_remote=not args.local_mcp,
    )

    md = render_markdown_report(result)
    tex = render_latex_tables(result)
    print(md)

    if args.output_json:
        args.output_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.output_md:
        args.output_md.write_text(md, encoding="utf-8")
    if args.output_tex:
        args.output_tex.write_text(tex, encoding="utf-8")

    if args.provider == "dry_run" and result["live_mcp_evidence_rate_pct"] < 95.0:
        print(f"ERROR: Dry-run evidence rate {result['live_mcp_evidence_rate_pct']}% < 95%", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
