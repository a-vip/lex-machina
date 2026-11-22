# `lex-machina` v2.0 — The Global AI, Cyber & International Law Bitemporal Git Corpus + Verification MCP Engine

[![01 - Ingest & Build Corpus](https://github.com/a-vip/lex-machina/actions/workflows/01-ingest-and-build-corpus.yml/badge.svg)](https://github.com/a-vip/lex-machina/actions/workflows/01-ingest-and-build-corpus.yml)
[![02 - Verify Search & Provenance](https://github.com/a-vip/lex-machina/actions/workflows/02-build-search-index.yml/badge.svg)](https://github.com/a-vip/lex-machina/actions/workflows/02-build-search-index.yml)
[![03 - LexMachina-Eval (100-Case Benchmark)](https://github.com/a-vip/lex-machina/actions/workflows/03-run-legal-evals.yml/badge.svg)](https://github.com/a-vip/lex-machina/actions/workflows/03-run-legal-evals.yml)
[![Companion Agent Skills](https://img.shields.io/badge/Skills_Suite-a--vip%2Flex--machina--skills-blueviolet.svg)](https://github.com/a-vip/lex-machina-skills)
[![Zero Data Retention](https://img.shields.io/badge/Privacy-Zero_Data_Retention_(ZDR)-brightgreen.svg)](WHITEPAPER.md)

**`lex-machina`** is the world's first **bitemporal, cryptographically verified, full-text Git corpus and deterministic citation-verification Model Context Protocol (MCP) engine** spanning global **AI Regulation**, **Cybersecurity & Cybercrime Treaties**, **Data Protection**, and **International Humanitarian Law (IHL)**.

---

## Why No Competitor on Earth Has Built This — And Why `lex-machina` Is the Gold Standard

In landmark empirical studies (*Hallucination-Free?*, *Journal of Empirical Legal Studies* 2025; *Benchmarking Legal RAG*, 2026; *"There's No Free Benchmark"*, *PNAS* 2026), **Stanford RegLab** proved that even multi-billion-dollar proprietary legal AI platforms hallucinate at alarming rates (**Lexis+ AI ~17%**, **Westlaw AI ~33%**) primarily via **misgrounding**, while scoring only **58%–64%** on multi-jurisdictional statutory surveys. Meanwhile, open-source EU AI Act MCP servers (`SonnyLabs`, `Disclos`, `eucomplyhub`) rely on static hardcoded summaries with no full primary XML ingestion, no legislative drafting history, no bitemporal enforceability logic, and no citation verification.

**No commercial vendor, legal publisher, academic database, or open-source MCP server on the planet combines all seven architectural breakthroughs unified in `lex-machina` v2.0:**

| Capability | Westlaw AI / Lexis+ AI | Open EU AI Act MCPs (`SonnyLabs` / `Disclos`) | Civic-Tech Git (`Bundesgit`) | **`lex-machina` v2.0 (This Engine)** |
| :--- | :---: | :---: | :---: | :---: |
| **100% Full-Text Primary Ingestion** (EUR-Lex CELLAR XHTML/Akoma Ntoso `eId`, Consilium/UN/CoE/NIST PDFs, ICRC IHL) | Proprietary Black Box | Hardcoded summaries only | Single-country statutes | **Full primary texts + truthful `provenance_mode`** |
| **Cryptographic SHA-256 Primary Provenance & ELI/CELEX Permalinks** | No public digest | No | Commit hash only | **SHA-256 of raw upstream primary doc + ELI/CELEX** |
| **4-Column Concordance + Phrase-Level Institutional `git blame`** (tracks renumbered norms like Proposal Art. 52 → Final Art. 50) | No | No | Line-level only; breaks on renumbering | **Token-level institutional blame + 4-column concordance** |
| **Bitemporal Legal Enforceability Engine** (`Digital Omnibus 2026/1744`, `EO 14110` revocation, legacy grace periods, CRA/TRAIGA/China 2025) | Partial manual alerts | Static outdated 2024 dates | Publication time only | **Deterministic `check_applicability()` bitemporal engine** |
| **Deterministic Anti-Hallucination Citation & Verbatim Quote Verifier** (ABA Formal Opinion 512) | 17%–33% hallucination (Stanford RegLab) | None | None | **Deterministic `verify_citations()` + Claude Code `PostToolUse` hook** |
| **Cross-Domain AI + Cyber + Privacy + IHL Unification + UK↔US BM25** | Siloed paid modules | EU AI Act only | National only | **12 global regimes + UK↔US spelling & acronym BM25** |
| **Preregistered 100-Case Open Empirical Benchmark (`LexMachina-Eval`)** | Closed black box | None | None | **100 automated CI cases run on every corpus build** |
| **Zero-Local-Disk Cloud Build + Zero-Data-Retention Edge Streamable HTTP** | Heavy SaaS lock-in | Local Python/Node required | Full local clone | **< 500 KB local + Cloudflare Workers Streamable HTTP ZDR** |

Read the full scientific architecture in [**`WHITEPAPER.md`**](WHITEPAPER.md).

---

## Complete 2026 Multi-Domain Legal Corpus (`src/catalog.json`)

| Domain | Path | Instrument | Chronological Stages & 2025–2026 Amendments |
| :--- | :--- | :--- | :--- |
| **AI (EU)** | `eu/ai-act` | **Regulation (EU) 2024/1689 (EU AI Act)** as amended by **Regulation (EU) 2026/1744** | `2021-04-21` Commission Proposal (`52021PC0206`) → `2022-12-06` Council (`ST 14954/22`) → `2023-06-14` Parliament (`P9_TA(2023)0236`) → `2024-01-26` Trilogue (`ST 5662/24`) → `2024-07-12` Official Journal (`32024R1689`, full 113 arts/180 recitals/13 annexes) → `2025-02-04` Commission Art. 5/Art. 3 Guidelines → `2025-07-10` GPAI Code of Practice → `2026-07-20` **Digital Omnibus (`32026R1744`)** |
| **Privacy (EU)** | `eu/gdpr` | **Regulation (EU) 2016/679 (GDPR)** | `2012-01-25` Commission Proposal (`52012PC0011`) → `2016-04-27` Official Journal (`32016R0679`, full 99 arts/173 recitals) → `2018-05-23` Corrigendum Consolidation |
| **Cyber (EU)** | `eu/cyber/cra` | **Regulation (EU) 2024/2847 (Cyber Resilience Act)** | `2022-09-15` Proposal (`52022PC0454`) → `2024-11-20` Official Journal (`32024R2847`; Art. 14 ENISA reporting live **Sept 11, 2026**; full compliance **Dec 11, 2027**) |
| **Cyber (EU)** | `eu/cyber/nis2` | **Directive (EU) 2022/2555 (NIS2 Directive)** | `2020-12-16` Proposal (`52020PC0823`) → `2022-12-27` Official Journal (`32022L2555`, active since Oct 18, 2024) |
| **Cyber (EU)** | `eu/cyber/dora` | **Regulation (EU) 2022/2554 (DORA)** | `2020-09-24` Proposal (`52020PC0595`) → `2022-12-27` Official Journal (`32022R2554`, active since Jan 17, 2025; *lex specialis* over NIS2) |
| **AI Treaty (CoE)** | `coe/ai-convention` | **Framework Convention on AI (CETS No. 225)** | `2023-01-06` Zero Draft → `2023-12-18` Consolidated Draft → `2024-05-17` Adopted `CETS 225` → `2026-06-15` EU Formal Conclusion |
| **Cyber Treaty (CoE)** | `coe/budapest-convention` | **Budapest Convention (`ETS 185`) & 2nd Protocol (`CETS 224`)** | `2001-11-23` Budapest Convention (`ETS 185`) → `2022-05-12` Second Additional Protocol (`CETS 224`) |
| **Cyber Treaty (UN)** | `un/cybercrime-convention` | **UN Convention against Cybercrime (Hanoi Convention, `A/RES/79/243`)** | `2024-12-24` UNGA Adoption → `2025-10-25` Hanoi Opening for Signature (open until Dec 31, 2026; 40-ratification threshold under Art. 65) |
| **IHL / LAWS (UN)** | `un/ccw-laws` | **UN CCW GGE on Lethal Autonomous Weapons Systems** | `2019-08-21` 11 Guiding Principles → `2023-05-26` Two-Tier Framework → `2026-09-18` 2024–2026 Mandate & Seventh Review Conference |
| **AI (UN)** | `un/ai-governance` | **UNGA AI Resolutions & Global Digital Compact** | `2024-03-21` `A/RES/78/265` → `2024-09-22` Global Digital Compact (`A/RES/79/1`, Annex I) |
| **IHL (Treaty)** | `ihl/geneva-conventions` | **Geneva Conventions (1949) & Additional Protocols I & II (1977)** | `1949-08-12` Geneva Conventions I–IV → `1977-06-08` Additional Protocols I (Arts. 35, 36 Weapons Review, 48, 51, 57, 85) & II |
| **AI (US Federal)** | `national/us/nist-ai-rmf` | **NIST AI RMF 1.0, AI 600-1 & Federal EO Trajectory** | `2023-01-26` NIST AI 100-1 → `2024-07-26` NIST AI 600-1 GenAI Profile → `2025-01-20` **Formal Revocation of EO 14110** |
| **AI (US States)** | `national/us/state-ai-laws` | **US Binding State AI Statutes** | `2024-05-17` Colorado `SB 24-205` & California `AB 2013` → `2026-01-01` **Texas TRAIGA (`HB 149`)**, California `SB 53` (TFAIA) & Colorado `SB 26-189` |
| **AI (China)** | `national/cn/cac-ai-measures` | **China CAC AI Framework & 2025 Labeling Measures** | `2022-01-04` Order 9 → `2022-11-25` Order 12 → `2023-07-10` Order 15 → `2025-09-01` **Mandatory Synthetic Content Labeling (`GB 45438-2025`)** |

---

## 9 Read-Only MCP Tools + MCP Resources & Prompts (`mcp_server/server.py` v2.0)

1. `list_instruments(jurisdiction, domain)` — Inventory with SHA-256 provenance modes & article counts.
2. `get_provision(instrument_path, provision, as_of)` — Fast 3 KB per-stage retrieval (`versions/<inst>/<stage>/<prov>`) with concordance resolution, linked recitals, and SHA-256 provenance block.
3. `diff_provisions(instrument_path, provision, stage_a, stage_b)` — **Concordance-aware** redline diffs across renumbered legislative drafts.
4. `blame_provision(instrument_path, provision)` — **Clause- and token-level institutional attribution** preserving Commission/Council/Parliament authorship across formatting edits.
5. `search_corpus(query, jurisdiction, domain)` — Precomputed **BM25** search with UK↔US legal spelling normalization (`categorisation`↔`categorization`, `defence`↔`defense`) and acronym expansion (`FRIA`, `RBI`, `GPAI`, `LAWS`, `CRA`, `DORA`, `NIS2`).
6. `get_citation_graph(instrument_path)` — Cross-instrument citations + Recital-to-Article interpretive mappings.
7. `check_applicability(instrument_path, provision, as_of_date, placed_on_market_date)` — **Bitemporal enforceability engine** (Digital Omnibus 2026/1744, legacy grace cutoffs, EO 14110 revocation, CRA, TRAIGA, China 2025 Labeling).
8. `verify_citations(draft_text, as_of_date)` — **Deterministic ABA Formal Opinion 512 anti-hallucination verifier** checking article existence, verbatim quotes, and revoked/deferred status.
9. `get_provenance_audit(instrument_path)` — Full cryptographic SHA-256 audit manifest.

Plus native **MCP Resources** (`lex://provenance`, `lex://applicability`, `lex://concordance`, `lex://provision/{j}/{s}/{p}`), **MCP Prompts** (`audit_ai_system`, `travaux_redline`, `article_36_review`), **Tool Annotations** (`readOnlyHint: true`), **Cloudflare Workers Stateless Streamable HTTP** (`cloudflare_worker/`), and manifests for the **Official MCP Registry (`server.json`)**, **Smithery (`smithery.yaml`)**, and **Glama (`glama.json`)**.

---

## 1-Click Installation (Zero Local Corpus Storage)

### Option A: `uvx` (Claude Desktop / Claude Code / Cursor)
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

### Option B: Remote Streamable HTTP Edge MCP (Zero Python / Zero Node Install)
Deploy `cloudflare_worker/` via GitHub Actions workflow `04-deploy-edge-mcp.yml` and point any MCP client to:
```json
{
  "mcpServers": {
    "lex-machina": {
      "url": "https://lex-machina-mcp.<your-subdomain>.workers.dev/mcp"
    }
  }
}
```

### Companion Institutional Agent Skills Suite
Pair this engine with [**`a-vip/lex-machina-skills`**](https://github.com/a-vip/lex-machina-skills) (`agentskills.io` + `.claude-plugin/` + `agensi.io` + ABA Opinion 512 `PostToolUse` guardrail hook).

### Zero-Local-Disk Refspec Lock
Local clones stay under **500 KB forever** because heavy data and history reside exclusively on remote orphan branches (`corpus` and `pipeline-cache`):
```bash
git config remote.origin.fetch "+refs/heads/main:refs/remotes/origin/main"
```
