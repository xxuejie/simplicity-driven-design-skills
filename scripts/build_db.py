#!/usr/bin/env python3
"""Build / merge a strategies.db from a distilled-corpus JSONL.

Bring-your-own-corpus: this repo ships the distilled layer only. Point this
script at your own JSONL (one strategy per line) to create or extend a
reference archive. Schema matches references/strategies.db.

Input JSONL record (all fields optional except thinker + one of
strategy_name/content):

    {
      "strategy_name": "Remove until it breaks",
      "thinker": "case-study/my-project",
      "category": "operation",            // start_point|operation|boundary|signal|evidence
      "one_liner": "When to use, 50-100 words...",
      "content": "Paraphrase + short quotes + concrete data...",
      "context_hints": {"applies_to": [...], "not_applies_to": [...]},
      "quote": "exact attributed quote (keep it short)",
      "stats": {"removed": 30, "lines": 126},
      "has_code_example": false,
      "source": {"title": "Doc title", "type": "talk", "path": "local/path.md",
                 "public_access": "https://...", "license_status": "public-talk"}
    }

Usage:
    python3 scripts/build_db.py corpus.jsonl                    # create ./strategies.db
    python3 scripts/build_db.py corpus.jsonl --out path.db      # explicit path
    python3 scripts/build_db.py corpus.jsonl --merge existing.db
"""
import argparse, json, os, sqlite3, sys

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    id              INTEGER PRIMARY KEY,
    thinker         TEXT NOT NULL,
    doc_title       TEXT NOT NULL,
    doc_type        TEXT NOT NULL,
    local_path      TEXT NOT NULL,
    public_access   TEXT,
    license_status  TEXT NOT NULL DEFAULT 'needs-check'
) STRICT;

CREATE TABLE IF NOT EXISTS strategies (
    id                INTEGER PRIMARY KEY,
    strategy_name     TEXT NOT NULL,
    thinker           TEXT NOT NULL,
    category          TEXT NOT NULL,
    one_liner         TEXT,
    content           TEXT NOT NULL,
    context_hints     TEXT,
    quote             TEXT,
    stats             TEXT,
    has_code_example  INTEGER NOT NULL,
    source_id         INTEGER REFERENCES sources(id)
) STRICT;

CREATE TABLE IF NOT EXISTS examples (
    id                  INTEGER PRIMARY KEY,
    thinker             TEXT NOT NULL,
    title               TEXT NOT NULL,
    code_snippet        TEXT NOT NULL,
    analysis            TEXT,
    linked_strategy_ids TEXT,
    source_id           INTEGER REFERENCES sources(id)
) STRICT;

CREATE INDEX IF NOT EXISTS idx_strategies_thinker ON strategies(thinker);
CREATE INDEX IF NOT EXISTS idx_strategies_category ON strategies(category);
CREATE INDEX IF NOT EXISTS idx_examples_thinker ON examples(thinker);
"""

VALID_CATEGORIES = {"start_point", "operation", "boundary", "signal", "evidence"}

def connect(path):
    conn = sqlite3.connect(path)
    for p in ("journal_mode=WAL", "synchronous=NORMAL",
              "foreign_keys=ON", "busy_timeout=5000"):
        conn.execute(f"PRAGMA {p}")
    conn.executescript(SCHEMA)
    return conn

def source_key(src):
    return (src.get("title", ""), src.get("type", "unknown"), src.get("path", ""))

def find_or_create_source(conn, thinker, src):
    if not src:
        return None
    title, dtype, path = source_key(src)
    row = conn.execute(
        "SELECT id FROM sources WHERE doc_title=? AND doc_type=? AND local_path=?",
        (title, dtype, path)).fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO sources (thinker, doc_title, doc_type, local_path, public_access, license_status) "
        "VALUES (?,?,?,?,?,?)",
        (thinker, title or "untitled", dtype, path,
         src.get("public_access"), src.get("license_status", "needs-check")))
    return cur.lastrowid

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", help="JSONL file, one strategy record per line")
    ap.add_argument("--out", default="strategies.db")
    ap.add_argument("--merge", help="merge into an existing DB instead of creating --out")
    args = ap.parse_args()

    db_path = args.merge or args.out
    if args.merge and not os.path.exists(args.merge):
        sys.exit(f"merge target not found: {args.merge}")
    if not args.merge and os.path.exists(args.out):
        sys.exit(f"refusing to overwrite {args.out}; pass --merge to extend it")

    conn = connect(db_path)
    n, skipped, no_source = 0, 0, 0
    with open(args.corpus, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"line {i}: bad JSON ({e}), skipped"); skipped += 1; continue
            if not rec.get("thinker") or not (rec.get("strategy_name") or rec.get("content")):
                print(f"line {i}: missing thinker or content, skipped"); skipped += 1; continue
            cat = rec.get("category", "operation")
            if cat not in VALID_CATEGORIES:
                print(f"line {i}: unknown category '{cat}', skipped"); skipped += 1; continue
            content = rec.get("content") or rec.get("one_liner")
            sid = find_or_create_source(conn, rec["thinker"], rec.get("source"))
            if sid is None:
                no_source += 1
            conn.execute(
                "INSERT INTO strategies (strategy_name, thinker, category, one_liner, "
                "content, context_hints, quote, stats, has_code_example, source_id) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (rec.get("strategy_name") or rec["content"][:60],
                 rec["thinker"], cat, rec.get("one_liner"), content,
                 json.dumps(rec["context_hints"], ensure_ascii=False) if rec.get("context_hints") else None,
                 rec.get("quote"),
                 json.dumps(rec["stats"]) if rec.get("stats") else None,
                 1 if rec.get("has_code_example") else 0,
                 sid))
            n += 1
    conn.commit()
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM strategies").fetchone()[0]
    conn.close()
    print(f"inserted {n}, skipped {skipped} ({no_source} without source doc) -> {db_path}")
    print(f"archive now holds {total} strategies")

if __name__ == "__main__":
    main()
