# decisions: The Decision Ledger

## Role

The distillation slot of the project protocol: where *why* lives. An ADR-lite append
account — every decision that shaped the project (architecture choices, tool adoptions,
scope rulings) lands as one compact entry, appended at the bottom, never rewritten. It is
the project-protocol counterpart of the vaultwiki notes slot, shrunk to its highest-value
subset: a fresh agent reads the ledger cold and understands the project's shape without
re-deriving it from git archaeology.

Boundary, stated once: the native tracker (issues, TODO comments, project boards) owns
*tasks*; this ledger owns *reasons*. "What shall we do next" never lives here.

## Structure

- Single file `PROJECT/decisions.md`; entries appended at the bottom (an account grows
  downward, unlike the journal which is prepend-top for freshness)
- Entry shape:

  ```
  ## D-<n> YYYY-MM-DD <one-line title>

  - Context: the situation that forced a choice
  - Decision: what was chosen (and the salient alternative)
  - Consequence: what this buys and what it costs
  ```

- Superseding a decision = a new entry referencing the old (`supersedes D-3`), never an
  edit of the old entry

## Invariants

- Append-only, never rewrite: modifying a historical entry is an error (verifiable via
  git)
- Entry numbers are monotone and never reused; the heading format `D-<n> YYYY-MM-DD` is
  the mechanical contract (attached-audit checked)
- Entries distill, they don't narrate: narration belongs to the journal, process belongs
  nowhere

## Changelog

- 0.1 2026-11-15: first release with the protocol package (spec v2) — ADR-lite ledger,
  append-at-bottom discipline, develop-bridge landing site
