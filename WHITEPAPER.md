# Lex Machina v3.0: Planetary Bitemporal Git Provenance, Binding Judicial Precedent, Concordance-Aware Institutional Attribution, and Deterministic Citation Verification for Agentic Legal Reasoning

**Technical Architecture & Empirical Methodology Whitepaper (Edition 2026.11 — v3.0.0)**  
*Avi Perera / Lex Machina Consortium — `a-vip/lex-machina` & `a-vip/lex-machina-skills`*

---

## Abstract

Empirical evaluations of commercial Retrieval-Augmented Generation (RAG) legal research tools—most notably **Stanford RegLab's** preregistered audits (*Hallucination-Free?*, *Journal of Empirical Legal Studies*, 2025; *Benchmarking Legal RAG*, 2026; *"There's No Free Benchmark"*, *PNAS*, 2026)—demonstrate that proprietary legal AI platforms continue to exhibit 17%–33% hallucination rates driven largely by **misgrounding**, while scoring 58%–64% on multi-jurisdictional statutory surveys. Separately, **SkillsBench (2026)** established that agentic legal accuracy requires concise, human-curated procedural skills paired with deterministic verification scripts rather than monolithic prompt dumps.

**Lex Machina v3.0** addresses every failure mode through a six-layer open legal-informatics architecture spanning **27 authoritative instruments** across **5 continents**, **complete International Humanitarian Law (Geneva Conventions I–IV & Additional Protocols I–II)**, and **binding international/EU judicial precedent (CJEU & ICJ)**:
1. **Cryptographically Hashed Full-Text Primary Ingestion**: EUR-Lex CELLAR content negotiation (Akoma Ntoso `eId` XHTML + HTTP 300 multi-part merger + CJEU Formex XHTML), European Commission 2025 Guidelines PDFs, Consilium/UN/CoE/NIST/UK/Singapore IMDA PDFs, Texas Legislature enrolled HTML, official PRC CAC Chinese statutory HTML, and static IHL treaty mirrors, recording exact raw SHA-256 digests and truthful `provenance_mode` labels.
2. **Binding Case Law Layer Wired into Statutory Graphs**: Verbatim primary judgments for CJEU *SCHUFA* (`C-634/21`), *Schrems II* (`C-311/18`), *Meta Platforms v Bundeskartellamt* (`C-252/21`), *La Quadrature du Net* (`C-511/18`), and the ICJ 1996 *Nuclear Weapons Advisory Opinion* (`A/51/218`), directly cross-linked to the statutory provisions they interpret inside `graph.json`.
3. **4-Column Normative Concordance & Token-Level Institutional `git blame`**: Maps renumbered norms across drafts (`Proposal → Council → Parliament → Trilogue → Official Journal → Amending Acts`) with sequential token alignment in both Python (`SequenceMatcher`) and Cloudflare Edge TypeScript (flat-array LCS).
4. **Planetary Bitemporal Legal Enforceability Engine**: Separates publication time, entry into force, phased application, legacy system grace periods, executive revocations, pending legislation, and voluntary standards across the EU (Digital Omnibus `2026/1744`), US (EO 14110 revocation, TX HB 149, CO SB 24-205/26-189, CA AB 2013/SB 53), China (`GB 45438-2025`), UK (`DUAA 2025`), South Korea (`Act No. 20676`, Jan 22, 2026), Japan (`Act No. 53 of 2025`, Sept 1, 2025), Brazil (`PL 2338/2023`, pending), Singapore (`IMDA Agentic AI MGF`), ISO/IEC 42001, and UN Hanoi Cybercrime (40-ratification gate).
5. **Deterministic Citation & Verbatim Quote Verification**: Operationalizes **ABA Formal Opinion 512** under strict **Zero Data Retention (ZDR)** across Python MCP, Cloudflare Edge Streamable HTTP, a live client-side browser verifier (`docs/index.html`), and a Claude Code `PostToolUse` guardrail hook.
6. **150-Case Continuous Open Benchmark (`LexMachina-Eval v3.0`)**: Runs automatically in GitHub Actions after every corpus rebuild and publishes verified `eval-scorecard.json` directly onto `refs/heads/corpus`.

---

## 1. Architectural Pillars

