#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Project-protocol post-write pipeline: index / journal / verify.

Lives at the package root (the P2a ruling: protocol machinery travels with the
package; the kernel never calls it). Instance path:
`.owfa/plugins/domains/project/pipeline.py`. An old-host copy at
`.owfa/scripts/pipeline.py` is tolerated the same way the personal suite treats
its deprecation shim.

Positioning (same as the personal suite): deterministic structural operations go
to this script; semantic judgment goes to the LLM. The script writes only inside
`PROJECT/` (the protocol's single territory — the project tree outside is
read-only, red line 2). verify is post-write self-attestation: the LLM executes,
the script certifies.

Usage:
  python .owfa/plugins/domains/project/pipeline.py index        # rebuild PROJECT/index.md (idempotent; preserves the hand-maintained Anchors block)
  python .owfa/plugins/domains/project/pipeline.py journal <type> "<one sentence>"   # capacity-archive + prepend a journal line
  python .owfa/plugins/domains/project/pipeline.py verify       # post-write self-attestation: kernel audit + index drift

Journal type enumeration: map / save / check / plugin / develop / other (the
journal member, P3 ruling).

Window parameters (the script source is the rule list; PLUGIN.md keeps the
semantic explanation):
  JOURNAL_MAX_ENTRIES = 100   # main-file rolling window; overflow archived by entry
                              # month to PROJECT/archive/<YYYY-MM>/journal.md

