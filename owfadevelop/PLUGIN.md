# owfadevelop: The Dev Loop

## Role

The first protocol member that exists because of the protocol: when the workspace *is* a
project under development — the strongest case being owfa developing owfa — the agent's
dev loop needs shape: environment declarations that survive sessions, a sandbox that
never pollutes the project's git, an install-and-validate iteration step, the project's
native tests, and a release gate. The owfa-develop command (see
[command/owfa-develop/SKILL.md](../command/owfa-develop/SKILL.md)) carries the five-step
operational flow; this member owns the territory and the knowledge.

## Structure

- `PROJECT/dev/env.md` — the environment page: host declarations the dev loop must honor
  (interpreter and package manager, PATH quirks, tool locations). Convention: whatever
  the host mandates (e.g. a uv-only Python policy) is written here once and read every
  session — the loop never re-discovers the host.
- `PROJECT/dev/releases.md` — the release ledger, append-only: one entry per release
  (`## <version> YYYY-MM-DD` + what shipped + gate evidence pointer).
- `command/owfa-develop/` — the command skill (owner: this member).

## Invariants

- The sandbox (`test-repo/`) is disposable by contract: it is created inside the
  sandbox step, torn down at session close, and never committed (gitignore rides adopt)
- The release gate is generic by default — a project that ships anything runs its own
  gate discovered from its own self-description; the dogfood clause (owfa developing
  owfa) stacks the framework-specific clauses on top (see the SKILL's step ⑤)
- Conclusions distill, sessions narrate: the bridge to decisions is on-demand; a dev
  journal entry is written at session close regardless

## Changelog

- 0.1 2026-11-15: first release with the protocol package (spec v2, P6 ruling: develop
  ships in the first batch — it is half the protocol's reason to exist; M4: generic
  release gate + dogfood clause)
