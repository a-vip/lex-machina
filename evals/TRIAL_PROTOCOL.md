# Lex Machina v3.0 — Preregistered 3-Way Empirical Legal Hallucination Trial Protocol

**Study Identifier**: `LexMachina-Trial-2026-v3`  
**Preregistered Prompt Corpus**: `evals/hallucination_trial_prompts.jsonl` ($N = 100$ prompts across 5 strata)  
**Target Journals / Preprint Archives**: SSRN Legal Scholarship Network · arXiv (`cs.CL` / `cs.CY`)  
**Methodological Anchors**: Stanford RegLab (*Hallucination-Free?*, *JELS* 2025; *"There's No Free Benchmark"*, *PNAS* 2026) · SkillsBench (2026) · ABA Formal Opinion 512 (2024)

---

## 1. Study Objective & Preregistered Hypotheses

Commercial legal AI platforms (Lexis+ AI ~17%, Westlaw AI ~33%) exhibit persistent **misgrounding**, **temporal collapse**, and **false-premise acquiescence**. This study tests whether coupling frontier LLMs with a **bitemporal, SHA-256-provenanced Git corpus MCP server**, **modular `agentskills.io` legal skills**, and a **deterministic ABA Formal Opinion 512 verification loop** produces statistically significant reductions in legal hallucination rates.

- **$H_1$ (MCP Grounding Effect)**: Arm 2 (`LLM + Lex Machina Live Edge MCP`) achieves significantly higher overall accuracy and lower hallucination rate than Arm 1 (`Baseline Parametric LLM`) on paired two-sided exact McNemar's test ($\alpha = 0.01$).
- **$H_2$ (Skills + Deterministic Guardrail Effect)**: Arm 3 (`LLM + Edge MCP + agentskills.io + ABA 512 Verifier Loop`) achieves the highest overall accuracy, highest ABA Formal Opinion 512 citation-audit pass rate, and lowest false-premise acquiescence rate across all 5 legal failure strata.
- **$H_3$ (Bitemporal Dominance)**: The largest accuracy delta occurs on **Category 1 (`bitemporal_2025_2026_traps`)** and **Category 2 (`travaux_concordance_and_blame`)**, where parametric cutoff memory and monotemporal RAG fail systematically.

---

## 2. Stratified 100-Prompt Dataset Design (`N = 100`)

| Stratum | IDs | Count | Legal Failure Mode Tested |
| :--- | :---: | :---: | :--- |
| **1. Bitemporal 2025–2026 Traps** | `HT-001` – `HT-020` | 20 | EU Digital Omnibus `2026/1744` postponements, legacy grace cutoffs, US `EO 14110` Jan 2025 revocation, Texas TRAIGA Jan 2026, China `GB 45438-2025`, South Korea Jan 2026, Japan Sept 2025, Brazil `PL 2338` pending status, EU CRA/DORA/NIS2, UN Hanoi 40-ratification gate |
| **2. Travaux Concordance & Blame** | `HT-021` – `HT-040` | 20 | Cross-draft renumbering (EU AI Act Prop. Art. 52→50, 62→73, 71→99, Parl. 29a→27, 28b→51/53/55; GDPR 20→22, 33→35, 35→37; CoE 4→2, 11→8), token-level institutional authorship, linked recitals |
| **3. Adversarial False-Premise & Abstention** | `HT-041` – `HT-060` | 20 | Fabricated article numbers (`EU AI Act Art. 128`, `GDPR Art. 145`, `CRA Art. 999`, `NIS2 Art. 404`, `DORA Art. 888`, `AP I Art. 299`, `AP II Art. 99`, `CETS 225 Art. 99`), fabricated quotes, false 72h Art. 73 clock, active-EO-14110 / enacted-PL-2338 traps |
| **4. Verbatim Statutory & IHL Precision** | `HT-061` – `HT-080` | 20 | Exact clauses of AP I Arts. 36/48/51/57, GC IV Art. 147, Common Art. 3, GC III Art. 13, AP II Art. 13, CCW Guiding Principle (a), AI Act Arts. 6(3)/51/53/55/73/99, CRA Art. 14, NIS2 Art. 23, Budapest Art. 15, NIST RMF, GDPR Art. 83(5) |
| **5. Judicial Precedent & Planetary Crosswalk** | `HT-081` – `HT-100` | 20 | Binding CJEU (*SCHUFA* C-634/21, *Schrems II* C-311/18, *Meta* C-252/21, *La Quadrature du Net* C-511/18), ICJ 1996 *Nuclear Weapons* (Martens Clause), ISO/IEC 42001, UK DUAA 2025, Korea/Japan/Singapore/US State/China harmonization |

---

## 3. Experimental Arms & Deterministic Scoring (Zero LLM-as-Judge Bias)

Every prompt is evaluated at **`temperature = 0.0`** across three paired arms:
1. **Arm 1 — Baseline**: Frontier model using parametric memory alone.
2. **Arm 2 — `+ Lex Machina Live Edge MCP`**: Model grounded in real-time JSON responses fetched from `https://lex-machina.aviperera0.workers.dev/mcp`.
3. **Arm 3 — `+ MCP + agentskills.io + ABA 512 Self-Correction`**: Model given the domain-matched `SKILL.md` from `a-vip/lex-machina-skills` + live Edge MCP evidence + deterministic `verify_citations()` audit triggering an automated correction pass if any error or warning fires.

**Strict Non-LLM Scoring Rule**: To eliminate circular LLM-as-a-judge bias highlighted in Stanford RegLab (*PNAS* 2026), an answer is marked **`PASS`** if and only if:
1. Every preregistered `required_fact_group` matches at least one canonical legal phrasing variant;
2. Zero `forbidden_patterns` (known hallucination signatures) match; AND
3. `verify_citations(answer, as_of_date="2026-11-23")` returns zero fabricated article citations and zero misquoted statutory excerpts.

---

## 4. Statistical Plan & Cloud Execution

- **Point estimates**: Accuracy % and Hallucination Rate (`100% - Accuracy %`) with **exact Wilson 95% confidence intervals**.
- **Hypothesis tests**: Exact two-sided paired **McNemar's test** on discordant pairs $(b, c)$ comparing Arm 2 vs. Arm 1 and Arm 3 vs. Arm 1.
- **Reproducibility**: Executed exclusively on GitHub Actions via `.github/workflows/06-run-llm-hallucination-trial.yml` (`workflow_dispatch`), pinning the SHA-256 digest of `hallucination_trial_prompts.jsonl` and emitting `trial-results.json`, `TRIAL_REPORT.md`, and LaTeX `trial_tables.tex`.

### How to Execute a Live Paid Trial (Takes ~3–5 Minutes on GitHub Actions)
1. In GitHub (`a-vip/lex-machina → Settings → Secrets and variables → Actions`), add any one (or all three) provider API keys:
   - `GEMINI_API_KEY` (recommended lowest cost — `gemini-2.5-flash` runs all 300 calls for < \$0.50!)
   - `OPENAI_API_KEY` (e.g., `gpt-4.1-mini` or `gpt-4.1`)
   - `ANTHROPIC_API_KEY` (e.g., `claude-sonnet-4-5`)
2. Open **Actions → `06 - Run 3-Way LLM Hallucination Trial` → Run workflow**, choose `provider`, `model`, `sample_size = 100`, and `publish_to_corpus = true`.
3. Download `TRIAL_REPORT.md` and `trial_tables.tex` directly from the workflow artifact (or `refs/heads/corpus/trials/`) and paste Table 1 & Table 2 directly into `WHITEPAPER.md` for SSRN / arXiv submission!
