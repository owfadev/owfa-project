#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Project-protocol ABI query surface (abi-spec v2, package-root script).

The ABI is the protocol's only legal access face for connectors / bridges /
federated search: callers see the four semantics and the JSON envelope, never
the protocol's internal structure. Same charter as pipeline.py (the P2a
ruling): this script travels with the package, is self-contained (standard
library only), and never writes — every semantic is read-only.

Usage (abi-spec v2 §2/§3; `proto-query` == this script):
  proto_query.py list [--kind K]          # K in {decision, journal}; unknown K -> empty, exit 0
  proto_query.py get <addr>               # addr: decisions/D-<n> | journal/<date>-<seq>
  proto_query.py search <expr>            # case-insensitive substring over entry text
  proto_query.py recent [--window Nd|Nm]  # default 7d; mtime window, op best-effort

Envelope (single items carry these fields + protocol + proto_ver):
  list/search/recent -> {"ok": true, "semantic": ..., "count": N, "items": [...]}
  item fields        -> {addr, title, kind, mtime} (+content for get, +op for recent)
Errors               -> {"ok": false, "error_code": ..., "message": ...}, exit 0
error_code in {not_found, bad_request, unsupported_semantic, internal};
query-level failures exit 0, process crashes exit != 0.

Addressing (kind vocabulary is protocol sovereignty — abi-spec §2; the spec's
draft task/decision pair predates this package's task-boundary ruling, see
docs/abi.md): one workspace = one project (docs/protocol.md scope ruling), so
the <project>/ address segment is omitted. Addressable entries:
  decisions/D-<n>         one ADR entry of PROJECT/decisions.md (heading `## D-<n> ...`)
  journal/<date>-<seq>    one run-journal line of PROJECT/journal.md (seq: 1-based
                          among same-date entries, oldest first — stable under prepend)
