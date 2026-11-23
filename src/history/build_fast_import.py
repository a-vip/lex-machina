"""
Deterministic `git fast-import` Stream Engine (`src/history/build_fast_import.py` — v2.0).

Builds `refs/heads/corpus` on GitHub Actions with:
- Strict GitHub `git fsck --strict` timestamp compliance (pre-1970 treaties mapped
  sequentially from `1970-01-01T00:00:10Z` with true historical dates in commit subject
  and `metadata.json`).
- Per-stage lightweight addressable paths (`versions/<instrument_path>/<stage>/<provision>`)
  in addition to live chronological tree commits (`<instrument_path>/<provision>`), so
  remote MCP / Cloudflare Edge workers fetch only a single ~3 KB article instead of
  multi-megabyte JSON blobs.
- Full cryptographic `provenance.json`, `concordance.json`, `applicability.json`,
  `graph.json`, `bm25-index.json`, `search-index.json`, and `search-index.sqlite` (FTS5).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ingest.eurlex_fetcher import fetch_eurlex_stage
from src.ingest.national_fetcher import fetch_national_stage
from src.ingest.un_coe_fetcher import fetch_un_coe_stage
from src.parser.bm25_index import build_bm25_index
from src.parser.diff_graph import build_citation_graph
from src.parser.normalizer import render_stage_files


def compute_fsck_safe_timestamps(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sorted_events = sorted(
        events,
        key=lambda e: (e["version"]["date"], e["instrument"]["id"], e["version"]["stage"]),
    )

    pre_1970_counter = 10
    last_post_1970_ts = 0

    for event in sorted_events:
        parsed_date = dt.date.fromisoformat(event["version"]["date"])
        if parsed_date.year < 1970:
            unix_ts = pre_1970_counter
            pre_1970_counter += 1
        else:
            base_dt = dt.datetime(
                parsed_date.year,
                parsed_date.month,
                parsed_date.day,
                12,
                0,
                0,
                tzinfo=dt.timezone.utc,
            )
            unix_ts = int(base_dt.timestamp())
            if unix_ts <= last_post_1970_ts:
                unix_ts = last_post_1970_ts + 1
            last_post_1970_ts = unix_ts
        event["git_timestamp"] = unix_ts

    return sorted_events


def fetch_stage_for_event(
    instrument: dict[str, Any],
    version: dict[str, Any],
    cache_dir: Path | None,
) -> dict[str, Any]:
    source_type = version.get("source_type", "un_coe_pdf")
    if source_type in ("eurlex", "eurlex_cellar", "consilium_pdf", "europarl_html", "ec_guideline_pdf", "cjeu_cellar"):
        return fetch_eurlex_stage(instrument, version, cache_dir=cache_dir)
    if source_type in ("national", "national_pdf", "national_web", "cn_cac_html", "us_tx_html", "framework_pdf"):
        return fetch_national_stage(instrument, version, cache_dir=cache_dir)
    if source_type == "regulatory_supplement":
        if instrument["jurisdiction"] == "eu":
            return fetch_eurlex_stage(instrument, version, cache_dir=cache_dir)
        if instrument["jurisdiction"] in ("national", "standards"):
            return fetch_national_stage(instrument, version, cache_dir=cache_dir)
        return fetch_un_coe_stage(instrument, version, cache_dir=cache_dir)
    return fetch_un_coe_stage(instrument, version, cache_dir=cache_dir)


def build_search_index_json(
    catalog: dict[str, Any],
    cumulative_tree: dict[str, str],
    commit_log_manifest: list[dict[str, Any]],
    latest_provenance_by_path: dict[str, str],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    instruments_by_path = {inst["path"]: inst for inst in catalog.get("instruments", [])}

    for rel_path, content in sorted(cumulative_tree.items()):
        if not rel_path.endswith(".md"):
            continue
        if (
            rel_path.endswith("/full-text.md")
            or rel_path.endswith("/instrument.md")
            or rel_path.endswith("/preamble/recitals.md")
        ):
            continue

        matched_inst = None
        provision_rel = ""
        for inst_path, inst in instruments_by_path.items():
            prefix = f"{inst_path}/"
            if rel_path.startswith(prefix):
                matched_inst = inst
                provision_rel = rel_path[len(prefix) :]
                break

        if not matched_inst:
            continue

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        heading = lines[0].lstrip("# ").strip() if lines else provision_rel
        body_lines = [line for line in lines[1:] if not line.startswith("- **")]
        body_text = "\n".join(body_lines)

        latest_version = matched_inst["versions"][-1]
        entries.append({
            "instrument_id": matched_inst["id"],
            "instrument_path": matched_inst["path"],
            "instrument_title": matched_inst.get("short_title", matched_inst["title"]),
            "jurisdiction": matched_inst["jurisdiction"],
            "domain": matched_inst.get("domain", "ai"),
            "provision": provision_rel,
            "full_path": rel_path,
            "heading": heading,
            "latest_stage": latest_version["stage"],
            "latest_date": latest_version["date"],
            "latest_author": f"{latest_version['author_name']} <{latest_version['author_email']}>",
            "provenance_mode": latest_provenance_by_path.get(matched_inst["path"], "unknown"),
            "text": body_text,
        })

    return {
        "schema_version": "2.0.0",
        "total_provisions": len(entries),
        "commits": commit_log_manifest,
        "entries": entries,
    }


def build_sqlite_fts5_bytes(search_index: dict[str, Any]) -> bytes:
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        conn = sqlite3.connect(str(tmp_path))
        cur = conn.cursor()
        cur.execute(
            """
            CREATE VIRTUAL TABLE provisions_fts USING fts5(
                instrument_path,
                jurisdiction,
                domain,
                provision,
                heading,
                latest_stage,
                latest_date,
                latest_author,
                provenance_mode,
                text,
                tokenize = 'porter unicode61'
            );
            """
        )
        for entry in search_index.get("entries", []):
            cur.execute(
                """
                INSERT INTO provisions_fts (
                    instrument_path, jurisdiction, domain, provision, heading,
                    latest_stage, latest_date, latest_author, provenance_mode, text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    entry["instrument_path"],
                    entry["jurisdiction"],
                    entry.get("domain", "ai"),
                    entry["provision"],
                    entry["heading"],
                    entry["latest_stage"],
                    entry["latest_date"],
                    entry["latest_author"],
                    entry.get("provenance_mode", "unknown"),
                    entry["text"],
                ),
            )
        conn.commit()
        conn.close()
        return tmp_path.read_bytes()
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def write_fast_import_blob_and_modify(
    stream_parts: list[bytes],
    repo_path: str,
    payload_bytes: bytes,
) -> None:
    header = f"M 100644 inline {repo_path}\ndata {len(payload_bytes)}\n".encode("utf-8")
    stream_parts.append(header)
    stream_parts.append(payload_bytes)
    stream_parts.append(b"\n")


