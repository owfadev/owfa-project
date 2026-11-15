# The Project Protocol

> Reader: anyone whose workspace *is* a project — the project owner, agents working in
> the repository, and anyone assessing whether this second protocol deserves a registry
> row. Facts live here as implemented; nothing on this page is a promise about future
> syntax. Spec: project-protocol-spec v2 (rulings P1b / P2a / P3 / P5 / P6 baked in).

## Why a Second Protocol (the double tax)

The default vaultwiki protocol organizes workspaces whose primary product is
*information* — the vault/wiki split, derived layers, distillation zones. A project
repository's primary product is the project. Forcing it into vaultwiki charges two
standing taxes:

- **Organization-principle conflict**: a project's native organization is
  project-as-spine — the project tree is the body, the task graph is the native layer,
  and there is no vault/wiki split to honor. When the workspace is the project (say,
  using owfa to develop owfa), the split is a tax paid forever.
- **Insertion cost**: a project inside vaultwiki can only live as a domain (the legacy
  `projects/` container); a repository-posture workspace is an alien there — no
  AGENTS.md, no wiki/, a sandbox doc just to explain the awkwardness.

When the workspace is the project, both taxes are structural, not incidental. Hence
this protocol: **the project tree is the body; the protocol owns exactly one territory
directory, `PROJECT/`; everything else is the project's, read-only.**

## The Slot Mapping

The four vaultwiki slots, each with this protocol's shape — and the vw extras, each
with an explicit disposition (the registry's slot-by-slot accounting):

| Slot | vaultwiki shape | project-protocol shape |
|---|---|---|
| Storage | vault/wiki split | **the project tree itself** (code/docs/data each where the project puts them; no protocol containers); protocol pages live only under `PROJECT/` |
| Retrieval | index / tags / hot | `PROJECT/index.md` (project-aware: PROJECT/ pages + declared anchors); code retrieval is toolchain-native (grep), not the protocol's |
| Distillation | notes / sessions + bridges | `PROJECT/decisions.md` (ADR-lite append ledger — the *why*) + `PROJECT/journal.md` (prepend run journal — the *what*) |
| Checking | 21-member check.py | the check member: PROJECT/ consistency, append discipline, anchor drift; the project's own tests/lint stay toolchain-native (the protocol provides the hook in the develop loop) |

Vocabulary extras and their dispositions:

| vw extra | Disposition here |
|---|---|
| map (asset registration) | **Abandoned, defended**: the project tree is native; external material lands in `PROJECT/refs/` via save — no SHA mirror layer, the project repo's asset discipline is the project's |
| save / query | **Command member**: owfa-develop carries the loop; distillation goes to decisions/journal; retrieval = index + anchors + native grep |
| tmp (draft transit) | `PROJECT/tmp/` — check only audits `stale_after`, zero retention promise |
| hot (freshness) | **Into the AGENTS injection line** as an entering discipline: journal tail window + `git log` summary (freshness semantics kept, the page dropped) |
| todo (working set) | **Abandoned, defended**: tasks are project-native (issues, TODO comments) — same boundary declaration as the vw project domain's |
| trust | **Minimal subset, git-derived**: agent commit = machine-confirmed, human commit = human-reviewed; never stored as fields (derived-never-stored); bridge pointers carry `stale_after` = pull + TTL |
| project-domain tasks (project.md tasks) | **Boundary declared**: the task source of truth is the project's native tracker; decisions record why, journal records what was done |

## Vocabulary

| Term | Meaning |
|---|---|
| **project tree** | The repository itself — code, docs, data; the protocol's body, zero protocol containers |
| **PROJECT/** | The protocol's single territory directory; every protocol write lands inside it |
| **member territory** | `PROJECT/<member>/` (e.g. `PROJECT/dev/`); the extension point for future member dimensions |
| **workspace marker** | `.owfa/WORKSPACE.yaml` — kernel-home discovery applies as-is |
| **anchors** | Hand-declared project entry points in `PROJECT/index.md`'s `## Anchors` block — where the body's doors are |
| **ledger / journal** | decisions.md (append-at-bottom, the why) vs journal.md (prepend-top, rolling window, the what) |
| **release gate** | The develop loop's step ⑤: a generic clause for every project + a dogfood clause for owfa-on-owfa |
| **red lines** | The protocol never modifies project code; outside `PROJECT/` is read-only (writes only via explicitly declared command targets); credentials never tracked |

## The Derived Machine

[pipeline.py](../pipeline.py) lives at the package root (P2a): index rebuild, journal
write + rolling archive, and verify (post-write self-attestation: kernel audit + drift
check). Same charter as the personal suite's — deterministic structure to the script,
semantics to the LLM; the script writes only inside `PROJECT/`. Window parameters live
in the script source (journal main file ≤ 100 entries, overflow archived by month to
`PROJECT/archive/<YYYY-MM>/journal.md`).

## Red Lines (once more, they carry the protocol)

1. The protocol never modifies project code.
2. Everything outside `PROJECT/` is read-only for protocol machinery — a write anywhere
   else requires an explicitly declared target in the issuing command.
3. Credentials/session files never enter the repository (the instance-git discipline).

## The Bridge to vaultwiki (and the dual-track sunset)

The vw-side `bridge-project` domain plugin is the connection point: pointer pages under
`wiki/projects-extern/<name>.md` (path + status summary + recent changes), pulling
through this protocol's retrieval surface; the symmetric `bridge-vaultwiki` on the
project side ships **uninstalled by default** (a project workspace is usually
self-sufficient). Both ride the kernel-home registry and external-workspace connector
state — the two specs' confluence.

The legacy vw **project domain** (`projects/` containers, this package's predecessor)
stays installable — dual-track by ruling P5 — with a sunset clause: one year after the
bridge stabilizes, the dual track is re-reviewed so it cannot silently become a
permanent tax.

## The ABI Surface (semantic anchor only)

The first real consumer of the protocol ABI is this package: `list` (PROJECT/ pages +
anchors), `get`, `search` (PROJECT/ full text + anchor metadata), `recent` (journal
tail + `git log` summary — a project protocol's change stream gets git for free).
**These four semantics are anchored here; the concrete command shapes wait for the ABI
standardization round — nothing in this repository implements them yet.**

## Relationship to the Kernel

`kind: protocol` + `protocol: project` + `provides: [project.org.v1]` (R1-R10 apply:
org capabilities are protocol-only, one org holder per workspace, all-or-nothing
members). The kernel owns the machinery (manifests, projections, package lifecycle);
this protocol owns everything the kernel deliberately does not interpret. The AGENTS.md
injection is additive into the project's own charter (P1b; the injection marker's
name-parameterization lands with kernel 0.4.5 — until then a project workspace still
carries the generic inject markers, mechanically identical, vocabulary to be cleaned by
that kernel release).
