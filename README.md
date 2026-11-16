# owfa-project

**OWFA project protocol package** — the second `kind: protocol` package (`protocol:
project`, `provides: project.org.v1`): for workspaces whose primary product *is* the
project — the project tree is the body, and the protocol owns exactly one territory
directory, `PROJECT/`. Five members (project, decisions, journal, index, check)
give the workspace a self-sufficient baseline: an ADR-lite decision ledger, a rolling
run journal, a project-aware index with declared anchors, and a scoped protocol check.
Developing owfa itself is NOT bundled: install the optional
[`owfadevelop`](https://github.com/owfadev/owfa-owfadevelop) package (needs this
protocol) — it carries the `owfa-develop` dev-loop command, the three owfa dev tracks
(kernel / protocol / package), and the **target pin**: a workspace declaring
`target: owfa/<component>` in `PROJECT/owfadevelop/target.md` is pinned to developing
exactly that component, out-of-target work refused by the loop. Replaces this repository's former content (the legacy
vw `projects/`-container domain package, which remains installable dual-track with a
one-year sunset review after the bridge stabilizes).

- Protocol charter: [docs/protocol.md](docs/protocol.md) — the double-tax motivation,
  slot mapping, vocabulary, red lines, bridge & ABI anchors
- Members: [PKG.yaml](PKG.yaml) for the roster; each `<member>/PLUGIN.md` for the
  charter
- Machinery: [pipeline.py](pipeline.py) at the package root (index / journal / verify;
  the kernel never calls it)
- Requires framework `>= 0.4.5` (protocol-kind discipline R1-R10; AGENTS-injection
  marker parameterization)

The kernel and plugin mechanics live in the framework ([owfa](https://github.com/owfadev/owfa)).
