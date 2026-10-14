# Sources & License Status

The archive distills from publicly delivered talks, essays, blog posts, and
two commercial books. **Raw source texts are NOT distributed in this repo.**
This file records where each source lives and its redistribution status, so
every distilled claim stays traceable and users can consult originals
through legitimate access.

`strategies.db` `sources.license_status` values:

| Status | Meaning |
|--------|---------|
| `public-talk` | Delivered publicly (conference keynote / public lecture). Quoted in short form with attribution — standard fair-use shape. |
| `open-blog` | Author's own blog, free to read. Short quotes with attribution + link. |
| `free-with-license` | Freely available with an explicit open license — **per-document check required before any verbatim redistribution**. |
| `commercial-book` | Copyrighted book. **No raw text distributed, ever.** Only tiny quoted fragments with attribution, if any. |
| `needs-check` | Status not yet verified — treat as copyrighted by default. |

## Source Registry

> Generated from the v1 archive. `local_path` is provenance-only — the file
> is not shipped. 126 of 198 strategies lack a doc-level citation (v1 export
> gap); their per-thinker *candidate* sources are listed under each thinker.

## Talk Sources (public-talk)

- **Rob Pike** — "Simplicity is Complicated" (GopherCon 2015, dotGo 2014 talks), Go language design essays (blog.golang.org)
  - covers: Go's feature-selection process, basis-set orthogonality, dependency hygiene, "clear is better than clever"
- **Rich Hickey** — "Simple Made Easy" (StrangeLoop 2011), "The Value of Values" (2012), "Hammock Driven Development" (Clojure Conj 2010)
  - covers: simple vs easy, complecting, value-vs-state, place-oriented programming critique
- **Joe Armstrong** — "The Mess We're In" (StrangeLoop 2014)
  - covers: state explosion, why systems get messy, identity and state
- **Greg Young** — "The Art of Destroying Software" (2013), event-sourcing essays (leanpub/blog)
  - covers: immutability, rebuild-from-events, deleting code as the primary simplification
- **Bret Victor** — "Inventing on Principle" (CUSEC 2012)
  - covers: immediate feedback loops, tools that reveal possibility, first-principles invention
- **Michel Martens** — So Simple talks / good-practice essays (soveran.com)
  - covers: minimal library design, Ohm/Redic/Nest/Stal architecture, Lua-as-transaction

## Writing Sources (open-blog)

- **antirez** — blog posts at antirez.com (12 essays distilled): protocol design, fork() over WAL, hash-over-ORM, write fanout, security boundaries, "programs must be simple for their author"
- **esr (Eric S. Raymond)** — catb.org essays incl. The Cathedral and the Bazaar, TAoUP chapters
  - ⚠️ catb.org texts carry explicit open licenses (TAoUP: verbatim-copying license; newer essays: CC). **Per-document check required before verbatim redistribution; short quotes with attribution are safe.**

## Book Sources (commercial-book — raw text never shipped)

- **Ousterhout** — *A Philosophy of Software Design* (Yaknyam Press, 2018). Distilled locally into a book_distillate (2–5% compression) before strategy extraction; only paraphrase + attributed one-line quotes are published.
- **Deutsch** — *The Beginning of Infinity* (Allen Lane, 2011). Archived at C-level (not in the distillation pipeline); paraphrase only.

## Rebuild Note

This DB is a **distilled export**, not the full v1 archive. The full archive
(documents with full text, FTS chunks, book distillates) is deliberately
private. Anyone can rebuild an equivalent DB from their own legally-obtained
copies: see `scripts/build_db.py` (bring-your-own-corpus).
