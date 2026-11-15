# index: The Project-Aware Index

## Role

The retrieval slot, halved on purpose. Protocol-side retrieval is `PROJECT/index.md` —
the complete list of pages under `PROJECT/` (the decisions ledger, member territories,
anything the protocol or its members wrote), plus the **anchors block**: a
hand-maintained list of the project's key entry points (README, the docs tree, CI
config, the tracker) so a fresh agent knows where the body's doors are. Code retrieval
is *not* the protocol's business — grep and the project's toolchain are native and
better; the protocol indexes pages, not source trees.

## Structure

- Single file `PROJECT/index.md`, two zones:
  - **Page list** — derived, never hand-edited; rebuilt via `pipeline.py index`; lists
    every `.md` under `PROJECT/` except reserved names (`index.md`, `journal.md`), the
    `archive/` subtree (immutable zone) and the `packages/` machine zone
  - **`## Anchors` block** — hand-maintained between `<!-- project-anchors:start -->` and
    `<!-- project-anchors:end -->` markers; rebuild preserves it verbatim
- Anchor entry shape: `- <repo-relative path or glob> — one line on why it's a door`

## Invariants

- The page list is a pure function of the PROJECT/ tree (same tree, same list, no
  historical state); hand edits are futile — the next rebuild overwrites
- The anchors block is the opposite: the script never writes inside the markers; anchor
  truth is human judgment, the check only verifies existence
- Anchor drift (a declared anchor gone from the repository) is a warning, not an error —
  the human decides whether the door moved or the project did

## Changelog

- 0.1 2026-11-15: first release with the protocol package (spec v2) — page list +
  anchors block, marker-preserved rebuild, drift check
