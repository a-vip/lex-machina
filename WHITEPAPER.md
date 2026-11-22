# Lex Machina: Bitemporal Git Provenance, Concordance-Aware Institutional Attribution, and Deterministic Citation Verification for Agentic Legal Reasoning

**Technical Architecture & Empirical Methodology Whitepaper (Edition 2026.11)**  
*Avi Perera / Lex Machina Consortium — `a-vip/lex-machina` & `a-vip/lex-machina-skills`*

---

## Abstract

Empirical audits of commercial Retrieval-Augmented Generation (RAG) legal research tools—most notably **Stanford RegLab's** preregistered evaluations (*Hallucination-Free?*, *Journal of Empirical Legal Studies*, 2025; *Benchmarking Legal RAG*, 2026; *"There's No Free Benchmark"*, *PNAS*, 2026)—demonstrate that proprietary legal AI platforms continue to exhibit 17%–33% hallucination rates, driven largely by **misgrounding** (citing real statutes that fail to support the asserted proposition) and poor performance (58%–64%) on multi-jurisdictional statutory surveys. Separately, **SkillsBench (2026)** established that agentic performance leaps require concise, human-curated procedural skills paired with deterministic verification scripts rather than monolithic prompt dumps.

**Lex Machina** resolves these structural failure modes through a five-layer open legal-informatics architecture that no existing commercial publisher or open-source MCP server combines:
1. **Cryptographically Hashed Full-Text Primary Ingestion** via EUR-Lex CELLAR content negotiation (Akoma Ntoso `eId` XHTML), official diplomatic PDFs, and ICRC treaty databases, preserving raw SHA-256 digests and truthful `provenance_mode` labels.
2. **4-Column Normative Concordance & Token-Level Institutional `git blame`** mapping renumbered legal norms across legislative drafts (`Proposal → Council → Parliament → Trilogue → Official Journal → Amending Acts`) inside a `git fsck --strict` orphan branch.
3. **Bitemporal Legal Enforceability Modeling** separating *publication time* from *legal effect time* and *legacy system transition cutoffs* (explicitly encoding the 2026 EU Digital Omnibus Regulation (EU) 2026/1744, the Jan 20, 2025 revocation of US EO 14110, CRA 2026/2027 phases, Texas TRAIGA, China 2025 Labeling Measures, and the UN Hanoi Cybercrime 40-ratification threshold).
4. **Deterministic Citation & Verbatim Quote Verification (`verify_citations` + `PostToolUse` Guardrail Hook)** operationalizing **ABA Formal Opinion 512** (Model Rules 1.1, 1.6, 3.3, 5.1) under strict **Zero Data Retention (ZDR)**.
5. **Continuous Preregistered Open Benchmarking (`LexMachina-Eval`)** executing 100 automated tests across five legal-reasoning failure modes on every cloud corpus build.

---

## 1. Structural Failure Modes of Existing Legal AI Systems

1. **The Partial-Corpus & Misgrounding Failure**: Hardcoded summaries or incomplete chunk indices force frontier models to fall back to parametric memory whenever a lawyer queries deep operational clauses (e.g., EU AI Act Art. 73 serious incident windows or CRA Art. 14 vulnerability notifications).
2. **Temporal Collapse (Failure of Monotemporal RAG)**: Vector databases treat a 2023 Executive Order (EO 14110) and a 2024 enacted Regulation (original Aug 2, 2026 Annex III deadline) as timeless facts—failing catastrophically once EO 14110 is revoked (Jan 20, 2025) or Regulation (EU) 2026/1744 postpones Annex III enforcement to Dec 2, 2027.
3. **Renumbering Amnesia & Fragile Line-Level Diffs**: Traditional Git-ification of law (*Bundesgit*) fails on legislative *travaux préparatoires* because EU co-legislators routinely renumber articles between Proposal, Parliament Mandate, and Official Journal, and lawyer-linguist punctuation tweaks erase original institutional line-blame.
4. **Cross-Dialect Recall Loss**: EU, UN, and ICRC treaties employ British orthography (`categorisation`, `harmonised`, `defence`, `offence`), causing naive substring search engines to miss critical provisions when queried by US counsel (`categorization`, `harmonized`, `defense`, `offense`).
5. **Closed-Box Unverifiability**: Commercial vendors refuse to publish reproducible statutory benchmarks or primary-source cryptographic digests, leaving AmLaw 100 / Magic Circle ethics committees unable to audit compliance with ABA Formal Opinion 512.

---

## 2. System Architecture

