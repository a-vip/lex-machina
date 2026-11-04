# `lex-machina` — The Global AI, Cyber & International Law Git Corpus + MCP Server

[![01 - Ingest & Build Legal Git Corpus](https://github.com/a-vip/lex-machina/actions/workflows/01-ingest-and-build-corpus.yml/badge.svg)](https://github.com/a-vip/lex-machina/actions/workflows/01-ingest-and-build-corpus.yml)
[![02 - Build & Verify Search Index](https://github.com/a-vip/lex-machina/actions/workflows/02-build-search-index.yml/badge.svg)](https://github.com/a-vip/lex-machina/actions/workflows/02-build-search-index.yml)

**`lex-machina`** is a self-updating Git repository and stateless Model Context Protocol (MCP) server that tracks the chronological, article-by-article evolution of global AI regulation, cyber norms, and International Humanitarian Law (IHL).

Every legislative draft, negotiating mandate, trilogue compromise, treaty adoption, and corrigendum is recorded as a deterministic Git commit on the remote `corpus` orphan branch where:
- **Commit Author** = The institutional actor (`European Commission <commission@europa.eu>`, `Council of the European Union <council@consilium.europa.eu>`, `European Parliament <parliament@europa.eu>`, `EU Trilogue Negotiators <trilogue@europa.eu>`, `UN CCW GGE <ccw@un.org>`, `Diplomatic Conference of Geneva <ihl@icrc.org>`, `NIST <ai-rmf@nist.gov>`, `CAC <cac@cac.gov.cn>`). This enables true institutional `git blame` on every legal clause.
- **Directory Granularity** = Broken down into individual files per Article (`articles/article-005.md`), Recital (`recitals/recital-001.md`), and Annex (`annexes/annex-iii.md`), alongside a full compiled `full-text.md` (`instrument.md`) and `metadata.json`. This allows surgical `git diff` and `git log -L` across legislative stages.

---

## Zero-Local-Disk Architecture

To keep local clones under **500 KB** forever:
1. **`main` branch**: Contains only lightweight Python scripts (`src/`), the stateless MCP server (`mcp_server/`), and GitHub Actions workflows (`.github/workflows/`).
2. **`corpus` branch (Remote-Only Orphan Branch)**: Generated inside GitHub Actions (`ubuntu-latest`) via `git fast-import` and force-pushed directly to GitHub. Contains the full multi-stage legal history, `graph.json`, `search-index.json`, and `search-index.sqlite` (SQLite FTS5).
3. **`pipeline-cache` branch (Remote-Only Orphan Branch)**: Stores `.json.gz` compressed source payloads on GitHub.
4. **Local Git Refspec Lock**:
   ```bash
   git config remote.origin.fetch "+refs/heads/main:refs/remotes/origin/main"
   ```
   Running `git pull` on your laptop will only ever fetch `main` and ignore the heavy `corpus` and `pipeline-cache` branches.

---

## Tracked Legal Pillars (`src/catalog.json`)

| Jurisdiction | Path | Instrument | Tracked Chronological Stages |
| :--- | :--- | :--- | :--- |
| **European Union** | `eu/ai-act` | Regulation (EU) 2024/1689 (EU AI Act) | `2021-04-21` Commission Proposal (`52021PC0206`) → `2022-12-06` Council General Approach (`14954/22`) → `2023-06-14` Parliament Mandate (`P9_TA(2023)0236`) → `2024-01-26` Provisional Trilogue Text (`5662/24`) → `2024-07-12` Final Official Journal (`32024R1689`) |
| **European Union** | `eu/gdpr` | Regulation (EU) 2016/679 (GDPR) | `2012-01-25` Commission Proposal (`52012PC0011`) → `2016-04-27` Final OJ Text (`32016R0679`) → `2018-05-23` Corrigendum |
| **Council of Europe** | `coe/ai-convention` | Framework Convention on AI (CETS No. 225) | `2023-01-06` CAI Revised Zero Draft → `2023-12-18` CAI Consolidated Working Draft → `2024-05-17` Adopted Convention (CETS 225) + Explanatory Report |
| **United Nations** | `un/ccw-laws` | UN CCW GGE on Lethal Autonomous Weapons Systems (LAWS) | `2019-08-21` 11 Guiding Principles (`CCW/GGE.1/2019/3`) → `2023-05-26` GGE Consensus Report & Two-Tier Framework (`CCW/GGE.1/2023/2`) |
| **United Nations** | `un/ai-governance` | UNGA Global AI Governance & Digital Compact | `2024-03-21` UNGA Resolution `A/RES/78/265` → `2024-09-22` UN Global Digital Compact (`A/79/L.2`) |
| **Int'l Humanitarian Law** | `ihl/geneva-conventions` | Geneva Conventions & Additional Protocols | `1949-08-12` Geneva Conventions I–IV → `1977-06-08` Additional Protocols I (incl. Art. 35, Art. 36 Weapons Review, Arts. 48, 51, 57) & II |
| **United States** | `national/us/nist-ai-rmf` | NIST AI Risk Management Framework | `2023-01-26` NIST AI RMF 1.0 (`NIST AI 100-1`) → `2024-07-26` NIST AI 600-1 Generative AI Profile |
| **China** | `national/cn/cac-ai-measures` | CAC Algorithmic, Deep Synthesis & GenAI Trilogy | `2022-01-04` Algorithmic Recommendation Provisions → `2022-11-25` Deep Synthesis Provisions → `2023-07-10` Interim Measures for Generative AI Services |

---

## Stateless Remote MCP Server (`mcp_server/server.py`)

The FastMCP server requires **0 MB of local corpus storage**—it queries `refs/heads/corpus` on GitHub via `raw.githubusercontent.com` and the GitHub API:

- `list_instruments(jurisdiction: str | None = None)`
- `get_provision(instrument_path: str, provision: str, as_of: str | None = None)`
- `diff_provisions(instrument_path: str, provision: str, stage_a: str, stage_b: str)`
- `blame_provision(instrument_path: str, provision: str)`
- `search_corpus(query: str, jurisdiction: str | None = None)`
- `get_citation_graph(instrument_path: str)`