"""

import datetime
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Location-adaptive bootstrap — same hosts as pipeline.py:
#   package install: <root>/.owfa/plugins/domains/project/proto_query.py
#   old host shim:   <root>/.owfa/scripts/proto_query.py
#   source checkout: this repo (PKG.yaml beside the script); PROJECT/ beside it
_here = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(_here) == "scripts":
    ROOT = os.path.dirname(os.path.dirname(_here))
elif os.path.basename(os.path.dirname(_here)) == "domains":
    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_here))))
else:
    ROOT = _here

PROJECT = os.path.join(ROOT, "PROJECT")
PROTOCOL_ID = "project"
KINDS = ("decision", "journal")
DECISION_RE = re.compile(r"^## (D-\d+) (\d{4}-\d{2}-\d{2}) (.+?)\s*$", re.M)
JOURNAL_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) (map|save|check|plugin|develop|other)[：:]\s*(.+?)\s*$")
WINDOW_RE = re.compile(r"^(\d+)([dm])$")


# ---------- version (single source: PKG.yaml beside this script) ----------

def proto_ver():
    pkg = os.path.join(_here, "PKG.yaml")
    try:
        text = open(pkg, encoding="utf-8").read()
    except OSError:
        return "unknown"
    m = re.search(r"^version:\s*(\S+)", text, re.M)
    return m.group(1) if m else "unknown"


# ---------- entry model ----------

def _mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def _fmt(mts):
    return datetime.datetime.fromtimestamp(mts).isoformat(timespec="seconds")


def _decisions():
    """Addressable decision entries from PROJECT/decisions.md (append ledger)."""
    path = os.path.join(PROJECT, "decisions.md")
    if not os.path.isfile(path):
        return []
    text = open(path, encoding="utf-8").read()
    mts = _mtime(path)
    out = []
    for m in DECISION_RE.finditer(text):
        key, date, title = m.group(1), m.group(2), m.group(3)
        nxt = DECISION_RE.search(text, m.end())
        end = nxt.start() if nxt else len(text)
        body = text[m.start():end].rstrip("\n")
        out.append({
            "addr": "decisions/" + key,
            "title": title,
            "kind": "decision",
            "mtime": _fmt(mts),
            "_mts": mts,
            "_key": key,
            "_date": date,
            "content": body,
        })
    return out


def _journal():
    """Addressable journal entries from PROJECT/journal.md (main file only;
    the archive/ subtree is the immutable zone and is not enumerated)."""
    path = os.path.join(PROJECT, "journal.md")
    if not os.path.isfile(path):
        return []
    lines = open(path, encoding="utf-8").read().splitlines()
    mts = _mtime(path)
    parsed = [m.groups() for m in (JOURNAL_RE.match(l) for l in lines) if m]
    # seq: 1-based among same-date entries, oldest first (parsed is newest-first)
    seen, keyed = {}, []
    for date, jtype, text in reversed(parsed):
        seen[date] = seen.get(date, 0) + 1
        keyed.append((date, seen[date], jtype, text))
    out = []
    for date, seq, jtype, text in keyed:
        raw = "- %s %s：%s" % (date, jtype, text)
        out.append({
            "addr": "journal/%s-%d" % (date, seq),
            "title": text,
            "kind": "journal",
            "mtime": _fmt(mts),
            "_mts": mts,
            "content": raw,
        })
    return out


def _entries():
    return _decisions() + _journal()


def _item(e, extra=()):
    out = {"addr": e["addr"], "title": e["title"], "kind": e["kind"], "mtime": e["mtime"],
           "protocol": PROTOCOL_ID, "proto_ver": proto_ver()}
    for k in extra:
        out[k] = e[k]
    return out


# ---------- semantics ----------

def do_list(kind):
    items = [e for e in _entries() if kind is None or e["kind"] == kind]
    items.sort(key=lambda e: e["addr"])
    return {"ok": True, "semantic": "list", "count": len(items),
            "items": [_item(e) for e in items]}


def do_get(addr):
    m = re.match(r"^decisions/(D-\d+)$", addr)
    if m:
        pool = [e for e in _entries() if e["addr"] == addr]
    else:
        m2 = re.match(r"^journal/(\d{4}-\d{2}-\d{2})-(\d+)$", addr)
        if not m2:
            return {"ok": False, "error_code": "bad_request",
                    "message": "malformed addr %r: expected decisions/D-<n> or journal/<date>-<seq> (see docs/abi.md)" % addr}
        pool = [e for e in _entries() if e["addr"] == addr]
    if not pool:
        return {"ok": False, "error_code": "not_found", "message": "no entry at addr %r" % addr}
    return _item(pool[0], extra=("content",))


def do_search(expr):
    needle = expr.lower()
    items = [e for e in _entries()
             if needle in e["title"].lower() or needle in e["content"].lower()]
    items.sort(key=lambda e: e["addr"])
    return {"ok": True, "semantic": "search", "count": len(items),
            "items": [_item(e) for e in items]}


def _journal_text():
    path = os.path.join(PROJECT, "journal.md")
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return ""


def _op(entry, journal_text):
    # Best effort (abi-spec §2: never lie). A journal line is written once and
    # never rewritten -> create. A decision whose key the journal records is
    # create; otherwise unknown (the ledger file mtime is contaminated by later
    # appends of other entries, so update is never claimed).
    if entry["kind"] == "journal":
        return "create"
    if re.search(r"\b%s\b" % re.escape(entry["_key"]), journal_text):
        return "create"
    return "unknown"


def do_recent(window):
    m = WINDOW_RE.match(window or "")
    if not m:
        return {"ok": False, "error_code": "bad_request",
                "message": "invalid --window %r: expected positive integer with unit d or m (e.g. 7d, 2m)" % window}
    n, unit = int(m.group(1)), m.group(2)
    now = datetime.datetime.now().timestamp()
    span = n * 86400.0 if unit == "d" else n * 86400.0 * 30
    journal_text = _journal_text()
    items = [e for e in _entries() if e["_mts"] is not None and now - e["_mts"] <= span]
    items.sort(key=lambda e: (-e["_mts"], e["addr"]))
    out = []
    for e in items:
        it = _item(e)
        it["op"] = _op(e, journal_text)
        out.append(it)
    return {"ok": True, "semantic": "recent", "count": len(out), "items": out}


# ---------- cli ----------

def _emit(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main(argv):
    if not argv:
        _emit({"ok": False, "error_code": "bad_request",
               "message": "missing semantic: expected list|get|search|recent"})
        return 0
    semantic, rest = argv[0], argv[1:]
    try:
        if semantic == "list":
            kind = None
            if "--kind" in rest:
                i = rest.index("--kind")
                if i + 1 >= len(rest):
                    _emit({"ok": False, "error_code": "bad_request", "message": "--kind needs a value"})
                    return 0
                kind = rest[i + 1]  # unknown kind -> empty result, never an error (smoke relies on this)
            _emit(do_list(kind))
        elif semantic == "get":
            if not rest:
                _emit({"ok": False, "error_code": "bad_request", "message": "get needs an addr"})
            else:
                _emit(do_get(rest[0]))
        elif semantic == "search":
            if not rest:
                _emit({"ok": False, "error_code": "bad_request", "message": "search needs an expression"})
            else:
                _emit(do_search(" ".join(rest)))
        elif semantic == "recent":
            window = "7d"
            if "--window" in rest:
                i = rest.index("--window")
                if i + 1 >= len(rest):
                    _emit({"ok": False, "error_code": "bad_request", "message": "--window needs a value"})
                    return 0
                window = rest[i + 1]
            _emit(do_recent(window))
        else:
            _emit({"ok": False, "error_code": "unsupported_semantic",
                   "message": "unknown semantic %r: expected list|get|search|recent" % semantic})
    except Exception as exc:  # query-level failure, not a crash
        _emit({"ok": False, "error_code": "internal", "message": "%s: %s" % (type(exc).__name__, exc)})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
