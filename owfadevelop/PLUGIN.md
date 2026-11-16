# owfadevelop: The Dev Loop, Pinned to owfa

## Role

A workspace's nature is decided by its protocol: the project protocol makes a workspace
*be* a project. This member makes that project **concrete**: when the workspace develops
owfa — kernel, protocol, or any plugin/package — this member is the operating shape of
that work. It owns the target pin (which owfa component this workspace develops), the
environment declarations that survive sessions, a sandbox that never pollutes the
project's git, an install-and-validate iteration step, the project's native tests, and a
release gate. The owfa-develop command (see
[command/owfa-develop/SKILL.md](../command/owfa-develop/SKILL.md)) carries the five-step
operational flow and the three dev tracks; this member owns the territory and the
knowledge.

## Pin Semantics (what installing this member means)

- The project protocol constrains the workspace's *kind* (it is a project); the pin
  constrains the workspace's *project*.
- `PROJECT/owfadevelop/target.md` declares exactly one target:

  ```
  target: owfa/<kernel|protocol|package:<id>>
  why: <one sentence>
  ```

  With the pin in force, this workspace develops **that component and nothing else**:
  the dev loop refuses work whose declared target falls outside the pin (the refusal is
  the loop's discipline; the check member surfaces drift). Changing or removing the pin
  is a decision — it lands in `PROJECT/decisions.md` with a back-reference.
- An absent `target.md` keeps the member in its generic shape (a dev loop for whatever
  project the workspace is). The pin exists precisely for the owfa-on-owfa case: one
  workspace, one owfa component, no scope drift.

## Structure

- `PROJECT/owfadevelop/target.md` — the pin (above). Created on first pinning; changing
  it requires a decisions entry.
- `PROJECT/owfadevelop/env.md` — the environment page: host declarations the dev loop
  must honor (interpreter and package manager, PATH quirks, tool locations). Convention:
  whatever the host mandates (e.g. a uv-only Python policy) is written here once and read
  every session — the loop never re-discovers the host.
- `PROJECT/owfadevelop/releases.md` — the release ledger, append-only: one entry per
  release (`## <version> YYYY-MM-DD` + what shipped + gate evidence pointer).
- `command/owfa-develop/` — the command skill (owner: this member).

## The Three Tracks (summary; operational detail in the SKILL)

- **kernel** (`owfadev/owfa`): fix → kernel unit tests + channel smoke + docs lint → PR
  with fresh review → release commit (VERSION + package.json, tag must match) → tag →
  npm publish (CI provenance) → upgrade the dev instances (CLI / kernel / registry
  three zones).
- **protocol** (this package, `owfadev/owfa-project`): the `abi:` block is mandatory
  (R11), `proto_query.py` at the package root, registry row carries the tag + commit
  pin; upgrade every connected workspace via bridge after release.
- **package** (a domain package, e.g. `owfadev/owfa-cuhksz`): manifest/PLUGIN contract
  and the three projections green in a sandbox install; tag `<id>-vX.Y.Z`; registry pin;
  instance upgrade + validate before closing.

## Invariants

- The sandbox (`test-repo/`) is disposable by contract: it is created inside the sandbox
  step, torn down at session close, and never committed (gitignore rides adopt).
- The pin is law for the session: out-of-target work is refused until the pin changes
  through a decisions entry; the loop never "just quickly" touches a second component.
- The release gate is generic by default — a project that ships anything runs its own
  gate discovered from its own self-description; the three owfa tracks are the pinned
  specializations of that gate (see the SKILL's step ⑤).
- Conclusions distill, sessions narrate: the bridge to decisions is on-demand; a dev
  journal entry is written at session close regardless.

## Changelog

- 0.2 2026-11-16: the target pin — `PROJECT/owfadevelop/target.md` declares the one owfa
  component this workspace develops (kernel / protocol / package); out-of-target work
  refused by the loop, pin changes go through decisions; three dev tracks written into
  the SKILL's release gate; fixed the PLUGIN.md/SKILL `PROJECT/dev/` naming drift (the
  territory has always been `PROJECT/owfadevelop/`).
- 0.1 2026-11-15: first release with the protocol package (spec v2, P6 ruling: develop
  ships in the first batch — it is half the protocol's reason to exist; M4: generic
  release gate + dogfood clause).