def generate_fast_import_stream(
    catalog_path: Path,
    cache_dir: Path | None = None,
    include_sqlite: bool = True,
) -> bytes:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    concordance_path = catalog_path.parent / "concordance.json"
    applicability_path = catalog_path.parent / "applicability.json"
    concordance = json.loads(concordance_path.read_text(encoding="utf-8")) if concordance_path.exists() else {}
    applicability = json.loads(applicability_path.read_text(encoding="utf-8")) if applicability_path.exists() else {}

    raw_events: list[dict[str, Any]] = []
    for inst in catalog.get("instruments", []):
        for ver in inst.get("versions", []):
            raw_events.append({"instrument": inst, "version": ver})

    ordered_events = compute_fsck_safe_timestamps(raw_events)

    stream_parts: list[bytes] = []
    cumulative_tree: dict[str, str] = {}
    commit_log_manifest: list[dict[str, Any]] = []
    provenance_records: list[dict[str, Any]] = []
    latest_provenance_by_path: dict[str, str] = {}
    mark_id = 1

    catalog_bytes = json.dumps(catalog, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"

    for idx, event in enumerate(ordered_events):
        inst = event["instrument"]
        ver = event["version"]
        git_ts = event["git_timestamp"]

        stage_payload = fetch_stage_for_event(inst, ver, cache_dir=cache_dir)
        stage_files = render_stage_files(inst, ver, stage_payload)
        prov = stage_payload.get("provenance", {})

        inst_prefix = f"{inst['path'].strip('/')}/"
        # Preserve enacted parent-act articles when applying supplements or amending regulations (patch_mode=True)
        is_supplement = ver.get("source_type") == "regulatory_supplement"
        is_patch_amendment = bool(ver.get("patch_mode"))

        if is_patch_amendment:
            stale_keys: list[str] = []
            # Route amending regulation into `<inst>/amendments/<stage>/` so parent 113 articles stay intact!
            remapped_stage_files: dict[str, str] = {}
            for rel_path, content_str in stage_files.items():
                sub_rel = rel_path[len(inst_prefix) :]
                remapped_stage_files[f"{inst_prefix}amendments/{ver['stage']}/{sub_rel}"] = content_str
            live_files_to_write = remapped_stage_files
        elif is_supplement:
            stale_keys = []
            live_files_to_write = stage_files
        else:
            stale_keys = [
                k for k in cumulative_tree if k.startswith(inst_prefix) and k not in stage_files
            ]
            for k in stale_keys:
                del cumulative_tree[k]
            live_files_to_write = stage_files

        cumulative_tree.update(live_files_to_write)
        if prov.get("provenance_mode") != "structured_regulatory_brief" or inst["path"] not in latest_provenance_by_path:
            latest_provenance_by_path[inst["path"]] = prov.get("provenance_mode", "unknown")

        commit_subject = ver.get(
            "commit_subject",
            f"[{ver['date']}] {inst['short_title']} — {ver['stage_label']} ({ver['document_symbol']})",
        )
        commit_body = (
            f"{commit_subject}\n\n"
            f"Instrument: {inst['title']}\n"
            f"Path: {inst['path']}\n"
            f"Stage: {ver['stage_label']} ({ver['stage']})\n"
            f"Document Symbol: {ver['document_symbol']}\n"
            f"Historical Publication Date: {ver['date']}\n"
            f"Institutional Author: {ver['author_name']} <{ver['author_email']}>\n"
            f"Provenance Mode: {prov.get('provenance_mode', 'unknown')}\n"
            f"Primary Source SHA-256: {prov.get('sha256_raw', 'n/a')}\n"
            f"Counts: {len(stage_payload.get('articles', []))} articles, "
            f"{len(stage_payload.get('recitals', []))} recitals, "
            f"{len(stage_payload.get('annexes', []))} annexes\n"
            f"Source URL: {prov.get('final_url') or ver.get('source_url', 'N/A')}\n\n"
            f"{ver.get('summary', '')}\n"
        ).encode("utf-8")

        commit_mark = mark_id
        mark_id += 1

        stream_parts.append(b"commit refs/heads/corpus\n")
        stream_parts.append(f"mark :{commit_mark}\n".encode("utf-8"))
        stream_parts.append(
            f"author {ver['author_name']} <{ver['author_email']}> {git_ts} +0000\n".encode("utf-8")
        )
        stream_parts.append(
            f"committer {ver['author_name']} <{ver['author_email']}> {git_ts} +0000\n".encode("utf-8")
        )
        stream_parts.append(f"data {len(commit_body)}\n".encode("utf-8"))
        stream_parts.append(commit_body)
        stream_parts.append(b"\n")

        if idx > 0:
            stream_parts.append(f"from :{commit_mark - 1}\n".encode("utf-8"))

        for deleted_path in stale_keys:
            stream_parts.append(f"D {deleted_path}\n".encode("utf-8"))

        if idx == 0:
            write_fast_import_blob_and_modify(stream_parts, "catalog.json", catalog_bytes)

        # Write live tree files AND lightweight per-stage addressable files under versions/<inst>/<stage>/
        stage_dir_prefix = f"versions/{inst['path'].strip('/')}/{ver['stage']}"
        for rel_path, content_str in sorted(live_files_to_write.items()):
            write_fast_import_blob_and_modify(stream_parts, rel_path, content_str.encode("utf-8"))
        for rel_path, content_str in sorted(stage_files.items()):
            sub_rel = rel_path[len(inst_prefix) :]
            if sub_rel not in ("full-text.md", "instrument.md"):
                write_fast_import_blob_and_modify(
                    stream_parts,
                    f"{stage_dir_prefix}/{sub_rel}",
                    content_str.encode("utf-8"),
                )

        stream_parts.append(b"\n")

        print(
            f"[lex-machina] Stage {idx + 1}/{len(ordered_events)}: {inst['path']}@{ver['stage']} "
            f"-> mode={prov.get('provenance_mode')} articles={len(stage_payload.get('articles', []))} "
            f"recitals={len(stage_payload.get('recitals', []))} annexes={len(stage_payload.get('annexes', []))}",
            file=sys.stderr,
        )

        provenance_records.append({
            "instrument_id": inst["id"],
            "instrument_path": inst["path"],
            "stage": ver["stage"],
            "stage_label": ver["stage_label"],
            "date": ver["date"],
            "document_symbol": ver["document_symbol"],
            "author": f"{ver['author_name']} <{ver['author_email']}>",
            "counts": {
                "articles": len(stage_payload.get("articles", [])),
                "recitals": len(stage_payload.get("recitals", [])),
                "annexes": len(stage_payload.get("annexes", [])),
            },
            **prov,
        })

        commit_log_manifest.append({
            "order": idx + 1,
            "instrument_id": inst["id"],
            "instrument_path": inst["path"],
            "stage": ver["stage"],
            "stage_label": ver["stage_label"],
            "date": ver["date"],
            "git_timestamp": git_ts,
            "document_symbol": ver["document_symbol"],
            "author_name": ver["author_name"],
            "author_email": ver["author_email"],
            "provenance_mode": prov.get("provenance_mode"),
            "sha256_raw": prov.get("sha256_raw"),
            "commit_subject": commit_subject,
        })

    # Final Index, Provenance, Concordance, Applicability & BM25 Commit
    final_ts = ordered_events[-1]["git_timestamp"] + 1 if ordered_events else 1790000000
    graph_data = build_citation_graph(catalog, cumulative_tree, concordance=concordance)
    search_index_data = build_search_index_json(
        catalog, cumulative_tree, commit_log_manifest, latest_provenance_by_path
    )
    bm25_data = build_bm25_index(search_index_data["entries"])
    provenance_manifest = {
        "schema_version": "2.0.0",
        "built_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_stages": len(provenance_records),
        "total_indexed_provisions": search_index_data["total_provisions"],
        "stages": provenance_records,
    }

    index_commit_mark = mark_id
    index_msg = (
        b"[corpus-index-v2] Build provenance.json, concordance.json, applicability.json, "
        b"bm25-index.json, graph.json, search-index.json & SQLite FTS5\n"
    )
    stream_parts.append(b"commit refs/heads/corpus\n")
    stream_parts.append(f"mark :{index_commit_mark}\n".encode("utf-8"))
    stream_parts.append(
        f"author Lex Machina Indexer <indexer@lex-machina.org> {final_ts} +0000\n".encode("utf-8")
    )
    stream_parts.append(
        f"committer Lex Machina Indexer <indexer@lex-machina.org> {final_ts} +0000\n".encode("utf-8")
    )
    stream_parts.append(f"data {len(index_msg)}\n".encode("utf-8"))
    stream_parts.append(index_msg)
    if ordered_events:
        stream_parts.append(f"from :{index_commit_mark - 1}\n".encode("utf-8"))

    for fname, obj in [
        ("catalog.json", catalog),
        ("concordance.json", concordance),
        ("applicability.json", applicability),
        ("provenance.json", provenance_manifest),
        ("graph.json", graph_data),
        ("search-index.json", search_index_data),
        ("bm25-index.json", bm25_data),
    ]:
        write_fast_import_blob_and_modify(
            stream_parts,
            fname,
            json.dumps(obj, ensure_ascii=False, separators=(",", ":") if fname == "bm25-index.json" else None, indent=None if fname == "bm25-index.json" else 2).encode("utf-8") + b"\n",
        )

    # Embed authoritative README.md and WHITEPAPER.md directly into the corpus orphan branch
    for doc_name in ("README.md", "WHITEPAPER.md"):
        doc_path = ROOT_DIR / doc_name
        if doc_path.exists():
            write_fast_import_blob_and_modify(
                stream_parts,
                doc_name,
                doc_path.read_bytes(),
            )

    if include_sqlite:
        sqlite_bytes = build_sqlite_fts5_bytes(search_index_data)
        write_fast_import_blob_and_modify(stream_parts, "search-index.sqlite", sqlite_bytes)

    stream_parts.append(b"\ndone\n")
    return b"".join(stream_parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate deterministic v2.0 git fast-import stream for refs/heads/corpus."
    )
    parser.add_argument("--catalog", type=Path, default=ROOT_DIR / "src" / "catalog.json")
    parser.add_argument("--cache-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--no-sqlite", action="store_true")
    args = parser.parse_args()

    stream_bytes = generate_fast_import_stream(
        catalog_path=args.catalog,
        cache_dir=args.cache_dir,
        include_sqlite=not args.no_sqlite,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(stream_bytes)
        print(f"[lex-machina] Wrote {len(stream_bytes):,} bytes to {args.output}", file=sys.stderr)
    else:
        sys.stdout.buffer.write(stream_bytes)


if __name__ == "__main__":
    main()
