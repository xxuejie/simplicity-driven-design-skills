---
name: simplicity-lens
description: "Review and critique software designs through five distilled simplicity lenses (Pike/Hickey/Martens/antirez/Armstrong/Victor/Ousterhout/esr), backed by a 198-strategy SQLite reference archive with provenance. Prompt for direction, DB for evidence — no RAG."
version: 1.1.0
author: rafael faint
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design-review, simplicity, architecture, sqlite, distillation]
---

# Simplicity Lens — Design Review Through Distilled Wisdom

## Trigger Conditions

Use this skill when the user wants to:
- Validate or critique a software design / architecture
- Review a code design with a simplicity-first lens
- Discuss design decisions against the distilled strategies of Rob Pike, Rich Hickey, Michel Martens, antirez, Joe Armstrong, Bret Victor, Ousterhout, or esr
- Pressure-test scope: what to cut, what to defer, what never to build

## Core Principle (one, not negotiable)

> **Reduce software complexity by every possible means, starting from first principles.**

Everything else is a strategy for executing this in different contexts. The
thinkers do not always agree — that is a feature. Contradictions are recorded
as *different strategies for different contexts* (`context_hints`), never
harmonized. The situation picks.

## The Five Lenses

| Lens | What to ask |
|------|-------------|
| **Starting point** | What is the first cut? What question do you ask first? |
| **Operation** | What do you actually *do*? Remove? Merge? Replace? |
| **Boundary** | What don't you touch? When do you accept complexity? |
| **Signal** | What smells wrong? What patterns indicate complexity creeping in? |
| **Evidence** | Is there a concrete code example demonstrating this? |

These map 1:1 to the `category` column in the DB — the lenses are not
metaphor, they are the query axes.

## Extra Lens: AI-Era Division of Labor

When reviewing a design built with AI assistance, split complexity into two kinds:

| Kind | Owner | Test |
|------|-------|------|
| **Design complexity** | Human | Needs judgment; unknowns and trade-offs; hard to reverse |
| **Implementation complexity** | AI | Deterministic, verifiable, "just follow the logic" |

Rule of thumb: *design complexity the human carries; implementation
complexity the AI fills.* The differentiator: is the task checkable
(tests pass/fail) or does it need judgment?

## The Reference-Archive Principle (why no RAG)

The DB is a **reference archive, not a knowledge base**. It stores facts the
model cannot reason out: exact short quotes, code line counts, concrete
numbers, provenance. It does not store reasoning or merged consensus.

- Prompt gives direction; DB holds evidence. Never query to decide *what*
  to think — query to *confirm* or *illustrate*.
- Vector similarity is the wrong tool: design review needs conscious
  judgment about what to retrieve. SQL is deterministic and verifiable.
- Each strategy row carries `one_liner` (scan-level summary — read this
  first to decide relevance), `content` (paraphrase + short quotes + data),
  `context_hints` (applies_to / not_applies_to), `stats` (numbers).

## Workflow

### Step 1: Reason through the five lenses YOURSELF first

Analyze the user's design without the DB. Don't let retrieval substitute
for judgment.

### Step 2: Query the DB for evidence

```python
import sqlite3, os
db_path = os.path.join(SKILL_DIR, "references", "strategies.db")
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON")   # not default — set per connection
conn.execute("PRAGMA busy_timeout = 5000") # not default

# sweep a lens
conn.execute("""SELECT strategy_name, thinker, one_liner, content
                FROM strategies WHERE category = 'operation'""")

# one thinker's view
conn.execute("SELECT strategy_name, one_liner, context_hints FROM strategies WHERE thinker = 'rich_hickey'")

# keyword search (SQL LIKE; scale is 200 rows — FTS5 is unnecessary here)
conn.execute("SELECT strategy_name, one_liner FROM strategies WHERE content LIKE '%abstraction%'")

# code-level evidence
conn.execute("SELECT title, code_snippet, analysis FROM examples WHERE thinker = 'antirez'")

# provenance: every claim must be traceable
conn.execute("""SELECT s.strategy_name, s.quote, src.doc_title, src.public_access
                FROM strategies s LEFT JOIN sources src ON s.source_id = src.id
                WHERE s.thinker = 'rob_pike'""")
```

