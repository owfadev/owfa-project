# journal: The Run Journal

## Role

What was done to the workspace, and when. The log slot's project form: prepend-top,
never rewritten, with a type enumeration cut for project work — `develop` is its own
type so the develop member's activity is countable, and the vaultwiki types that make no
sense outside an information repository (`query`, `todo`, `profile`) are gone.

Six types: **map / save / check / plugin / develop / other** — map for workspace-shape
changes (adopt, package installs), save for distilled writes (decisions appends, docs),
check for audit outcomes, plugin for package lifecycle, develop for dev-loop sessions,
other for the residue.

## Structure

- Single file `PROJECT/journal.md`; entries prepended at the top, newest on top
- Entry format: `- YYYY-MM-DD <type>: one-sentence summary`
- Type enum: map/save/check/plugin/develop/other; instances may extend

## Invariants

- Entries are append-only and never rewritten — prepend at top, modify nothing below
- Every entry carries a date, accurate to the day, and a type from the enum
  (attached-audit checked, main file and archive alike)
- Archival moves don't change a single character of entry content

## Rolling

The main file is a rolling window, not an infinite ledger: at most **100** entries
(`JOURNAL_MAX_ENTRIES` in [pipeline.py](../pipeline.py) is the mechanical authority; this
section is the semantic description). On overflow the oldest segment is moved, grouped by
entry month, to `PROJECT/archive/<YYYY-MM>/journal.md`; the archive subtree is the
immutable zone.

## Changelog

- 0.1 2026-11-15: first release with the protocol package (spec v2, P3 ruling: the
  six-type project enumeration) — journal + rolling archive, written via `pipeline.py journal`
