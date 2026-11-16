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
| **member territory** | `PROJECT/<member>/` (e.g. `PROJECT/owfadevelop/`); the extension point for future member dimensions |
| **workspace marker** | `.owfa/WORKSPACE.yaml` — kernel-home discovery applies as-is |
| **anchors** | Hand-declared project entry points in `PROJECT/index.md`'s `## Anchors` block — where the body's doors are |
| **ledger / journal** | decisions.md (append-at-bottom, the why) vs journal.md (prepend-top, rolling window, the what) |
| **target pin** | `PROJECT/owfadevelop/target.md` — declares the one owfa component this workspace develops (`owfa/<kernel\|protocol\|package:<id>>`); with the pin in force the dev loop refuses out-of-target work, and changing the pin goes through decisions (see the owfadevelop member) |
| **release gate** | The develop loop's step ⑤: a generic clause for every project + a dogfood clause for owfa-on-owfa |
| **red lines** | The protocol never modifies project code; outside `PROJECT/` is read-only (writes only via explicitly declared command targets); credentials never tracked |

## The Derived Machine

[pipeline.py](../pipeline.py) lives at the package root (P2a): index rebuild, journal
write + rolling archive, and verify (post-write self-attestation: kernel audit + drift
check). Same charter as the personal suite's — deterministic structure to the script,
semantics to the LLM; the script writes only inside `PROJECT/`. Window parameters live
in the script source (journal main file ≤ 100 entries, overflow archived by month to
`PROJECT/archive/<YYYY-MM>/journal.md`).

## Member Roster

The six members (versions verbatim from each PLUGIN.yaml; the `project` package, `kind: protocol` / `protocol: project` — version and compat floor see [PKG.yaml](../PKG.yaml)):

| id | one line | version |
|---|---|---|
| project | Territory `PROJECT/` (the protocol's only one — the project tree is the body): `PROJECT/<member>/`; red lines — never modify project code, outside PROJECT/ read-only, no credentials | 0.1 |
| decisions | Decisions ledger `PROJECT/decisions.md`: ADR-lite entries, append at bottom, never rewrite; the native tracker owns tasks, this owns reasons | 0.1 |
| journal | Journal `PROJECT/journal.md`: prepend, never rewrite; entry via `pipeline.py journal`; >100 auto-archived to `PROJECT/archive/<m>/` | 0.1 |
| index | Index `PROJECT/index.md`: derived page list + preserved hand `## Anchors` block; rebuild via `pipeline.py index`; code search is toolchain-native | 0.1 |
| check | Protocol check `scripts/check.py`: journal/decisions/index/anchor consistency; project tests/lint stay toolchain-native; run via `kernel audit` / `pipeline.py verify` | 0.1 |
| owfadevelop | Dev territory `PROJECT/owfadevelop/` (env page + release ledger); dev loop → owfa-develop command (①env ②sandbox ③iterate ④test ⑤release gate) | 0.1 |

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

The ABI surface is shipped as of 0.1.1: the package-root `proto_query.py`
implements the four semantics — `list` / `get` / `search` / `recent` — over
the decision ledger and the run journal, with the JSON envelope, error codes
and addressing rules specified in [docs/abi.md](abi.md) (abi-spec v2). The
entry kinds are `decision` and `journal` (the task-boundary ruling applied:
tasks are the native tracker's, so no task kind exists); the change stream
consumers get is the ledgers' mtime (best-effort `op`, see docs/abi.md); git history stays
toolchain-native and is not part of the ABI.

## Relationship to the Kernel

`kind: protocol` + `protocol: project` + `provides: [project.org.v1]` (R1-R10 apply:
org capabilities are protocol-only, one org holder per workspace, all-or-nothing
members). The kernel owns the machinery (manifests, projections, package lifecycle);
this protocol owns everything the kernel deliberately does not interpret. The AGENTS.md
injection is additive into the project's own charter (P1b). On the marker vocabulary:
the kernel made the injection-region marker id a parameterizable constant
(`inject_markers()`, C3, kernel-home step 1 — shipped v0.4.4/0.4.5), but no call site
drives it with a per-protocol name: through the current release (kernel 0.4.8) all
projections still emit the generic `wiki-inject` markers, so a project workspace
carries generic inject markers, mechanically identical to the vaultwiki ones — the
vocabulary cleanup remains unshipped kernel work.

## Scope rulings（owner 定稿）

**定位**：project 协议 = agent 在人类监督下进行开发的通用框架——为合法化开发工作而设：每步有时间账（journal）、每个决定有理由账（decisions）、每次收尾有自证（check/verify），人类监督有完整审计面。

**一个工作区一个项目，项目 = 一个 git 根**（判据：独立目标 + 独立生命周期）。多项目 = 多开工作区（注册表 + 联邦检索提供统一视图）。monorepo 是合法形态但算一个项目；其内部结构是项目自己的领地，协议零干预。不考虑子项目——长大要独立的，直接分家为新工作区。


