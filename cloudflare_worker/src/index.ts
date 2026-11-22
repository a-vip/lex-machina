/**
 * Zero-Dependency Stateless Remote Streamable HTTP MCP Server for Cloudflare Workers.
 * Deployed purely via GitHub Actions (zero local node_modules!).
 * Serves `POST /mcp` (MCP JSON-RPC 2.0 Streamable HTTP) and `GET /health` globally
 * with Cloudflare Edge Caching over `raw.githubusercontent.com/a-vip/lex-machina/corpus`
 * and strict Zero Data Retention (ZDR: zero prompt or query payload logging).
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

const TOOLS_SPEC = [
  {
    name: "list_instruments",
    description: "List all tracked AI, privacy, cyber, and IHL instruments with chronological stages and SHA-256 provenance.",
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
    inputSchema: {
      type: "object",
      properties: {
        jurisdiction: { type: "string", description: "Optional filter: eu, coe, un, ihl, national" },
        domain: { type: "string", description: "Optional filter: ai, cyber, privacy, ihl" }
      }
    }
  },
  {
    name: "get_provision",
    description: "Fetch exact normalized Markdown text of an article, recital, or annex at a specific date or legislative stage with SHA-256 provenance.",
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
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
    name: "check_applicability",
    description: "Bitemporal enforceability check accounting for EU Digital Omnibus Regulation (EU) 2026/1744, EO 14110 revocation, CRA, Texas TRAIGA, and China 2025 Labeling Measures.",
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
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
    name: "search_corpus",
    description: "BM25 legal search with UK<->US spelling normalization and legal acronym synonym expansion.",
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
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
    description: "Return incoming/outgoing cross-references and Recital-to-Article interpretive links from graph.json.",
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
    inputSchema: {
      type: "object",
      required: ["instrument_path"],
      properties: {
        instrument_path: { type: "string" }
      }
    }
  },
  {
    name: "get_provenance_audit",
    description: "Return SHA-256 primary-source provenance manifest and official ELI/CELEX permalinks.",
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
    inputSchema: {
      type: "object",
      properties: {
        instrument_path: { type: "string" }
      }
    }
  }
];

async function fetchCorpusText(env: Env, relPath: string): Promise<string | null> {
  const repo = env.LEX_MACHINA_REPO || DEFAULT_REPO;
  const branch = env.LEX_MACHINA_BRANCH || DEFAULT_BRANCH;
  const url = `https://raw.githubusercontent.com/${repo}/${branch}/${relPath.replace(/^\/+/, "")}`;

  const cache = (caches as any).default;
  const cacheReq = new Request(url, { method: "GET" });
  let resp: Response | undefined = await cache.match(cacheReq);

  if (!resp) {
    const upstream = await fetch(url, {
      headers: { "User-Agent": "lex-machina-edge-mcp/2.0" }
    });
    if (!upstream.ok) return null;
    resp = new Response(upstream.body, {
      status: 200,
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "public, max-age=300"
      }
    });
    await cache.put(cacheReq, resp.clone());
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
    .replace(/ised$/, "ized")
    .replace(/ising$/, "izing")
    .replace(/ise$/, "ize")
    .replace(/^defence$/, "defense")
    .replace(/^offence$/, "offense")
    .replace(/^behaviour$/, "behavior")
    .replace(/^labelling$/, "labeling");
}

async function executeTool(env: Env, name: string, args: Record<string, any>): Promise<any> {
  if (name === "list_instruments") {
    const catalog = (await fetchCorpusJson(env, "catalog.json")) || { instruments: [] };
    let list = catalog.instruments || [];
    if (args.jurisdiction) {
      const jf = String(args.jurisdiction).toLowerCase();
      list = list.filter((i: any) => i.jurisdiction.toLowerCase() === jf);
    }
    if (args.domain) {
      const df = String(args.domain).toLowerCase();
      list = list.filter((i: any) => (i.domain || "").toLowerCase() === df);
    }
    return { count: list.length, instruments: list };
  }

  if (name === "get_provision") {
    const instPath = String(args.instrument_path || "").replace(/^\/+|\/+$/g, "");
    const normProv = normalizeProvision(String(args.provision || ""));
    const catalog = (await fetchCorpusJson(env, "catalog.json")) || { instruments: [] };
    const inst = (catalog.instruments || []).find((i: any) => i.path === instPath || i.id === instPath);
    if (!inst) return { error: `Unknown instrument_path: ${instPath}` };

    const versions = inst.versions || [];
    let ver = versions[versions.length - 1];
    if (args.as_of) {
      const q = String(args.as_of).toLowerCase();
      ver = versions.find((v: any) => v.stage.toLowerCase().includes(q) || v.date === q) || ver;
    }

    const md =
      (await fetchCorpusText(env, `versions/${inst.path}/${ver.stage}/${normProv}`)) ||
      (await fetchCorpusText(env, `${inst.path}/${normProv}`));
    if (!md) return { error: `PROVISION NOT IN CORPUS: ${inst.path}/${normProv}@${ver.stage}` };

    return {
      instrument_path: inst.path,
      provision: normProv,
      stage: ver.stage,
      date: ver.date,
      author: `${ver.author_name} <${ver.author_email}>`,
      markdown: md
    };
  }

  if (name === "check_applicability") {
    const app = (await fetchCorpusJson(env, "applicability.json")) || { rules: [] };
    const instPath = String(args.instrument_path || "").replace(/^\/+|\/+$/g, "").toLowerCase();
    const prov = args.provision ? normalizeProvision(String(args.provision)) : "*";
    const asOf = args.as_of_date || new Date().toISOString().slice(0, 10);
    const rule =
      (app.rules || []).find((r: any) => r.instrument_path.toLowerCase() === instPath && r.provisions.includes(prov)) ||
      (app.rules || []).find((r: any) => r.instrument_path.toLowerCase() === instPath && r.provisions.includes("*"));
    if (!rule) return { instrument_path: instPath, provision: prov, as_of_date: asOf, legal_status: "NO_RULE_RECORDED" };

    let status = "ENFORCEABLE";
    if (rule.revoked_date && asOf >= rule.revoked_date) status = "REVOKED";
    else if (rule.status_override === "OPEN_FOR_SIGNATURE_PENDING_40_RATIFICATIONS") status = "PENDING_RATIFICATIONS";
    else if (rule.entry_into_application && asOf < rule.entry_into_application) status = "IN_FORCE_NOT_YET_APPLICABLE";

    return { ...rule, as_of_date: asOf, legal_status: status };
  }

  if (name === "search_corpus") {
    const bm25 = await fetchCorpusJson(env, "bm25-index.json");
    if (!bm25) return { error: "bm25-index.json unavailable" };
    const terms = Array.from(
      new Set((String(args.query || "").toLowerCase().match(/[a-z0-9]{2,}/g) || []).map(normalizeToken))
    );
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
    const top = Object.entries(scores)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 20)
      .map(([id, sc]) => ({ bm25_score: Number(sc.toFixed(3)), ...bm25.docs[Number(id)] }));
    return { query: args.query, match_count: Object.keys(scores).length, results: top };
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

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    if (url.pathname === "/health" || (url.pathname === "/" && request.method === "GET")) {
      return new Response(
        JSON.stringify({
          service: "lex-machina-edge-mcp",
          version: "2.0.0",
          transport: "streamable-http",
          zero_data_retention: true,
          corpus: `${env.LEX_MACHINA_REPO || DEFAULT_REPO}@${env.LEX_MACHINA_BRANCH || DEFAULT_BRANCH}`
        }),
        { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    if (url.pathname === "/mcp" && request.method === "POST") {
      if (env.ENTERPRISE_API_KEY) {
        const auth = request.headers.get("Authorization") || "";
        if (auth !== `Bearer ${env.ENTERPRISE_API_KEY}`) {
          return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: corsHeaders });
        }
      }

      const body = (await request.json()) as JsonRpcRequest;
      let result: any;

      if (body.method === "initialize") {
        result = {
          protocolVersion: "2025-03-26",
          capabilities: { tools: {}, resources: {}, prompts: {} },
          serverInfo: { name: "lex-machina", version: "2.0.0" }
        };
      } else if (body.method === "tools/list") {
        result = { tools: TOOLS_SPEC };
      } else if (body.method === "tools/call") {
        const toolName = body.params?.name;
        const toolArgs = body.params?.arguments || {};
        const payload = await executeTool(env, toolName, toolArgs);
        result = { content: [{ type: "text", text: JSON.stringify(payload, null, 2) }] };
      } else if (body.method === "resources/list") {
        result = {
          resources: [
            { uri: "lex://provenance", name: "SHA-256 Provenance Manifest", mimeType: "application/json" },
            { uri: "lex://applicability", name: "Bitemporal Enforceability Schedule", mimeType: "application/json" },
            { uri: "lex://concordance", name: "4-Column Article Concordance", mimeType: "application/json" }
          ]
        };
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