### 1.1 Zero-Local-Disk Cloud Pipeline & Pruned Cryptographic Caching
All XML/XHTML parsing (`BeautifulSoup` + `lxml`), encrypted UN PDF extraction (`pypdf` + `cryptography`), BM25 indexing, SQLite FTS5 compilation, and `git fast-import` stream generation run exclusively on ephemeral GitHub Actions runners (`ubuntu-latest`). The local repository stays under **500 KB** via `remote.origin.fetch = +refs/heads/main:refs/remotes/origin/main`, while `pipeline-cache` automatically prunes legacy cache schemas to retain only current `v7` `.json.gz` artifacts.

### 1.2 Parser Fidelity Guarantees (v3.0)
- **Heading-vs-Cross-Reference Disambiguation**: Rejects wrapped PDF cross-reference lines (`Article 50 of this Regulation shall...`) and Table-of-Contents dotted leaders so Consilium PDFs and UN treaties extract complete enacting article sequences without losing trailing provisions.
- **Mid-Paragraph Treaty Splitting**: Splits mid-paragraph inline IHL markers (`Art. 147.` in Yale Avalon Geneva Convention IV HTML) to guarantee 100% extraction across all 159 articles of GC IV, all 270 articles of GC I–III, and all 130 articles of AP I & AP II.
- **Bilingual Chinese Statutory Parsing**: Parses `第[一二三四五六七八九十百零]+条` directly from `www.cac.gov.cn` into Arabic-indexed Markdown provisions preserving verbatim Chinese statutory authority alongside English bibliographic headers.
- **CJEU Formex XHTML & ICJ UN ODS Parsing**: Extracts official numbered judicial paragraphs and binding Operative Parts / Dispositifs directly from EUR-Lex CELLAR (`CELEX 6...`) and UN ODS (`A/51/218`).

### 1.3 Live Client-Side Zero-Data-Retention Verification
The GitHub Pages explorer (`https://a-vip.github.io/lex-machina/`) executes 100% inside the attorney's browser with zero backend servers and zero prompt retention—live-fetching cited articles from `raw.githubusercontent.com/a-vip/lex-machina/corpus/` to perform character-for-character verbatim quote verification against primary official texts.

---

## 2. Preregistered Empirical Evaluation (`LexMachina-Eval v3.0` — 150 Cases)

`evals/lexmachina_bench.jsonl` executes **150 deterministic legal verification cases** on every build:
- **Category A (25 cases)**: Deep-article verbatim grounding across EU AI Act, GDPR, CRA, NIS2, DORA, CoE CETS 225, IHL AP I, and Texas TRAIGA.
- **Category B (20 cases)**: Concordance-resolved renumbering lookups, multi-stage diffs, linked recitals, and token-level institutional blame.
- **Category C (20 cases)**: 2025–2026 bitemporal traps (Digital Omnibus postponements, legacy cutoffs, EO 14110 revocation, CRA, TRAIGA, China 2025 Labeling, UN Hanoi threshold).
- **Category D (20 cases)**: Adversarial anti-hallucination citation verification injecting fabricated articles and revoked EO 14110 claims.
- **Category E (15 cases)**: Cross-dialect UK↔US BM25 retrieval, acronym expansion, citation graph density, and SHA-256 provenance verification.
- **Category F (20 cases)**: Verbatim quote-fidelity audits (`EXACT_MATCH` vs. `UNVERIFIED_OR_PARAPHRASED`) and primary-source depth across GC IV (incl. Art. 147), AP I, UN treaties, and NIST core functions.
- **Category G (30 cases)**: Planetary v3.0 validation covering Geneva Conventions I–III, Additional Protocol II, UN Hanoi Art. 65, EC 2025 Guidelines PDFs, China CAC verbatim Chinese articles, UK DUAA/AISI/White Paper, Singapore IMDA Agentic AI PDF, South Korea AI Basic Act, Japan AI Promotion Act, Brazil PL 2338 pending-enactment trap, ISO/IEC 42001, all 4 CJEU landmark judgments, and ICJ 1996 Nuclear Weapons Opinion.

---

## 3. Citation

```bibtex
@software{perera2026lexmachina,
  author = {Perera, Avi},
  title = {Lex Machina v3.0: Planetary Bitemporal Git Provenance, Binding Judicial Precedent, and Deterministic Citation Verification for Agentic Legal Reasoning},
  year = {2026},
  version = {3.0.0},
  url = {https://github.com/a-vip/lex-machina}
}
```
