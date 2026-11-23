/**
 * Lex Machina v3.0 — Zero-Dependency Stateless Remote Streamable HTTP Edge MCP Server
 * for Cloudflare Workers (100% 9-Tool + Token-Level Institutional Blame + Verbatim Quote
 * Verification + MCP Resources + 4 MCP Prompts Parity).
 *
 * Deployed purely via GitHub Actions (zero local node_modules!).
 * Serves `POST /mcp` (MCP JSON-RPC 2.0 Streamable HTTP) and `GET /health` globally
 * with Cloudflare Edge Caching over `raw.githubusercontent.com/a-vip/lex-machina/corpus`
 * and strict Zero Data Retention (ZDR: zero prompt or query logging).
 */

export interface Env {
  LEX_MACHINA_REPO?: string;
  LEX_MACHINA_BRANCH?: string;
  ENTERPRISE_API_KEY?: string;
}

const DEFAULT_REPO = "a-vip/lex-machina";
const DEFAULT_BRANCH = "corpus";

interface JsonRpcRequest {
  jsonrpc: "2.0";
  id?: string | number | null;
  method: string;
  params?: Record<string, any>;
}

const READ_ONLY = {
  readOnlyHint: true,
  destructiveHint: false,
  idempotentHint: true,
  openWorldHint: false
};

const TOOLS_SPEC = [
  {
    name: "list_instruments",
    description: "List all 27 tracked AI, privacy, cyber, full IHL, global national, ISO/IEC 42001, and CJEU/ICJ case law instruments with SHA-256 provenance.",
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      properties: {
        jurisdiction: { type: "string", description: "Optional filter: eu, coe, un, ihl, national, standards, caselaw" },
        domain: { type: "string", description: "Optional filter: ai, cyber, privacy, ihl" }
      }
    }
  },
  {
    name: "get_provision",
    description: "Fetch exact normalized Markdown text of an article, recital, annex, or judicial ruling section at a specific date or legislative stage with concordance resolution and SHA-256 provenance.",
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      required: ["instrument_path", "provision"],
      properties: {
        instrument_path: { type: "string" },
        provision: { type: "string" },
        as_of: { type: "string" }
      }
    }
  },
  {
    name: "diff_provisions",
    description: "Compute a concordance-aware redline diff between two legislative stages (resolving renumbered articles such as EU AI Act Proposal Art. 52 -> Final Art. 50).",
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      required: ["instrument_path", "provision", "stage_a", "stage_b"],
      properties: {
        instrument_path: { type: "string" },
        provision: { type: "string" },
        stage_a: { type: "string" },
        stage_b: { type: "string" }
      }
    }
  },
  {
    name: "blame_provision",
    description: "Token- and clause-level institutional git blame across chronological legislative drafts (concordance-resolved), computing institutional authorship share percentages.",
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      required: ["instrument_path", "provision"],
      properties: {
        instrument_path: { type: "string" },
        provision: { type: "string" }
      }
    }
  },
  {
    name: "search_corpus",
    description: "BM25 legal search with UK<->US spelling normalization and legal acronym synonym expansion across statutes, treaties, national frameworks, and CJEU/ICJ case law.",
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      required: ["query"],
      properties: {
        query: { type: "string" },
        jurisdiction: { type: "string" }
      }
    }
  },
  {
    name: "get_citation_graph",
    description: "Return incoming/outgoing cross-references, CJEU/ICJ judicial precedent edges, and Recital-to-Article interpretive links from graph.json.",
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      required: ["instrument_path"],
      properties: {
        instrument_path: { type: "string" }
      }
    }
  },
  {
    name: "check_applicability",
    description: "Bitemporal enforceability check accounting for EU Digital Omnibus Regulation (EU) 2026/1744, EO 14110 revocation, legacy grace cutoffs, CRA, Texas TRAIGA, China 2025 Labeling, South Korea AI Basic Act, Japan AI Promotion Act, UK DUAA 2025, and Brazil PL 2338.",
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      required: ["instrument_path"],
      properties: {
        instrument_path: { type: "string" },
        provision: { type: "string" },
        as_of_date: { type: "string" },
        placed_on_market_date: { type: "string" }
      }
    }
  },
  {
    name: "verify_citations",
    description: "Deterministic Stanford-RegLab-grade ABA Formal Opinion 512 anti-hallucination verifier checking compound statutory references, verbatim quoted strings, and bitemporal validity.",
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      required: ["draft_text"],
      properties: {
        draft_text: { type: "string" },
        as_of_date: { type: "string" }
      }
    }
  },
  {
    name: "get_provenance_audit",
    description: "Return SHA-256 primary-source provenance manifest and official ELI/CELEX permalinks.",
    annotations: READ_ONLY,
    inputSchema: {
      type: "object",
      properties: {
        instrument_path: { type: "string" }
      }
    }
  }
];