Three query paths — combine as needed:
- **By category** (systematic sweep of one lens)
- **By thinker** (one person's position, including their context_hints)
- **By keyword** (concept-centered)

### Query discipline (output budget)

The archive is 198 rows / ~195 KB of text. A bare `SELECT *` emits
~195K chars, which overflows typical agent tool-output caps (~16K) and
is silently truncated — leaving a biased ~16-row sample. Sized queries
instead:

- **Table of contents first** (one call, fits any budget):
  `SELECT id, strategy_name, thinker, category FROM strategies`
  (~10K chars for all 198 rows)
- **One lens sweep**: 50 rows x (name, one_liner) ~ 20K — fine, but
  defer `content`: fetch it for the 3-5 rows you actually need via
  `WHERE id IN (...)`
- **Never** `SELECT content` (or `SELECT *`) without a WHERE clause.
- If an output was truncated anyway, narrow columns or add LIMIT and
  re-query — never reason from a truncated sample (you cannot tell
  which rows were cut).

This is a reference, not a knowledge base: no RAG, no bulk dump —
targeted reads driven by your own five-lens analysis.

### Step 3: Produce structured output

1. **Starting point** — is the first cut right?
2. **Operations** — what can be removed/merged/replaced?
3. **Boundaries** — what complexity is necessary?
4. **Signals** — what smells wrong?
5. **Evidence table** — decision → supporting thinker → DB evidence
6. **Verdict + specific recommendations** (prefer "remove X, defer Y" over "add Y")

When citing a thinker, say which lens you're using, and keep their exact framing.

### Step 4: Second pass on the written artifact

After producing a design document, run the five lenses **again over the
document itself**, not the discussion. Writing exposes a different bug class:
things "agreed" verbally that degrade when written down (real catch: a
fingerprint key `(state_rank, position_rank, position)` survived discussion
but writing the DDL exposed that state ranks collide across states).

If pass 2 finds nothing, say so and move on — do not invent findings.

### Step 5: Track decisions

For ongoing design work, write `DESIGN-DECISIONS.md`: decided items with
rationale, explicitly-not-doing items, pending items.

## Pitfalls

- **Don't use the DB to think.** Reasoning is yours; the DB is evidence only.
- **Don't over-engineer the review.** If the design is sound, say so.
- **Contradictions between thinkers are not errors.** Present them as
  different strategies for different contexts; let the situation pick.
- **Check `context_hints` before applying a strategy.** "Delete until it
  breaks" applies to prototype scope, not to the auth layer.
- **Honor provenance gaps.** Strategies with `source_id IS NULL` are real
  content but lack a doc-level citation (known v1 export gap, 126 rows —
  per-thinker candidate sources in `references/sources.md`). Cite thinker,
  not document, for these.
- **This DB contains only the distilled layer.** Raw texts are deliberately
  not shipped (copyright). To trace a paraphrase to its full original,
  follow `sources.public_access` and read the source yourself. To add your
  own corpus, see `scripts/build_db.py` (bring-your-own-corpus).

## Extending: Bring Your Own Corpus

The archive format is deliberately simple. Add your own thinkers:

1. Distill your sources into strategy rows (see `references/sources.md`
   for the field contract)
2. `python3 scripts/build_db.py my_corpus.jsonl --out references/strategies.db --merge`
3. Strategies carry `thinker` as a free label — case studies and your own
   post-mortems are first-class entries

## Verification

After producing an assessment:
1. Every cited claim traces to an actual DB row (provenance)
2. Contradictions presented as context differences, not errors
3. Recommendations respect "don't predict future needs" (Martens)
4. The one core principle is never violated by the recommendation
