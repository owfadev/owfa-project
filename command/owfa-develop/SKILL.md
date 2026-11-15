---
name: owfa-develop
owner: owfadevelop
consumes: [owfadevelop, project]
description: "Run the project dev loop: environment / sandbox / iterate / test / release gate — a five-step flow for developing a project whose workspace runs the project protocol. Triggers on: develop, dev loop, 开发迭代, iterate on this project, cut a release."
---

<!-- cmd-inject:start -->

<!-- cmd-inject:end -->

# owfa-develop: The Five-Step Dev Loop

For project-protocol workspaces (the project tree is the body; protocol machinery lives
under `PROJECT/`). Operational detail and territory contracts: read
`.owfa/plugins/domains/project/owfadevelop/PLUGIN.md` first and stay aligned with it.

## Scope

Write: PROJECT/ (dev territory, decisions, journal — per each member's contract),
test-repo/ (disposable sandbox)
Read: the project tree (code, docs, native self-description), PROJECT/owfadevelop/env.md,
`.owfa/scripts/owfa_kernel.py`

## Steps

1. **Environment** — read `PROJECT/owfadevelop/env.md` (create it on first use from the host's
   declarations: interpreter, package manager, PATH quirks, tool locations). Honor it
   for the whole session; the host's mandates (e.g. a uv-only Python policy) are law,
   never re-discovered ad hoc.
2. **Sandbox lifecycle** — `test-repo/` is the disposable arena: create it by copying the
   framework substrate (`.owfa` + `.agents`) and the project as the AGENTS shell, mirror
   the project repo in, and tear it down at session close. The sandbox's git is never
   the project's git; nothing in it is committed to the project.
3. **Iterate** — install the in-progress package/working tree into the sandbox with
   `kernel install <pkg> --path <source> --yes`, then `kernel validate` (scoped where the
   kernel supports it) after each meaningful change; fix before stacking.
4. **Test** — run the project's native tests, discovered from its self-description
   (README / docs / config: `python -m unittest discover`, `node test/smoke.js`, `make
   test`, whatever the project declares). The protocol adds no test rules; it requires
   the native suite green before any release action.
5. **Release gate** — two clauses:
   - **Generic clause (every project)**: tests green (step ④) · version and changelog
     updated · release ledger entry appended to `PROJECT/owfadevelop/releases.md` · journal entry
     written (`develop` type) · the project's declared packaging/distribution steps run.
   - **Dogfood clause (owfa developing owfa)**: on top of the generic clause —
     `verify-release` / blessed-suite sync (`sync-blessed` / five-carrier parity) /
     pre-tag verification discipline, per the framework repo's releasing doc
     (`.owfa/docs/releasing.md`); the framework converting itself to this protocol is
     the loop's strongest acceptance.

## Close

Append the release/session record (decisions entry when a durable conclusion emerged,
with a back-reference to the journal line; always a journal line via
`python .owfa/plugins/domains/project/pipeline.py journal develop "<one sentence>"`),
then `pipeline.py verify`; commit per the project's own git discipline.

## Prohibitions

- Never modify project code outside a declared task target (red line 1); never write
  outside PROJECT/ or test-repo/ without an explicit declared target (red line 2)
- Never commit sandbox state; never let credentials enter any tree

## Language

Follow the session language unless `PROJECT/owfadevelop/env.md` declares otherwise.