const PROMPTS_SPEC = [
  {
    name: "audit_ai_system",
    description: "Partner-level FIRAC EU AI Act + Digital Omnibus 2026/1744 compliance audit workflow",
    arguments: [
      { name: "system_description", description: "Technical description of the AI system", required: true },
      { name: "deployment_date", description: "ISO YYYY-MM-DD assessment date", required: false }
    ]
  },
  {
    name: "travaux_redline",
    description: "CJEU teleological interpretation & concordance-aware institutional blame workflow",
    arguments: [
      { name: "instrument_path", description: "e.g., eu/ai-act or eu/gdpr", required: true },
      { name: "provision", description: "e.g., articles/article-050.md", required: true }
    ]
  },
  {
    name: "article_36_review",
    description: "Additional Protocol I Article 36, ICJ Nuclear Weapons Opinion & UN CCW LAWS military AI legal weapons review",
    arguments: [
      { name: "weapons_system_description", description: "Operational profile of the autonomous system", required: true }
    ]
  },
  {
    name: "cjeu_precedent_brief",
    description: "Binding CJEU AI/Privacy/Cyber jurisprudence synthesis (SCHUFA, Schrems II, Meta, La Quadrature du Net)",
    arguments: [
      { name: "legal_issue", description: "Legal question to analyze against binding CJEU holdings", required: true }
    ]
  }
];

const LEGAL_SYNONYMS: Record<string, string[]> = {
  fria: ["fundamental", "rights", "impact", "assessment"],
  dpia: ["data", "protection", "impact", "assessment"],
  rbi: ["remote", "biometric", "identification"],
  gpai: ["general", "purpose", "model"],
  laws: ["lethal", "autonomous", "weapons"],
  cra: ["cyber", "resilience"],
  nis2: ["network", "information", "security"],
  dora: ["digital", "operational", "resilience"],
  traiga: ["texas", "responsible", "governance"],
  omnibus: ["2026", "1744", "postponed"],
  schufa: ["automated", "decision", "scoring", "article", "22", "634"],
  schrems: ["transfer", "adequacy", "surveillance", "standard", "contractual"],
  cjeu: ["court", "justice", "preliminary", "ruling", "operative"],
  icj: ["international", "court", "justice", "martens", "intransgressible"],
  duaa: ["data", "use", "access", "2025", "automated"],
  imda: ["singapore", "agentic", "governance", "framework"],
  iso42001: ["42001", "management", "system", "aims"]
};

async function fetchCorpusText(env: Env, relPath: string): Promise<string | null> {
  const repo = env.LEX_MACHINA_REPO || DEFAULT_REPO;
  const branch = env.LEX_MACHINA_BRANCH || DEFAULT_BRANCH;
  const url = `https://raw.githubusercontent.com/${repo}/${branch}/${relPath.replace(/^\/+/, "")}`;

  const cache = (caches as any).default;
  const cacheReq = new Request(url, { method: "GET" });
  let resp: Response | undefined = cache ? await cache.match(cacheReq) : undefined;

  if (!resp) {
    const upstream = await fetch(url, {
      headers: { "User-Agent": "lex-machina-edge-mcp/3.0" }
    });
    if (!upstream.ok) return null;
    resp = new Response(upstream.body, {
      status: 200,
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "public, max-age=300"
      }
    });
    if (cache) await cache.put(cacheReq, resp.clone());
  }
  return await resp.text();
}

async function fetchCorpusJson(env: Env, relPath: string): Promise<any | null> {
  const txt = await fetchCorpusText(env, relPath);
  if (!txt) return null;
  try {
    return JSON.parse(txt);
  } catch {
    return null;
  }
}

function normalizeProvision(prov: string): string {
  const p = prov.trim().replace(/^\/+|\/+$/g, "");
  if (p.endsWith(".md") && p.includes("/")) return p;
  const art = p.match(/^(?:article[-_\s]*)?(\d+)([a-z]?)$/i);
  if (art) return `articles/article-${art[1].padStart(3, "0")}${art[2].toLowerCase()}.md`;
  const rec = p.match(/^recital[-_\s]*(\d+)([a-z]?)(?:\.md)?$/i);
  if (rec) return `recitals/recital-${rec[1].padStart(3, "0")}${rec[2].toLowerCase()}.md`;
  const anx = p.match(/^annex[-_\s]*([ivxlc0-9a-z]+)(?:\.md)?$/i);
  if (anx) return `annexes/annex-${anx[1].toLowerCase()}.md`;
  return p.includes("/") ? (p.endsWith(".md") ? p : `${p}.md`) : `articles/${p}.md`;
}