Index page determination (what enters the page list): all .md under PROJECT/,
excluding reserved names (index.md, journal.md), the archive/ subtree (immutable
zone) and the packages/ machine zone (installed packages — a planned machine zone; enforcement rides kernel-home).
"""
import datetime
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Location-adaptive bootstrap. Two legal hosts:
#   package install: <root>/.owfa/plugins/domains/project/pipeline.py  (canonical)
#   old host shim:   <root>/.owfa/scripts/pipeline.py  (tolerated, personal-suite precedent)
# A source checkout (this repo, PKG.yaml present) resolves ROOT as the checkout
# for self-tests; PROJECT then sits beside PKG.yaml and must be created by the caller.
_here = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(_here) == "scripts":
    ROOT = os.path.dirname(os.path.dirname(_here))            # <root>/.owfa/scripts
elif os.path.basename(os.path.dirname(_here)) == "domains":
    # <root>/.owfa/plugins/domains/project -> 4 dirnames up = <root>
    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_here))))
else:
    ROOT = _here                                              # source checkout / unknown host

PROJECT = os.path.join(ROOT, "PROJECT")
FORMAT_VERSION = "0.1"
DESC_MAX = 80

JOURNAL_MAX_ENTRIES = 100
TYPE_ORDER = ["map", "save", "check", "plugin", "develop", "other"]
INDEX_HEADER = ("# 索引\n\n> 项目感知索引：页清单只聚合、永不手编，由 index 插件经 `pipeline.py index` 重建；"
                "`## Anchors` 块为手维区（标记块保留，重建不改一字）。规则见 `.owfa/plugins/domains/project/index/`。\n")
JOURNAL_HEADER = ("# 运行日志\n\n> 置顶追加、只增不删；条目 = `- YYYY-MM-DD <类型>：一句话`，类型枚举 map/save/check/plugin/develop/other。"
                  "规则见 `.owfa/plugins/domains/project/journal/`，写走 `pipeline.py journal`。\n")
DATE_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) ")
ANCHOR_START = "<!-- project-anchors:start -->"
ANCHOR_END = "<!-- project-anchors:end -->"


def _today():
    return datetime.date.today().isoformat()


# ---------- index ----------

def _desc(rel):
    """First meaningful line of a page (frontmatter description: key wins, else first prose)."""
    try:
        text = open(os.path.join(PROJECT, rel), encoding="utf-8").read()
    except OSError:
        return ""
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if m:
        dm = re.search(r"^description:\s*(.+)$", m.group(1), re.M)
        if dm:
            t = dm.group(1).strip().strip("\"'")
            return t if len(t) <= DESC_MAX else t[: DESC_MAX - 1] + "…"
    for line in (text[m.end():] if m else text).splitlines():
        t = line.strip()
        if t and not t.startswith(("#", ">", "|", "```", "<!--", "-")):
            return t if len(t) <= DESC_MAX else t[: DESC_MAX - 1] + "…"
    return ""


def _pages():
    """Protocol pages under PROJECT/ (relative paths), sorted; reserved names, archive/ and packages/ excluded."""
    out = []
    if not os.path.isdir(PROJECT):
        return out
    for dirpath, dirs, files in os.walk(PROJECT):
        dirs[:] = sorted(d for d in dirs if d not in ("archive", "packages"))
        for fn in sorted(files):
            if not fn.endswith(".md") or fn in ("index.md", "journal.md"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), PROJECT).replace(os.sep, "/")
            out.append(rel)
    return sorted(out)


def render_index():
    lines = ["---", f"format_version: {FORMAT_VERSION}", "---", "", INDEX_HEADER, ""]
    pages = _pages()
    if pages:
        lines += ["## Pages", ""]
        lines += [f"- `{p}` —— {_desc(p)}" for p in pages]
        lines += [""]
    else:
        lines += ["## Pages", "", "（暂无页面）", ""]
    lines += ["## Anchors", "", ANCHOR_START, ANCHOR_END, ""]
    return "\n".join(lines).rstrip() + "\n", pages


def _anchors_block(text):
    """Extract the hand-maintained anchors block (verbatim); None when absent."""
    m = re.search(re.escape(ANCHOR_START) + r"\n(.*?)" + re.escape(ANCHOR_END), text, re.S)
    return m.group(1) if m else None


def do_index(check_only=False):
    path = os.path.join(PROJECT, "index.md")
    content, _pages_list = render_index()
    cur = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if cur is not None and _anchors_block(cur) is not None:
        # preserve the hand-maintained anchors block verbatim
        content = content.replace(ANCHOR_START + "\n" + ANCHOR_END,
                                  ANCHOR_START + "\n" + _anchors_block(cur) + ANCHOR_END)
    if cur == content:
        if not check_only:
            print("[index] unchanged")
        return []
    if check_only:
        return ["index.md"]
    os.makedirs(PROJECT, exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(content)
    if not check_only:
        print(f"[index] rebuilt PROJECT/index.md ({len(_pages_list)} pages)")
    return ["index.md"]


# ---------- journal rolling ----------

def do_journal(kind, text):
    if kind not in TYPE_ORDER:
        print(f"[journal] type must be one of {'/'.join(TYPE_ORDER)} (got {kind})")
        return False
    path = os.path.join(PROJECT, "journal.md")
    entries = []
    if os.path.exists(path):
        for raw in open(path, encoding="utf-8").read().splitlines():
            if DATE_RE.match(raw):
                entries.append(raw)
    entries.insert(0, f"- {_today()} {kind}：{text}")  # prepend; existing entries are never rewritten
    overflow = entries[JOURNAL_MAX_ENTRIES:]
    if overflow:  # window overflow: the oldest stretch is grouped by entry month into archive/<month>/journal.md (position move only)
        for month in sorted({e[2:9] for e in overflow}):
            moved = [e for e in overflow if e[2:9] == month]
            adir = os.path.join(PROJECT, "archive", month)
            os.makedirs(adir, exist_ok=True)
            apath = os.path.join(adir, "journal.md")
            old = open(apath, encoding="utf-8").read() if os.path.exists(apath) else f"# 归档 {month}\n"
            open(apath, "w", encoding="utf-8", newline="\n").write(old.rstrip() + "\n" + "\n".join(moved) + "\n")
            print(f"[journal] archived {len(moved)} entries to PROJECT/archive/{month}/journal.md")
    os.makedirs(PROJECT, exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(
        JOURNAL_HEADER + "\n" + "\n".join(entries[:JOURNAL_MAX_ENTRIES]) + "\n")
    print(f"[journal] written ({kind}), main file {min(len(entries), JOURNAL_MAX_ENTRIES)} entries")
    return True


# ---------- post-write self-attestation ----------

def do_verify():
    ok = True
    kernel = os.path.join(ROOT, ".owfa", "scripts", "owfa_kernel.py")
    if os.path.isfile(kernel):
        r = subprocess.run([sys.executable, kernel, "audit"])
        if r.returncode != 0:
            ok = False
            print("[verify] plugin audit has errors")
    else:
        print("[verify] kernel not found at .owfa/scripts/owfa_kernel.py — audit skipped")
    drift = do_index(check_only=True)
    if drift:
        ok = False
        print("[verify] derived drift: " + ", ".join("PROJECT/" + d for d in drift) + " (run pipeline.py index to fix)")
    else:
        print("[verify] derived area consistent")
    print("[verify] " + ("passed" if ok else "failed"))
    return 0 if ok else 1


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "index":
        do_index()
        return 0
    if cmd == "journal":
        if len(sys.argv) < 4:
            print(__doc__)
            return 2
        return 0 if do_journal(sys.argv[2], " ".join(sys.argv[3:])) else 1
    if cmd == "verify":
        return do_verify()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
