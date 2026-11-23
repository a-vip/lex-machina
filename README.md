# `lex-machina` v3.0 — The Planetary AI, Cyber, IHL & Case Law Bitemporal Git Corpus + Verification MCP Engine

[![01 - Ingest & Build Corpus](https://github.com/a-vip/lex-machina/actions/workflows/01-ingest-and-build-corpus.yml/badge.svg)](https://github.com/a-vip/lex-machina/actions/workflows/01-ingest-and-build-corpus.yml)
[![02 - Verify Search & Provenance](https://github.com/a-vip/lex-machina/actions/workflows/02-build-search-index.yml/badge.svg)](https://github.com/a-vip/lex-machina/actions/workflows/02-build-search-index.yml)
[![03 - LexMachina-Eval (150-Case Benchmark)](https://github.com/a-vip/lex-machina/actions/workflows/03-run-legal-evals.yml/badge.svg)](https://github.com/a-vip/lex-machina/actions/workflows/03-run-legal-evals.yml)
[![05 - Interactive Web Explorer & Registries](https://github.com/a-vip/lex-machina/actions/workflows/05-publish-registries-and-pages.yml/badge.svg)](https://a-vip.github.io/lex-machina/)
[![Companion Agent Skills](https://img.shields.io/badge/Skills_Suite-a--vip%2Flex--machina--skills-blueviolet.svg)](https://github.com/a-vip/lex-machina-skills)
[![Zero Data Retention](https://img.shields.io/badge/Privacy-Zero_Data_Retention_(ZDR)-brightgreen.svg)](WHITEPAPER.md)

**Live Interactive Zero-Data-Retention Explorer**: **[https://a-vip.github.io/lex-machina/](https://a-vip.github.io/lex-machina/)**  
**`lex-machina` v3.0** is the world's first **planetary, bitemporal, cryptographically verified, full-text Git corpus, judicial precedent index, and deterministic citation-verification Model Context Protocol (MCP) engine** spanning **27 authoritative instruments** across global **AI Regulation**, **Cybersecurity & Cybercrime Treaties**, **Data Protection**, **Full International Humanitarian Law (Geneva Conventions I–IV & Additional Protocols I–II)**, **ISO/IEC 42001**, and **Binding CJEU & ICJ Case Law**.

---

## Why No Competitor on Earth Has Built This — And Why `lex-machina` v3.0 Sets the Global Benchmark

In preregistered empirical audits (*Hallucination-Free?*, *Journal of Empirical Legal Studies* 2025; *Benchmarking Legal RAG*, 2026; *"There's No Free Benchmark"*, *PNAS* 2026), **Stanford RegLab** proved that proprietary multi-billion-dollar legal AI platforms still hallucinate at **17% (Lexis+ AI)** to **33% (Westlaw AI)**—primarily through **misgrounding**—while scoring only **58%–64%** on multi-jurisdictional statutory surveys. Meanwhile, open-source EU AI Act MCP servers (`SonnyLabs`, `Disclos`, `eucomplyhub`) rely on static hardcoded summaries with no primary XML/PDF ingestion, no legislative drafting history, no case law, no bitemporal enforceability logic, and no citation verification.

**No commercial publisher, academic repository, civic-tech law repo, or open-source MCP server on Earth combines all eight architectural breakthroughs unified in `lex-machina` v3.0:**

| Capability | Westlaw AI / Lexis+ AI | Open EU AI Act MCPs (`SonnyLabs` / `Disclos`) | Civic-Tech Git (`Bundesgit`) | **`lex-machina` v3.0 (This Engine)** |
| :--- | :---: | :---: | :---: | :---: |
| **Full-Text Primary Ingestion Across 27 Regimes** (EUR-Lex CELLAR XHTML/Akoma Ntoso `eId`, EC 2025 PDFs, Consilium/UN/CoE/NIST/IMDA/UK PDFs, TX Enrolled HTML, China CAC HTML, Geneva I–IV & AP I–II) | Proprietary Black Box | Hardcoded summaries only | Single-country statutes | **45+ full-primary stages + truthful `provenance_mode`** |
| **Binding Judicial Precedent Linked to Statutes** (CJEU *SCHUFA* C-634/21, *Schrems II* C-311/18, *Meta* C-252/21, *La Quadrature du Net* C-511/18 + ICJ *Nuclear Weapons 1996*) | Paid walled garden | None | None | **Verbatim CELLAR/UN primary judgments wired into `graph.json`** |
| **Cryptographic SHA-256 Primary Provenance & ELI/CELEX Permalinks** | No public digest | No | Commit hash only | **SHA-256 of exact upstream primary bytes + ELI/CELEX** |
| **4-Column Concordance + Token-Level Institutional `git blame`** (tracks renumbered norms like Proposal Art. 52 → Final Art. 50 across Python & Cloudflare Edge) | No | No | Line-level only; breaks on renumbering | **Token-level LCS/SequenceMatcher blame + 4-column concordance** |
| **Bitemporal Legal Enforceability Engine** (`Digital Omnibus 2026/1744`, `EO 14110` revocation, legacy grace cutoffs, South Korea 2026, Japan 2025, Brazil PL 2338 pending, CRA/TRAIGA/China 2025) | Partial manual alerts | Outdated 2024 dates | Publication time only | **Deterministic `check_applicability()` across 27 instruments** |
| **Live Verbatim Quote & ABA Formal Opinion 512 Anti-Hallucination Verifier** | 17%–33% hallucination (Stanford RegLab) | None | None | **Python MCP + Edge MCP + Live Browser Verifier + Claude `PostToolUse` hook** |
| **Planetary 5-Continent Coverage + UK↔US Cross-Dialect BM25** | Siloed paid modules | EU AI Act only | Single-country | **EU + US + China + UK + Korea + Japan + Brazil + Singapore + ISO 42001 + UN + CoE + IHL + CJEU/ICJ** |
| **150-Case Preregistered Open CI Benchmark (`LexMachina-Eval`) + Zero-Local-Disk ZDR** | Closed black box | None | Local clone required | **150 automated CI cases published live to `refs/heads/corpus` (< 500 KB local)** |

Read the complete technical specification in [**`WHITEPAPER.md`**](WHITEPAPER.md).

---

## Complete Planetary 27-Instrument Corpus (`src/catalog.json` v3.0)

### 1. European Union AI, Privacy & Cybersecurity Statutes (Full CELLAR XHTML + Official PDFs)
- **`eu/ai-act`**: Regulation (EU) 2024/1689 (Commission Proposal → Council General Approach → Parliament Mandate → Trilogue → Full 113-Art/180-Recital/13-Annex OJ Final) + Official 2025 Commission Prohibited Practices Guidelines PDF (`C(2025) 884`) + Official 2025 Commission GPAI Guidelines PDF + Live **Digital Omnibus `Regulation (EU) 2026/1744`** (`patch_mode`).
- **`eu/gdpr`**: Regulation (EU) 2016/679 (2012 Proposal → 2016 OJ Final → 2018 Corrigendum Consolidation).
- **`eu/cyber/cra`**: Regulation (EU) 2024/2847 Cyber Resilience Act (Proposal → OJ Final; Art. 14 ENISA live Sept 11, 2026; full Dec 11, 2027).
- **`eu/cyber/nis2`**: Directive (EU) 2022/2555 NIS2 Directive (Proposal → OJ Final; active Oct 18, 2024).
- **`eu/cyber/dora`**: Regulation (EU) 2022/2554 DORA (Proposal → OJ Final; active Jan 17, 2025; *lex specialis* over NIS2).

### 2. Binding International & EU Judicial Precedent (`caselaw/` — Verbatim CELLAR XHTML & UN ODS PDF)
- **`caselaw/cjeu/schufa-c-634-21`**: *SCHUFA Holding* (`62021CJ0634`, Dec 2023) — GDPR Art. 22(1) automated algorithmic scoring.
- **`caselaw/cjeu/schrems-ii-c-311-18`**: *Schrems II* (`62018CJ0311`, July 2020) — Cross-border AI/cloud data transfers, SCCs & surveillance limits.
- **`caselaw/cjeu/meta-bundeskartellamt-c-252-21`**: *Meta Platforms v Bundeskartellamt* (`62021CJ0252`, July 2023) — Competition + GDPR Art. 6/9 AI behavioral profiling.
- **`caselaw/cjeu/la-quadrature-du-net-c-511-18`**: *La Quadrature du Net* (`62018CJ0511`, Oct 2020) — Bulk communications retention & automated traffic analysis.
- **`caselaw/icj/nuclear-weapons-1996`**: *ICJ Nuclear Weapons Advisory Opinion* (`A/51/218`, July 1996) — Intransgressible IHL principles & Martens Clause applicability to all emerging weapons.

### 3. Multilateral Treaties & Complete International Humanitarian Law
- **`coe/ai-convention`**: Council of Europe Framework Convention on AI (`CETS 225`: Zero Draft → Consolidated → Adopted → 2026 EU Conclusion).
- **`coe/budapest-convention`**: Budapest Cybercrime Convention (`ETS 185`) & Second Additional Protocol (`CETS 224`).
- **`un/cybercrime-convention`**: UN Convention against Cybercrime / Hanoi Convention (`A/RES/79/243`, full 68 articles + Oct 2025 signing window / 40-ratification gate).
- **`un/ccw-laws`**: UN CCW GGE on LAWS (`2019` 11 Guiding Principles → `2023` Two-Tier Report → `2026` Seventh Review Conference).
- **`un/ai-governance`**: UNGA Resolution `A/RES/78/265` & Global Digital Compact (`A/RES/79/1`, Annex I).
- **`ihl/geneva-conventions`**: 1949 Fourth Geneva Convention (complete 159 articles incl. Art. 147 Grave Breaches) & 1977 Additional Protocol I (102 articles incl. Art. 36 New Weapons Reviews).
- **`ihl/geneva-conventions-i-iii`**: Complete verbatim 1949 Geneva Conventions I (64 arts), II (63 arts), and III (143 arts).
- **`ihl/additional-protocol-ii`**: Complete verbatim 1977 Additional Protocol II (28 articles, Non-International Armed Conflicts).

### 4. Planetary National AI Jurisdictions & Technical Standards
- **`national/us/nist-ai-rmf`**: NIST AI RMF 1.0 (`AI 100-1`), GenAI Profile (`AI 600-1`) & Jan 20, 2025 **EO 14110 Revocation**.
- **`national/us/state-ai-laws`**: Verbatim enrolled **Texas TRAIGA (`HB 149`)**, Colorado `SB 24-205` / `SB 26-189`, California `AB 2013` & `SB 53` (TFAIA).
- **`national/cn/cac-ai-measures`**: Verbatim official Chinese texts from `cac.gov.cn` across Order 9 (35 arts), Order 12 (25 arts), Order 15 GenAI (24 arts), and **Sept 1, 2025 AI Labeling Measures (`GB 45438-2025`, 14 arts)**.
- **`national/uk/ai-governance`**: Official UK DSIT AI White Paper PDF, UK AI Safety Institute (AISI) PDF & **Data (Use and Access) Act 2025 (c. 18)**.
- **`national/sg/agentic-ai-governance`**: Verbatim official 2026 **Singapore IMDA Model AI Governance Framework for Agentic AI** PDF.
- **`national/kr/ai-basic-act`**: **South Korea AI Basic Act** (Act No. 20676 & Presidential Decree No. 36053, effective Jan 22, 2026).
- **`national/jp/ai-promotion-act`**: **Japan AI Promotion Act** (Act No. 53 of 2025, fully in force Sept 1, 2025).
- **`national/br/ai-bill-pl2338`**: **Brazil AI Bill `PL 2338/2023`** (Senate-approved Dec 2024; pending Chamber of Deputies Special Committee review).
- **`standards/iso-iec-42001`**: **ISO/IEC 42001:2023** AI Management System (AIMS) global statutory crosswalk.

---

## 9 Read-Only MCP Tools + 4 MCP Prompts + MCP Resources (`mcp_server/server.py` & `cloudflare_worker/`)

1. `list_instruments(jurisdiction, domain)` — Inventory across all 27 instruments (`eu`, `caselaw`, `coe`, `un`, `ihl`, `national`, `standards`).
2. `get_provision(instrument_path, provision, as_of)` — Fast 3 KB per-stage retrieval with concordance resolution, linked recitals, and SHA-256 provenance.
3. `diff_provisions(instrument_path, provision, stage_a, stage_b)` — Concordance-aware legislative redline diffs.
4. `blame_provision(instrument_path, provision)` — Token- and clause-level institutional authorship (`SequenceMatcher` in Python; flat-array LCS in Cloudflare Edge).
5. `search_corpus(query, jurisdiction, domain)` — BM25 with UK↔US spelling normalization & legal acronym expansion (`FRIA`, `SCHUFA`, `Schrems`, `IMDA`, `DUAA`, `ISO42001`).
6. `get_citation_graph(instrument_path)` — Cross-instrument citations, judicial precedent links, and Recital-to-Article mappings.
7. `check_applicability(instrument_path, provision, as_of_date, placed_on_market_date)` — Bitemporal enforceability engine across 2025–2028 global dates.
8. `verify_citations(draft_text, as_of_date)` — Deterministic ABA Formal Opinion 512 verifier checking compound citations, verbatim quotes, revoked EO 14110, and pending Brazil PL 2338.
9. `get_provenance_audit(instrument_path)` — Full SHA-256 primary-source audit ledger.

### 1-Click Installation (Zero Local Corpus Storage)

#### Option A: Live Remote Streamable HTTP Edge MCP (Zero Install — Recommended)
Connect any MCP client (Claude Code, Cursor, Windsurf, ChatGPT, Agensi) directly to our **live, Zero-Data-Retention Cloudflare Workers edge server** (`GET https://lex-machina.aviperera0.workers.dev/health`):
```json
{
  "mcpServers": {
    "lex-machina": {
      "type": "http",
      "url": "https://lex-machina.aviperera0.workers.dev/mcp"
    }
  }
}
```

#### Option B: Local Stateless `uvx` stdio
```json
{
  "mcpServers": {
    "lex-machina": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/a-vip/lex-machina", "lex-machina-mcp"]
    }
  }
}
```
Pair with [**`a-vip/lex-machina-skills`**](https://github.com/a-vip/lex-machina-skills) (6 `agentskills.io` legal skills + `.claude-plugin/` + ABA Opinion 512 `PostToolUse` hook).

### Zero-Local-Disk Refspec Lock
```bash
git config remote.origin.fetch "+refs/heads/main:refs/remotes/origin/main"
```