function normalizeToken(tok: string): string {
  return tok
    .toLowerCase()
    .replace(/isation$/, "ization")
    .replace(/isations$/, "izations")
    .replace(/ised$/, "ized")
    .replace(/ising$/, "izing")
    .replace(/ise$/, "ize")
    .replace(/^defence$/, "defense")
    .replace(/^offence$/, "offense")
    .replace(/^behaviour$/, "behavior")
    .replace(/^labelling$/, "labeling");
}

function extractBodyLines(md: string): string[] {
  return md
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((l) => l && !l.startsWith("- **") && !l.startsWith("# "));
}

function tokenizeBlame(text: string): string[] {
  return text.match(/[A-Za-z0-9']+|[.,;:()\-]/g) || [];
}

/**
 * Sequential token-level institutional attribution matching Python `difflib.SequenceMatcher`
 * semantics via fast anchor-guided LCS alignment (zero dependencies, edge-CPU safe).
 */
function alignTokenOwners<T>(prevTokens: string[], prevOwners: T[], curTokens: string[], curOwner: T): T[] {
  const m = prevTokens.length;
  const n = curTokens.length;
  const newOwners: T[] = new Array(n).fill(curOwner);
  if (!m || !n) return newOwners;

  const pLow = prevTokens.map((t) => t.toLowerCase());
  const cLow = curTokens.map((t) => t.toLowerCase());

  // Exact flat-array LCS DP when matrix fits comfortably in Worker memory/CPU budget
  if (m * n <= 1600000) {
    const cols = n + 1;
    const dp = new Uint16Array((m + 1) * cols);
    for (let i = m - 1; i >= 0; i--) {
      const row = i * cols;
      const nextRow = (i + 1) * cols;
      const tokI = pLow[i];
      for (let j = n - 1; j >= 0; j--) {
        if (tokI === cLow[j]) {
          dp[row + j] = dp[nextRow + j + 1] + 1;
        } else {
          const a = dp[nextRow + j];
          const b = dp[row + j + 1];
          dp[row + j] = a >= b ? a : b;
        }
      }
    }
    let i = 0;
    let j = 0;
    while (i < m && j < n) {
      if (pLow[i] === cLow[j]) {
        newOwners[j] = prevOwners[i];
        i++;
        j++;
      } else if (dp[(i + 1) * cols + j] >= dp[i * cols + j + 1]) {
        i++;
      } else {
        j++;
      }
    }
    return newOwners;
  }

  // Fallback for extraordinarily long articles (>1,250 tokens): 4-gram shingle anchor matching
  const shingleMap = new Map<string, number[]>();
  for (let i = 0; i + 3 < m; i++) {
    const key = `${pLow[i]} ${pLow[i + 1]} ${pLow[i + 2]} ${pLow[i + 3]}`;
    const arr = shingleMap.get(key);
    if (arr) arr.push(i);
    else shingleMap.set(key, [i]);
  }
  let lastPrev = 0;
  for (let j = 0; j + 3 < n; j++) {
    const key = `${cLow[j]} ${cLow[j + 1]} ${cLow[j + 2]} ${cLow[j + 3]}`;
    const hits = shingleMap.get(key);
    if (!hits) continue;
    const matchIdx = hits.find((idx) => idx >= lastPrev) ?? hits[0];
    for (let k = 0; k < 4; k++) newOwners[j + k] = prevOwners[matchIdx + k];
    lastPrev = matchIdx;
  }
  return newOwners;
}

async function resolveConcordance(env: Env, instPath: string, normProv: string, targetStage: string): Promise<{ mapped: string; recitals: string[] }> {
  const conc = (await fetchCorpusJson(env, "concordance.json")) || { concordances: {} };
  const list = (conc.concordances || {})[instPath] || [];
  for (const entry of list) {
    const vals = Object.values(entry.stage_map || {});
    if (vals.includes(normProv) || entry.norm_id === normProv) {
      return {
        mapped: (entry.stage_map || {})[targetStage] || normProv,
        recitals: entry.recitals || []
      };
    }
  }
  return { mapped: normProv, recitals: [] };
}

async function fetchProvisionAtStage(env: Env, inst: any, ver: any, normProv: string): Promise<{ text: string | null; resolved: string; recitals: string[] }> {
  const { mapped, recitals } = await resolveConcordance(env, inst.path, normProv, ver.stage);
  for (const cand of Array.from(new Set([mapped, normProv]))) {
    const t = await fetchCorpusText(env, `versions/${inst.path}/${ver.stage}/${cand}`);
    if (t) return { text: t, resolved: cand, recitals };
  }
  const latestNonPatch = resolveStage(inst, undefined);
  if (ver === latestNonPatch || ver === inst.versions[inst.versions.length - 1] || ver.source_type === "regulatory_supplement") {
    for (const cand of Array.from(new Set([mapped, normProv]))) {
      const t = await fetchCorpusText(env, `${inst.path}/${cand}`);
      if (t) return { text: t, resolved: cand, recitals };
    }
  }
  return { text: null, resolved: mapped, recitals };
}

function resolveStage(inst: any, asOf?: string): any {
  const versions = inst.versions || [];
  if (!asOf || ["latest", "head", "current"].includes(asOf.trim().toLowerCase())) {
    const nonPatch = versions.filter((v: any) => !v.patch_mode);
    return nonPatch.length ? nonPatch[nonPatch.length - 1] : versions[versions.length - 1];
  }
  const q = asOf.trim().toLowerCase();
  const direct = versions.find(
    (v: any) =>
      v.stage.toLowerCase() === q ||
      v.stage.toLowerCase().includes(q) ||
      v.stage_label.toLowerCase().includes(q) ||
      (v.document_symbol || "").toLowerCase().includes(q) ||
      v.date === q
  );
  if (direct) return direct;
  const dated = versions.filter((v: any) => v.date <= q);
  return dated.length ? dated[dated.length - 1] : versions[versions.length - 1];
}

function simpleLineDiff(linesA: string[], linesB: string[]): { added: number; removed: number; unified: string } {
  const setA = new Set(linesA);
  const setB = new Set(linesB);
  const out: string[] = [];
  let added = 0;
  let removed = 0;
  for (const l of linesA) {
    if (!setB.has(l)) {
      out.push(`- ${l}`);
      removed++;
    }
  }
  for (const l of linesB) {
    if (!setA.has(l)) {
      out.push(`+ ${l}`);
      added++;
    } else {
      out.push(`  ${l}`);
    }
  }
  return { added, removed, unified: out.join("\n") };
}

async function checkApplicability(env: Env, args: Record<string, any>): Promise<any> {
  const app = (await fetchCorpusJson(env, "applicability.json")) || { rules: [] };
  const instPath = String(args.instrument_path || "").replace(/^\/+|\/+$/g, "").toLowerCase();
  const rawProv = String(args.provision || "*");
  const prov = ["*", "all", ""].includes(rawProv.trim()) ? "*" : normalizeProvision(rawProv);
  const asOf = args.as_of_date || new Date().toISOString().slice(0, 10);
  const placed = args.placed_on_market_date || null;

  const rule =
    (app.rules || []).find((r: any) => r.instrument_path.toLowerCase() === instPath && (r.provisions.includes(prov) || r.provisions.includes(rawProv.toLowerCase()))) ||
    (app.rules || []).find((r: any) => r.instrument_path.toLowerCase() === instPath && r.provisions.includes("*"));
  if (!rule) return { instrument_path: instPath, provision: prov, as_of_date: asOf, legal_status: "NO_BITEMPORAL_RULE_RECORDED" };

  let status = "ENFORCEABLE";
  if (rule.revoked_date && asOf >= rule.revoked_date) status = "REVOKED";
  else if (rule.status_override === "OPEN_FOR_SIGNATURE_PENDING_40_RATIFICATIONS") status = "NOT_YET_IN_FORCE_PENDING_RATIFICATIONS";
  else if (rule.status_override === "PENDING_LEGISLATION_NOT_YET_ENACTED") status = "PENDING_LEGISLATION_NOT_YET_ENACTED";
  else if (["VOLUNTARY_GOVERNANCE_FRAMEWORK", "VOLUNTARY_CERTIFIABLE_STANDARD"].includes(rule.status_override)) status = rule.status_override;
  else if (rule.entry_into_application && asOf < rule.entry_into_application) status = "IN_FORCE_NOT_YET_APPLICABLE";
  else if (placed && rule.legacy_cutoff_date && rule.legacy_transition_deadline && placed < rule.legacy_cutoff_date && asOf < rule.legacy_transition_deadline) {
    status = "LEGACY_TRANSITION_GRACE_PERIOD";
  }

  return {
    ...rule,
    provision: prov,
    as_of_date: asOf,
    placed_on_market_date: placed,
    effective_entry_into_application: rule.entry_into_application || null,
    legal_status: status
  };
}

async function executeTool(env: Env, name: string, args: Record<string, any>): Promise<any> {
  const catalog = (await fetchCorpusJson(env, "catalog.json")) || { instruments: [] };
  const findInst = (p: string) =>
    (catalog.instruments || []).find((i: any) => i.path.toLowerCase() === p.replace(/^\/+|\/+$/g, "").toLowerCase() || i.id.toLowerCase() === p.toLowerCase());

  if (name === "list_instruments") {
    let list = catalog.instruments || [];
    if (args.jurisdiction) list = list.filter((i: any) => i.jurisdiction.toLowerCase() === String(args.jurisdiction).toLowerCase());
    if (args.domain) list = list.filter((i: any) => (i.domain || "").toLowerCase() === String(args.domain).toLowerCase());
    return { count: list.length, instruments: list };
  }

  if (name === "get_provision") {
    const inst = findInst(String(args.instrument_path || ""));
    if (!inst) return { error: `Unknown instrument_path: ${args.instrument_path}` };
    const ver = resolveStage(inst, args.as_of);
    const normProv = normalizeProvision(String(args.provision || ""));
    const { text, resolved, recitals } = await fetchProvisionAtStage(env, inst, ver, normProv);
    if (!text) return { error: `PROVISION NOT IN CORPUS: ${inst.path}/${normProv}@${ver.stage}` };
    return {
      instrument_path: inst.path,
      requested_provision: normProv,
      resolved_provision: resolved,
      renumbered_via_concordance: resolved !== normProv,
      linked_recitals: recitals,
      stage: ver.stage,
      date: ver.date,
      institutional_author: `${ver.author_name} <${ver.author_email}>`,
      markdown: text
    };
  }

  if (name === "diff_provisions") {
    const inst = findInst(String(args.instrument_path || ""));
    if (!inst) return { error: `Unknown instrument_path: ${args.instrument_path}` };
    const verA = resolveStage(inst, args.stage_a);
    const verB = resolveStage(inst, args.stage_b);
    const normProv = normalizeProvision(String(args.provision || ""));
    const resA = await fetchProvisionAtStage(env, inst, verA, normProv);
    const resB = await fetchProvisionAtStage(env, inst, verB, normProv);
    const diff = simpleLineDiff(extractBodyLines(resA.text || ""), extractBodyLines(resB.text || ""));
    return {
      instrument_path: inst.path,
      requested_provision: normProv,
      concordance_resolved: { stage_a_provision: resA.resolved, stage_b_provision: resB.resolved },
      stage_a: { stage: verA.stage, date: verA.date, author: `${verA.author_name} <${verA.author_email}>` },
      stage_b: { stage: verB.stage, date: verB.date, author: `${verB.author_name} <${verB.author_email}>` },
      stats: { lines_added: diff.added, lines_removed: diff.removed },
      unified_diff: diff.unified
    };
  }

  if (name === "blame_provision") {
    const inst = findInst(String(args.instrument_path || ""));
    if (!inst) return { error: `Unknown instrument_path: ${args.instrument_path}` };
    const normProv = normalizeProvision(String(args.provision || ""));
    const snapshots: Array<{ ver: any; lines: string[]; resolved: string }> = [];

    for (const ver of inst.versions || []) {
      if (ver.source_type === "regulatory_supplement" || ver.patch_mode) continue;
      const res = await fetchProvisionAtStage(env, inst, ver, normProv);
      if (!res.text) continue;
      const lines = extractBodyLines(res.text);
      if (lines.length) snapshots.push({ ver, lines, resolved: res.resolved });
    }

    if (!snapshots.length) return { error: `Provision '${normProv}' not found across stages of '${inst.path}'.` };

    const metaOf = (ver: any) => ({
      stage: ver.stage,
      stage_label: ver.stage_label,
      date: ver.date,
      document_symbol: ver.document_symbol,
      author: `${ver.author_name} <${ver.author_email}>`
    });

    let prevTokens = tokenizeBlame(snapshots[0].lines.join(" "));
    let prevOwners = new Array(prevTokens.length).fill(metaOf(snapshots[0].ver));

    for (let s = 1; s < snapshots.length; s++) {
      const curTokens = tokenizeBlame(snapshots[s].lines.join(" "));
      const curMeta = metaOf(snapshots[s].ver);
      prevOwners = alignTokenOwners(prevTokens, prevOwners, curTokens, curMeta);
      prevTokens = curTokens;
    }

    const latest = snapshots[snapshots.length - 1];
    const latestClauses = latest.lines.flatMap((l) => l.split(/(?<=[.;:])\s+/).filter(Boolean));
    let cursor = 0;
    const blame = latestClauses.map((clause, idx) => {
      const cToks = tokenizeBlame(clause);
      const slice = prevOwners.slice(cursor, cursor + cToks.length);
      cursor += cToks.length;
      const owners = slice.length ? slice : [metaOf(latest.ver)];

      const counts = new Map<string, { meta: any; count: number }>();
      for (const o of owners) {
        const k = `${o.author} [${o.stage}@${o.date}]`;
        const prev = counts.get(k);
        if (prev) prev.count++;
        else counts.set(k, { meta: o, count: 1 });
      }
      const sorted = Array.from(counts.values()).sort((a, b) => b.count - a.count);
      const dom = sorted[0].meta;
      const total = Math.max(1, owners.length);

      return {
        clause_number: idx + 1,
        primary_institutional_author: dom.author,
        introduced_in_stage: dom.stage,
        introduced_on_date: dom.date,
        document_symbol: dom.document_symbol,
        contributors: sorted.map((s) => ({
          institutional_author: s.meta.author,
          stage: s.meta.stage,
          date: s.meta.date,
          token_share_pct: Number(((100 * s.count) / total).toFixed(1))
        })),
        text: clause
      };
    });

    return {
      instrument_path: inst.path,
      provision: normProv,
      attribution_algorithm: "sequential_token_lcs_concordance_v3",
      latest_stage: latest.ver.stage,
      latest_date: latest.ver.date,
      stages_analyzed: snapshots.map((s) => ({
        stage: s.ver.stage,
        date: s.ver.date,
        provision: s.resolved,
        author: `${s.ver.author_name} <${s.ver.author_email}>`
      })),
      blame
    };
  }

  if (name === "check_applicability") {
    return await checkApplicability(env, args);
  }

  if (name === "verify_citations") {
    const draft = String(args.draft_text || "");
    const asOf = args.as_of_date || new Date().toISOString().slice(0, 10);
    const detectors: Array<[RegExp, string]> = [
      [/EU\s+AI\s+Act|Regulation\s*\(EU\)\s*2024\/1689/gi, "eu/ai-act"],
      [/\bGDPR\b|Regulation\s*\(EU\)\s*2016\/679/gi, "eu/gdpr"],
      [/Cyber\s+Resilience\s+Act|\bCRA\b|Regulation\s*\(EU\)\s*2024\/2847/gi, "eu/cyber/cra"],
      [/NIS\s*2|Directive\s*\(EU\)\s*2022\/2555/gi, "eu/cyber/nis2"],
      [/\bDORA\b|Regulation\s*\(EU\)\s*2022\/2554/gi, "eu/cyber/dora"],
      [/CETS\s*(?:No\.?\s*)?225|CoE\s+AI\s+Convention/gi, "coe/ai-convention"],
      [/Additional\s+Protocol\s+II|\bAP\s*II\b/gi, "ihl/additional-protocol-ii"],
      [/Additional\s+Protocol\s+I\b|\bAP\s*I\b|Geneva\s+Conventions?/gi, "ihl/geneva-conventions"],
      [/UN\s+Cybercrime\s+Convention|Hanoi\s+Convention|A\/RES\/79\/243/gi, "un/cybercrime-convention"],
      [/Budapest\s+Convention|ETS\s*(?:No\.?\s*)?185/gi, "coe/budapest-convention"]
    ];

    const checks: any[] = [];
    const seen = new Set<string>();
    const warnings: string[] = [];
    const fetchedForQuotes: Array<{ label: string; text: string }> = [];

    for (const sent of draft.split(/(?<=[.!?\n])\s+/)) {
      const anchors: Array<{ idx: number; path: string; label: string }> = [];
      for (const [rx, path] of detectors) {
        for (const m of sent.matchAll(rx)) {
          anchors.push({ idx: m.index ?? 0, path, label: m[0] });
        }
      }
      if (!anchors.length) continue;
      anchors.sort((a, b) => a.idx - b.idx);

      for (const am of sent.matchAll(/\bArticles?\s+(\d+[a-z]?)\b/gi)) {
        const pos = am.index ?? 0;
        const preceding = anchors.filter((a) => a.idx <= pos);
        const anc = preceding.length ? preceding[preceding.length - 1] : anchors[0];
        const normProv = normalizeProvision(am[1]);
        const key = `${anc.path}::${normProv}`;
        if (seen.has(key)) continue;
        seen.add(key);

        const inst = findInst(anc.path);
        let text: string | null = null;
        if (inst) {
          const latest = resolveStage(inst, undefined);
          text = (await fetchProvisionAtStage(env, inst, latest, normProv)).text;
          if (!text && anc.path === "eu/ai-act") {
            text = (await fetchProvisionAtStage(env, inst, resolveStage(inst, "official_journal_final"), normProv)).text;
          }
        }
        const bitemp = await checkApplicability(env, { instrument_path: anc.path, provision: normProv, as_of_date: asOf });
        const verdict = !text ? "NOT_IN_CORPUS_OR_NONEXISTENT" : bitemp.legal_status === "REVOKED" ? "REVOKED" : "VERIFIED";
        if (text) fetchedForQuotes.push({ label: `${anc.path}/${normProv}`, text });
        checks.push({ citation_match: `${anc.label} ${am[0]}`, instrument_path: anc.path, provision: normProv, verdict, bitemporal_status: bitemp.legal_status });
      }
    }

    if (/Executive\s+Order\s+14110|\bEO\s*14110\b/i.test(draft) && !/revok|rescind|repeal/i.test(draft)) {
      warnings.push("CRITICAL BITEMPORAL WARNING: Draft cites US Executive Order 14110 without noting its formal revocation on 2025-01-20.");
      checks.push({ citation_match: "Executive Order 14110", instrument_path: "national/us/nist-ai-rmf", provision: "eo-14110", verdict: "REVOKED_STATUTE_CITED_AS_ACTIVE", bitemporal_status: "REVOKED" });
    }

    if (/PL\s*2338(?:\/2023)?/i.test(draft) && /\b(?:enacted|in\s+force|currently\s+enforceable)\b/i.test(draft) && !/pending|bill|not\s+yet\s+enacted|chamber\s+of\s+deputies|review/i.test(draft)) {
      warnings.push("BITEMPORAL STATUS WARNING: Brazil PL 2338/2023 remains pending in the Chamber of Deputies Special Committee — it is NOT YET ENACTED.");
    }

    const quoteChecks: any[] = [];
    for (const qm of draft.matchAll(/"([^"]{30,400})"/g)) {
      const q = qm[1].replace(/\s+/g, " ").trim();
      const qLow = q.toLowerCase();
      let matched: string | null = null;
      for (const src of fetchedForQuotes) {
        if (src.text.replace(/\s+/g, " ").toLowerCase().includes(qLow)) {
          matched = src.label;
          break;
        }
      }
      quoteChecks.push({
        quote_excerpt: q.length > 120 ? q.slice(0, 120) + "..." : q,
        verdict: matched ? "EXACT_MATCH" : (fetchedForQuotes.length ? "UNVERIFIED_OR_PARAPHRASED" : "NO_CITED_PROVISION_TO_CHECK"),
        matched_source: matched
      });
    }

    const failed = checks.filter((c) => ["NOT_IN_CORPUS_OR_NONEXISTENT", "REVOKED_STATUTE_CITED_AS_ACTIVE"].includes(c.verdict));
    return {
      aba_formal_opinion_512_audit: !failed.length && !warnings.length ? "PASS" : "REQUIRES_ATTORNEY_CORRECTION",
      as_of_date: asOf,
      citations_checked: checks.length,
      citations_failed: failed.length,
      warnings,
      citation_checks: checks,
      quote_checks: quoteChecks
    };
  }

  if (name === "search_corpus") {
    const bm25 = await fetchCorpusJson(env, "bm25-index.json");
    if (!bm25) return { error: "bm25-index.json unavailable" };
    const raw = (String(args.query || "").toLowerCase().match(/[a-z0-9]{2,}/g) || []).map(normalizeToken);
    const expanded: string[] = [];
    for (const t of raw) {
      expanded.push(t);
      if (LEGAL_SYNONYMS[t]) expanded.push(...LEGAL_SYNONYMS[t]);
    }
    const terms = Array.from(new Set(expanded));
    const jf = args.jurisdiction ? String(args.jurisdiction).toLowerCase() : null;
    const scores: Record<number, number> = {};
    const avgdl = bm25.avgdl || 100;
    for (const t of terms) {
      const plist = bm25.postings[t];
      if (!plist) continue;
      const idf = bm25.idf[t] || 1.0;
      for (const [docId, tf] of plist) {
        const doc = bm25.docs[docId];
        if (jf && doc.jurisdiction.toLowerCase() !== jf) continue;
        const dl = doc.dl || 100;
        scores[docId] = (scores[docId] || 0) + idf * ((tf * 2.5) / (tf + 1.5 * (0.25 + 0.75 * (dl / avgdl))));
      }
    }
    const top = Object.entries(scores).sort((a, b) => b[1] - a[1]).slice(0, 20).map(([id, sc]) => ({ bm25_score: Number(sc.toFixed(3)), ...bm25.docs[Number(id)] }));
    return { query: args.query, engine: "Edge-BM25+UK_US_Norm_v3", match_count: Object.keys(scores).length, results: top };
  }

  if (name === "get_citation_graph") {
    const graph = (await fetchCorpusJson(env, "graph.json")) || { nodes: [], edges: [], recital_links: {} };
    const norm = String(args.instrument_path || "").replace(/^\/+|\/+$/g, "").toLowerCase();
    return {
      instrument_path: norm,
      outgoing_edges: graph.edges.filter((e: any) => e.source.toLowerCase() === norm),
      incoming_edges: graph.edges.filter((e: any) => e.target.toLowerCase() === norm),
      recital_to_article_links: (graph.recital_links || {})[norm] || []
    };
  }

  if (name === "get_provenance_audit") {
    const prov = (await fetchCorpusJson(env, "provenance.json")) || { stages: [] };
    const stages = args.instrument_path
      ? prov.stages.filter((s: any) => s.instrument_path.toLowerCase() === String(args.instrument_path).toLowerCase())
      : prov.stages;
    return { built_utc: prov.built_utc, stages_returned: stages.length, stages };
  }

  return { error: `Unknown tool: ${name}` };
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization, Mcp-Session-Id",
      "X-Zero-Data-Retention": "true"
    };

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders });

    if (url.pathname === "/health" || (url.pathname === "/" && request.method === "GET")) {
      return new Response(
        JSON.stringify({
          service: "lex-machina-edge-mcp",
          version: "3.0.0",
          transport: "streamable-http",
          tools_count: TOOLS_SPEC.length,
          prompts_count: PROMPTS_SPEC.length,
          zero_data_retention: true,
          corpus: `${env.LEX_MACHINA_REPO || DEFAULT_REPO}@${env.LEX_MACHINA_BRANCH || DEFAULT_BRANCH}`
        }),
        { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    if (url.pathname === "/mcp" && request.method === "POST") {
      if (env.ENTERPRISE_API_KEY && (request.headers.get("Authorization") || "") !== `Bearer ${env.ENTERPRISE_API_KEY}`) {
        return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: corsHeaders });
      }

      const body = (await request.json()) as JsonRpcRequest;
      let result: any;

      if (body.method === "initialize") {
        result = {
          protocolVersion: "2025-03-26",
          capabilities: { tools: {}, resources: {}, prompts: {} },
          serverInfo: { name: "lex-machina", version: "3.0.0" }
        };
      } else if (body.method === "tools/list") {
        result = { tools: TOOLS_SPEC };
      } else if (body.method === "tools/call") {
        const payload = await executeTool(env, body.params?.name, body.params?.arguments || {});
        result = { content: [{ type: "text", text: JSON.stringify(payload, null, 2) }] };
      } else if (body.method === "resources/list") {
        result = {
          resources: [
            { uri: "lex://provenance", name: "SHA-256 Provenance Manifest", mimeType: "application/json" },
            { uri: "lex://applicability", name: "Bitemporal Enforceability Schedule", mimeType: "application/json" },
            { uri: "lex://concordance", name: "4-Column Article Concordance", mimeType: "application/json" },
            { uri: "lex://eval-scorecard", name: "LexMachina-Eval Empirical Scorecard", mimeType: "application/json" }
          ]
        };
      } else if (body.method === "resources/read") {
        const uri = String(body.params?.uri || "");
        const map: Record<string, string> = {
          "lex://provenance": "provenance.json",
          "lex://applicability": "applicability.json",
          "lex://concordance": "concordance.json",
          "lex://eval-scorecard": "eval-scorecard.json"
        };
        const file = map[uri];
        const text = file ? await fetchCorpusText(env, file) : null;
        result = { contents: [{ uri, mimeType: "application/json", text: text || "{}" }] };
      } else if (body.method === "prompts/list") {
        result = { prompts: PROMPTS_SPEC };
      } else if (body.method === "prompts/get") {
        const pname = String(body.params?.name || "");
        const pargs = body.params?.arguments || {};
        const promptText =
          pname === "audit_ai_system"
            ? `Audit AI system (${pargs.system_description || ""}) as of ${pargs.deployment_date || "2026-11-23"} using get_provision, check_applicability (Digital Omnibus 2026/1744), and verify_citations.`
            : pname === "travaux_redline"
            ? `Perform CJEU travaux preparatoires analysis on ${pargs.instrument_path || "eu/ai-act"} ${pargs.provision || "articles/article-005.md"} using blame_provision, diff_provisions, get_citation_graph, and verify_citations.`
            : pname === "cjeu_precedent_brief"
            ? `Synthesize binding CJEU case law (SCHUFA C-634/21, Schrems II C-311/18, Meta C-252/21, La Quadrature du Net C-511/18) for: ${pargs.legal_issue || ""} using search_corpus, get_provision, get_citation_graph, and verify_citations.`
            : `Perform an Additional Protocol I Article 36, ICJ Nuclear Weapons Opinion & UN CCW LAWS legal weapons review on ${pargs.weapons_system_description || ""} using get_provision and verify_citations.`;
        result = { messages: [{ role: "user", content: { type: "text", text: promptText } }] };
      } else {
        return new Response(
          JSON.stringify({ jsonrpc: "2.0", id: body.id ?? null, error: { code: -32601, message: "Method not found" } }),
          { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }

      return new Response(
        JSON.stringify({ jsonrpc: "2.0", id: body.id ?? null, result }),
        { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    return new Response("Not Found", { status: 404, headers: corsHeaders });
  }
};
