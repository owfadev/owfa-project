# project: The Protocol Root

## Role

The holder's charter, shrunk to one page: under the **project protocol** the project
tree itself is the body — code, docs and data each live where the project natively puts
them, and the protocol owns exactly one territory directory, `PROJECT/`. There is no
vault/wiki split here; that organization serves workspaces whose primary product is
information, while this protocol serves workspaces whose primary product is the project
(see [docs/protocol.md](../docs/protocol.md) for the double-tax argument).

What this member owns:

- **Territory syntax** — every protocol write lands under `PROJECT/` or `PROJECT/<member>/`
  (member directories follow `PROJECT/<member>/`; the syntax is the extension point for
  future non-project member dimensions).
- **Red lines** — (1) the protocol never modifies project code; (2) everything outside
  `PROJECT/` is read-only for protocol machinery — a write anywhere else requires an
  explicitly declared target in the issuing command; (3) credentials/session files never
  enter the repository (the instance-git discipline, inherited).
- **The workspace marker** — `.owfa/WORKSPACE.yaml` marks the project root as an OWFA
  workspace (kernel-home discovery algorithm applies as-is); its gitignore template rides
  adopt.

## Structure

```
<project-root>/            # the project repository itself (its own git)
├── (anything the project wants — zero protocol intervention)
├── .owfa/WORKSPACE.yaml   # workspace marker
├── PROJECT/               # the protocol territory (the only one)
│   ├── index.md           # derived: project-aware index (index member)
│   ├── decisions.md       # append-only: decision ledger (decisions member)
│   ├── journal.md         # prepend-append: run journal (journal member)
│   ├── packages/          # machine zone: packages installed into this workspace; deleted on uninstall, not protected by retains
│   └── <member>/          # member territories (PROJECT/owfadevelop/ for owfadevelop, …)
└── AGENTS.md              # project agent charter (additive injection)
```

## Invariants

- One territory, one syntax: `PROJECT/` is the protocol's complete write surface; member
  subdirectories are `PROJECT/<member>/`
- The project tree outside `PROJECT/` is read-only territory for the protocol — owning
  nothing outside is what keeps the protocol removable without a scar
- Trust is derived from git provenance, never stored as fields: agent commits read as
  machine-confirmed, human commits as human-reviewed (the minimal trust subset)
- The task source of truth is the project's native tracker (issues, TODO comments) —
  decisions record *why*, journal records *what was done*, neither is a task list

## Changelog

- 0.1 2026-11-15: first release with the protocol package (spec v2) — territory syntax,
  red lines, workspace marker, git-derived trust subset, task-boundary declaration
