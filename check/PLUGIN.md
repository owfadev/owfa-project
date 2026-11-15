# check: The Protocol Check

## Role

The checking slot, scoped to what the protocol owns: the health of `PROJECT/` itself —
not the project's tests, lint or build (those are toolchain-native; the protocol provides
a hook in the develop loop, never competing rules). One attached-audit script
(`scripts/check.py`, the kernel contract: `check(ctx)` returning an issue list) covers
the mechanical items; semantic items stay in the check command.

## Structure

Rule set (mechanical, in `scripts/check.py`):

| # | Rule | Level |
|---|---|---|
| 1 | Journal entries dated and on-enum (`map/save/check/plugin/develop/other`), main file and `archive/` alike | error |
| 2 | Journal capacity ≤ 100 entries (overflow → archive via `pipeline.py journal`) | warning |
| 3 | Decisions entries carry `D-<n> YYYY-MM-DD` headings, numbers monotone and unique | error |
| 4 | Index page list equals the actual PROJECT/ page set (drift → `pipeline.py index`) | warning |
| 5 | Every declared anchor exists in the repository (anchor drift) | warning |
| 6 | `.owfa/WORKSPACE.yaml` present (workspace marker) | info |

Semantic items (not scriptable): writes outside `PROJECT/` without a declared target →
error; historical ledger entries modified → error (both verifiable via git, per the
instance-git discipline).

## Invariants

- The audit is read-only with zero side effects: repair actions belong to
  commands/humans, attached audits only report
- `ctx.pages` (the vaultwiki page scan) is empty in a project workspace by design — this
  script walks `PROJECT/` itself from `ctx.root`

## Changelog

- 0.1 2026-11-15: first release with the protocol package (spec v2) — six mechanical
  rules + two semantic items; own-tree walk, no wikilib dependency
