# The Project Protocol ABI (`proto_query.py`)

> The ABI is this protocol's only legal access face: connectors, bridges and
> federated search never read `PROJECT/` structure directly — they call the
> four semantics and consume the JSON envelope (abi-spec v2 §1/§2). The script
> lives at the package root (the pipeline.py precedent), is self-contained
> (standard library only), and every semantic is read-only.

## Invocation

```
python <path-to>/proto_query.py list [--kind K]
python <path-to>/proto_query.py get <addr>
python <path-to>/proto_query.py search <expr>
python <path-to>/proto_query.py recent [--window Nd|Nm]
```

The script locates the workspace the same way `pipeline.py` does (package
install under `.owfa/plugins/domains/project/`, the old-host `scripts/` shim,
or a source checkout). `proto_ver` in every envelope is read live from the
`PKG.yaml` sitting beside this script — the single version source (abi-spec
§4.1).

## Addressing (one workspace = one project, so no `<project>/` segment)

The ABI draft (abi-spec v2 §6) sketched addresses as
`<project>/<task-key>` / `<project>/decisions/<key>`. Both deviations from
that sketch are protocol-sovereignty decisions grounded in this package's
own rulings, recorded here:

1. **The `<project>/` segment is omitted.** docs/protocol.md rules that one
   workspace is one project (the git root is the judgment criterion;
   multi-project = multiple workspaces). A segment that is always constant
   is pure noise, so addresses start at the entry key.
2. **The kind vocabulary is `decision` + `journal`, not `task` + `decision`.**
   This protocol explicitly abandons protocol-side task tracking (the
   project's native tracker — issues, TODO comments — owns tasks; see
   docs/protocol.md's slot table). There is no task entry to address. The two
   entry kinds that do exist:

| kind | addr | what it is |
|---|---|---|
| `decision` | `decisions/D-<n>` | one ADR entry of `PROJECT/decisions.md` (heading `## D-<n> YYYY-MM-DD <title>`); `content` = the entry section verbatim, heading included |
| `journal` | `journal/<YYYY-MM-DD>-<seq>` | one line of `PROJECT/journal.md`; `seq` is 1-based among same-date entries, **oldest first** — stable under the journal's prepend-at-top discipline (new entries get the next seq within their date; existing addrs never shift). `content` = the raw line |

Only the journal main file is enumerated; `PROJECT/archive/` (the immutable
zone) and `PROJECT/packages/` (machine zone) are not part of the ABI surface.

## The four semantics

- **list** — enumerates entries; `--kind decision|journal` filters; **unknown
  kind → empty result, exit 0** (the kernel smoke relies on this).
- **get** — returns the entry verbatim (`content`, full text, never
  truncated). Well-formed but absent addr → `not_found`; malformed addr →
  `bad_request`.
- **search** — case-insensitive substring match over the entry's title and
  body text (`<expr>` is a plain substring; no operators).
- **recent** — entries whose mtime falls in the window (default `7d`;
  `--window` takes a positive integer + `d` or `m` unit).

## `mtime` and `op` precision (best-effort declaration, abi-spec §2)

Both ledgers are single files, so an entry's `mtime` is the **containing
file's mtime** — for `decisions.md` that is the time of the *latest append of
any* entry, not of this entry. Known disturbance sources (abi-spec §2):
`git checkout`, branch switches and whole-tree copies can batch-shift file
mtimes; treat window edges accordingly.

`op` precision:

- `journal` entries → `create` (journal lines are written once, prepended,
  never rewritten — the mtime is a creation time in practice);
- `decision` entries → `create` when the run journal mentions the entry key
  (e.g. a `save` line recording "D-3 appended"), otherwise `unknown`;
- `update` is **never claimed**: the ledgers are append-only and the file
  mtime is contaminated by other entries' appends, so an honest update
  judgment is not possible from this surface.

## Envelope

Batch (list/search/recent): `{"ok": true, "semantic": ..., "count": N,
"items": [...]}`; each item carries `{addr, title, kind, mtime, protocol,
proto_ver}` (recent adds `op`; get is a single item adding `content`).
`protocol` is always `"project"`; `proto_ver` = the PKG.yaml `version`.

Errors (query-level failures, always **exit 0**):

```json
{"ok": false, "error_code": "...", "message": "..."}
```

| error_code | when |
|---|---|
| `not_found` | `get` on a well-formed addr with no entry |
| `bad_request` | missing addr/expression, malformed addr, invalid `--window` (non-positive, non-integer, or missing `d`/`m` unit) |
| `unsupported_semantic` | a semantic other than list/get/search/recent |
| `internal` | an unexpected query-time failure caught at the boundary |

Only a process crash (the interpreter dying) exits non-zero — consumers use
the exit code to distinguish "query failed" from "command is dead".

## Changelog

- 0.1.1 2026-11-15: first ABI release (abi-spec v2) — package-root
  `proto_query.py`, kind vocabulary `decision`/`journal` (task-boundary
  ruling applied), project segment dropped from addresses, best-effort `op`
  declaration above.