### 2.1 Zero-Local-Disk Cloud Pipeline & Cryptographic Provenance
All ingestion, XML/XHTML DOM parsing (`BeautifulSoup` + `lxml`), PDF extraction (`pypdf`), BM25 indexing, SQLite FTS5 compilation, and `git fast-import` stream generation run exclusively on ephemeral GitHub Actions cloud runners (`ubuntu-latest`). The resulting history is pushed to remote-only orphan branches (`refs/heads/corpus` and `refs/heads/pipeline-cache`), keeping local developer repositories under 500 KB via `remote.origin.fetch = +refs/heads/main:refs/remotes/origin/main`.

Every ingested stage writes a cryptographic record to `provenance.json`:
- `sha256_raw`: SHA-256 digest of the exact upstream bytes fetched from CELLAR / Consilium / Europarl / UN / CoE / ICRC / NIST.
- `provenance_mode`: Honest classification (`full_primary_xhtml_akn`, `full_primary_pdf`, `full_primary_html`, or `structured_regulatory_brief`) so downstream agents never cite an analytical milestone summary as verbatim statute text.
- `eli` & `celex` & `final_url` & `fetched_utc`.

### 2.2 FRBR Concordance & Token-Level Institutional Attribution
Following OASIS Akoma Ntoso FRBR principles (Work → Expression → Manifestation), `concordance.json` assigns persistent normative IDs across renumbered drafts (e.g., `eu/ai-act` norm `transparency-obligations`: `52021PC0206` Art. 52 → `32024R1689` Art. 50; norm `fria`: `P9_TA(2023)0236` Art. 29a → `32024R1689` Art. 27; `eu/gdpr` norm `automated-decision-making`: `52012PC0011` Art. 20 → `32016R0679` Art. 22).

`blame_provision` aligns tokenized provision bodies sequentially across chronological stages via `difflib.SequenceMatcher`, computing exact institutional authorship shares per clause so lawyer-linguist punctuation edits never erase Commission, Council, or Parliament provenance.

### 2.3 Bitemporal Applicability Engine
`applicability.json` and `check_applicability(instrument_path, provision, as_of_date, placed_on_market_date)` evaluate three distinct temporal states:
1. `ENFORCEABLE`
2. `IN_FORCE_NOT_YET_APPLICABLE` (e.g., Annex III high-risk systems on Nov 23, 2026 under Regulation (EU) 2026/1744)
3. `LEGACY_TRANSITION_GRACE_PERIOD` (e.g., pre-Aug-2026 generative AI models under Art. 50(2) prior to Dec 2, 2026)
4. `REVOKED` (e.g., US EO 14110 on or after Jan 20, 2025)
5. `NOT_YET_IN_FORCE_PENDING_RATIFICATIONS` (e.g., UN Hanoi Cybercrime Convention awaiting 40 ratifications under Art. 65)

### 2.4 Stateless Zero-Data-Retention Edge MCP
`cloudflare_worker/src/index.ts` exposes the corpus over **MCP Streamable HTTP (`POST /mcp`)** globally at the edge with Cloudflare Cache API over `raw.githubusercontent.com` and `observability.enabled = false`—providing **strict Zero Data Retention (ZDR)** required under ABA Model Rule 1.6.

---

## 3. Preregistered Empirical Evaluation (`LexMachina-Eval`)

`evals/lexmachina_bench.jsonl` executes **100 deterministic legal verification cases** automatically on GitHub Actions (`03-run-legal-evals.yml`) after every corpus rebuild:
- **Category A (25 cases)**: Deep-article verbatim grounding across EU AI Act, GDPR, CRA, NIS2, DORA, CoE CETS 225, IHL AP I, and US State AI statutes.
- **Category B (20 cases)**: Concordance-resolved renumbering lookups, multi-stage diffs, linked recitals, and token-level institutional blame.
- **Category C (20 cases)**: 2025–2026 bitemporal traps (Digital Omnibus postponements, legacy cutoffs, EO 14110 revocation, CRA phased dates, Texas TRAIGA, China Sept 2025 Labeling, UN Hanoi treaty threshold).
- **Category D (20 cases)**: Adversarial anti-hallucination citation verification injecting fabricated articles (`EU AI Act Art. 128`, `GDPR Art. 145`, `CRA Art. 999`, `AP I Art. 299`) and revoked EO 14110 claims into `verify_citations`.
- **Category E (15 cases)**: Cross-dialect UK↔US BM25 retrieval (`categorization` → `categorisation`), legal acronym recall, cross-domain citation graph density, and primary-source SHA-256 provenance verification.

---

## 4. Citation

```bibtex
@software{perera2026lexmachina,
  author = {Perera, Avi},
  title = {Lex Machina: Bitemporal Git Provenance, Concordance-Aware Institutional Attribution, and Deterministic Citation Verification for Agentic Legal Reasoning},
  year = {2026},
  version = {2.0.0},
  url = {https://github.com/a-vip/lex-machina}
}
```
