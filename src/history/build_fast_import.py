"""
Deterministic `git fast-import` Stream Engine (`src/history/build_fast_import.py`).

Builds `refs/heads/corpus` with strict GitHub `git fsck --strict` timestamp
compliance:
- Pre-1970 instruments (such as the 1949 Geneva Conventions) are mapped
  sequentially into the first seconds of `1970-01-01T00:00:XX +0000` sorted
  chronologically, while preserving the true historical date in the commit
  subject (`[1949-08-12] Adopt Geneva Conventions I-IV...`) and `metadata.json`.
- Post-1970 instruments sharing the same calendar day have their Unix timestamp
  incremented by `+1` second per commit for deterministic topological ordering.
- Also generates `graph.json`, `search-index.json`, and `search-index.sqlite`
  (SQLite FTS5) inside the `corpus` orphan branch.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

# Ensure `src` is importable when invoked as `python -m src.history.build_fast_import`
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ingest.eurlex_fetcher import fetch_eurlex_stage
from src.ingest.national_fetcher import fetch_national_stage
from src.ingest.un_coe_fetcher import fetch_un_coe_stage
from src.parser.diff_graph import build_citation_graph
from src.parser.normalizer import render_stage_files


def compute_fsck_safe_timestamps(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Sort all legislative stage events chronologically by their true historical
    date (`YYYY-MM-DD`) and assign strictly increasing, non-negative Unix
    timestamps compliant with GitHub's `git fsck --strict`.
    """
    sorted_events = sorted(
        events,
        key=lambda e: (e["version"]["date"], e["instrument"]["id"], e["version"]["stage"]),
    )

    pre_1970_counter = 10  # 1970-01-01T00:00:10Z onwards for pre-1970 treaties
    last_post_1970_ts = 0

    for event in sorted_events:
        date_str = event["version"]["date"]
        parsed_date = dt.date.fromisoformat(date_str)
        if parsed_date.year < 1970:
            unix_ts = pre_1970_counter
            pre_1970_counter += 1
        else:
            # 12:00:00 UTC on the publication date
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
    """Dispatch stage ingestion to the appropriate specialized fetcher."""
    source_type = version.get("source_type", "un_coe")
    if source_type == "eurlex":
        return fetch_eurlex_stage(instrument, version, cache_dir=cache_dir)
    if source_type == "national":
        return fetch_national_stage(instrument, version, cache_dir=cache_dir)
    return fetch_un_coe_stage(instrument, version, cache_dir=cache_dir)


