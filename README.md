# simplicity-driven-design-skills

Review software designs through five simplicity lenses (Pike / Hickey /
Martens / antirez / Armstrong / Victor / Ousterhout / esr), backed by a
distilled strategy archive — reduce software complexity by every possible
means, starting from first principles.

This repository ships the **methodology and tooling** (public part):

```
SKILL.md                    ← the skill: five lenses + review workflow
references/sources.md       ← source registry: where every reference lives + license status
scripts/build_db.py         ← build / merge your own distilled strategies into a SQLite archive
LICENSE                     ← MIT for the original content here
```

The **distilled strategy database** (198 strategies + 25 code examples with
provenance, agent-ready SQLite) is distributed separately in a private
repository, together with the raw corpus it was distilled from. Only the
distilled layer is publishable: raw source texts — two commercial books and
talk transcripts among them — must not be redistributed.

## Bring your own corpus

You can rebuild an equivalent archive from sources you legally hold. There
are **no format requirements** for source material:

- paste raw text as-is into a `.txt` / `.md` file — messy is fine
- a plain `urls.txt` with one URL per line works
- any file containing the material is acceptable input

Distill (manually or with your own agent) into JSONL records — the field
contract is documented in the `scripts/build_db.py` docstring — then merge:

```bash
python3 scripts/build_db.py my_corpus.jsonl --out strategies.db
python3 scripts/build_db.py more.jsonl --merge strategies.db
```

## The reference-archive principle (why no RAG)

The archive is a **reference archive, not a knowledge base**: exact short
quotes, code line counts, concrete numbers, provenance — facts the model
cannot reason out on its own. Reasoning stays with the model. The prompt
gives direction; the DB holds evidence; retrieval is a conscious decision,
not a similarity search. See SKILL.md for the full argument and the
five-lens workflow.

## Copyright posture

Original content in this repository (methodology, scripts, structure) is
MIT-licensed. Third-party material appears only as paraphrase + short
attributed quotes; see `references/sources.md` for the per-source license
registry, and consult originals through legitimate access. Never
redistribute raw source texts.