def build_search_index_json(
    catalog: dict[str, Any],
    cumulative_tree: dict[str, str],
    commit_log_manifest: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Build `search-index.json` containing all indexed articles, recitals, annexes,
    and chronological commit metadata across every instrument.
    """
    entries: list[dict[str, Any]] = []
    instruments_by_path = {inst["path"]: inst for inst in catalog.get("instruments", [])}

    for rel_path, content in sorted(cumulative_tree.items()):
        if not rel_path.endswith(".md"):
            continue
        if rel_path.endswith("/full-text.md") or rel_path.endswith("/instrument.md") or rel_path.endswith("/preamble/recitals.md"):
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
        # Extract body lines (skip metadata bullet lines)
        body_lines = [
            line
            for line in lines[1:]
            if not line.startswith("- **")
        ]
        body_text = "\n".join(body_lines)

        latest_version = matched_inst["versions"][-1]
        entries.append(
            {
                "instrument_id": matched_inst["id"],
                "instrument_path": matched_inst["path"],
                "instrument_title": matched_inst.get("short_title", matched_inst["title"]),
                "jurisdiction": matched_inst["jurisdiction"],
                "provision": provision_rel,
                "full_path": rel_path,
                "heading": heading,
                "latest_stage": latest_version["stage"],
                "latest_date": latest_version["date"],
                "latest_author": f"{latest_version['author_name']} <{latest_version['author_email']}>",
                "text": body_text,
            }
        )

    return {
        "schema_version": "1.0.0",
        "total_provisions": len(entries),
        "commits": commit_log_manifest,
        "entries": entries,
    }


def build_sqlite_fts5_bytes(search_index: dict[str, Any]) -> bytes:
    """
    Build a lightweight SQLite FTS5 full-text search database in a temporary
    in-memory/disk buffer and return its raw bytes for inclusion on `corpus`.
    """
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
                provision,
                heading,
                latest_stage,
                latest_date,
                latest_author,
                text
            );
            """
        )
        for entry in search_index.get("entries", []):
            cur.execute(
                """
                INSERT INTO provisions_fts (
                    instrument_path, jurisdiction, provision, heading,
                    latest_stage, latest_date, latest_author, text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    entry["instrument_path"],
                    entry["jurisdiction"],
                    entry["provision"],
                    entry["heading"],
                    entry["latest_stage"],
                    entry["latest_date"],
                    entry["latest_author"],
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
    """Emit an inline `M 100644 inline <path>` entry into the fast-import stream."""
    header = f"M 100644 inline {repo_path}\ndata {len(payload_bytes)}\n".encode("utf-8")
    stream_parts.append(header)
    stream_parts.append(payload_bytes)
    stream_parts.append(b"\n")


def generate_fast_import_stream(
    catalog_path: Path,
    cache_dir: Path | None = None,
    include_sqlite: bool = True,
) -> bytes:
    """
    Generate the complete deterministic `git fast-import` byte stream that
    constructs `refs/heads/corpus` with one commit per historical legislative stage
    authored by the exact institutional actor, followed by an index/graph commit.
    """
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    raw_events: list[dict[str, Any]] = []
    for inst in catalog.get("instruments", []):
        for ver in inst.get("versions", []):
            raw_events.append({"instrument": inst, "version": ver})

    ordered_events = compute_fsck_safe_timestamps(raw_events)

    stream_parts: list[bytes] = []
    cumulative_tree: dict[str, str] = {}
    commit_log_manifest: list[dict[str, Any]] = []
    mark_id = 1

    # Always keep a copy of catalog.json at the root of `corpus` so remote clients can inspect it
    catalog_bytes = json.dumps(catalog, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"

    for idx, event in enumerate(ordered_events):
        inst = event["instrument"]
        ver = event["version"]
        git_ts = event["git_timestamp"]

        stage_payload = fetch_stage_for_event(inst, ver, cache_dir=cache_dir)
        stage_files = render_stage_files(inst, ver, stage_payload)

        # Update cumulative tree for this instrument
        inst_prefix = f"{inst['path'].strip('/')}/"
        stale_keys = [
            k for k in cumulative_tree if k.startswith(inst_prefix) and k not in stage_files
        ]
        for k in stale_keys:
            del cumulative_tree[k]
        cumulative_tree.update(stage_files)

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
            f"Source URL: {ver.get('source_url', 'N/A')}\n\n"
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

        # Delete any provisions removed between negotiating stages
        for deleted_path in stale_keys:
            stream_parts.append(f"D {deleted_path}\n".encode("utf-8"))

        # Write catalog.json on first commit
        if idx == 0:
            write_fast_import_blob_and_modify(stream_parts, "catalog.json", catalog_bytes)

        # Write all files for this stage
        for rel_path, content_str in sorted(stage_files.items()):
            write_fast_import_blob_and_modify(
                stream_parts,
                rel_path,
                content_str.encode("utf-8"),
            )

        # Also write a deterministic stage snapshot manifest so stage lookups work effortlessly
        snapshot_rel_path = f"snapshots/{inst['path'].strip('/')}/{ver['stage']}.json"
        snapshot_data = {
            "instrument_id": inst["id"],
            "instrument_path": inst["path"],
            "stage": ver["stage"],
            "stage_label": ver["stage_label"],
            "date": ver["date"],
            "document_symbol": ver["document_symbol"],
            "author_name": ver["author_name"],
            "author_email": ver["author_email"],
            "commit_subject": commit_subject,
            "files": stage_files,
        }
        write_fast_import_blob_and_modify(
            stream_parts,
            snapshot_rel_path,
            json.dumps(snapshot_data, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
        )

        stream_parts.append(b"\n")

        commit_log_manifest.append(
            {
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
                "commit_subject": commit_subject,
            }
        )

    # Final index & citation graph commit on refs/heads/corpus
    final_ts = ordered_events[-1]["git_timestamp"] + 1 if ordered_events else 1730000000
    graph_data = build_citation_graph(catalog, cumulative_tree)
    search_index_data = build_search_index_json(catalog, cumulative_tree, commit_log_manifest)

    index_commit_mark = mark_id
    index_msg = (
        b"[corpus-index] Build citation graph.json, search-index.json, and FTS5 SQLite index\n"
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

    write_fast_import_blob_and_modify(
        stream_parts,
        "catalog.json",
        catalog_bytes,
    )
    write_fast_import_blob_and_modify(
        stream_parts,
        "graph.json",
        json.dumps(graph_data, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
    )
    write_fast_import_blob_and_modify(
        stream_parts,
        "search-index.json",
        json.dumps(search_index_data, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
    )

    if include_sqlite:
        sqlite_bytes = build_sqlite_fts5_bytes(search_index_data)
        write_fast_import_blob_and_modify(
            stream_parts,
            "search-index.sqlite",
            sqlite_bytes,
        )

    stream_parts.append(b"\ndone\n")
    return b"".join(stream_parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic git fast-import stream for refs/heads/corpus."
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=ROOT_DIR / "src" / "catalog.json",
        help="Path to declarative catalog.json",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Optional directory for .json.gz stage caching (pipeline-cache)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file for fast-import stream (defaults to stdout)",
    )
    parser.add_argument(
        "--no-sqlite",
        action="store_true",
        help="Skip building binary search-index.sqlite inside fast-import stream",
    )
    args = parser.parse_args()

    stream_bytes = generate_fast_import_stream(
        catalog_path=args.catalog,
        cache_dir=args.cache_dir,
        include_sqlite=not args.no_sqlite,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(stream_bytes)
        print(
            f"[lex-machina] Wrote {len(stream_bytes):,} bytes to {args.output}",
            file=sys.stderr,
        )
    else:
        sys.stdout.buffer.write(stream_bytes)


if __name__ == "__main__":
    main()
