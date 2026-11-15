#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-tests for the project protocol's ABI surface (abi-spec v2 §7.2).

Runs a real copy of proto_query.py + PKG.yaml installed at the canonical
package path of a throwaway workspace, so the bootstrap resolution and the
proto_ver derivation are exercised the way a consumer would see them.

    python3 tests/test_proto_query.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

PKG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PKG_ROOT, "proto_query.py")
PKG_YAML = os.path.join(PKG_ROOT, "PKG.yaml")

DECISIONS_MD = """# 决策账

> 只在底部追加，永不改写。

## D-1 2026-11-10 Adopt the project protocol

- Context: the workspace is a project, not an information repository.
- Decision: project protocol over the legacy projects/ domain.
- Consequence: one territory directory PROJECT/, zero vault/wiki split.

## D-2 2026-11-14 Journal stays prepend-top

- Context: freshness beats archaeology for a run log.
- Decision: prepend at top, rolling window of 100.
- Consequence: archive subtree owns the overflow.
"""

JOURNAL_MD = """# 运行日志

> 置顶追加、只增不删；条目 = `- YYYY-MM-DD <类型>：一句话`，类型枚举 map/save/check/plugin/develop/other。规则见 `.owfa/plugins/domains/project/journal/`，写走 `pipeline.py journal`。

- 2026-11-14 save: decision D-1 appended to the ledger
- 2026-11-15 develop: worked on the ABI surface
"""


class AbiFixture:
    """A throwaway workspace with the package installed at the canonical path."""

    def __init__(self, root):
        self.root = root
        install = os.path.join(root, ".owfa", "plugins", "domains", "project")
        os.makedirs(install)
        shutil.copy(SCRIPT, os.path.join(install, "proto_query.py"))
        shutil.copy(PKG_YAML, os.path.join(install, "PKG.yaml"))
        project = os.path.join(root, "PROJECT")
        os.makedirs(project)
        with open(os.path.join(project, "decisions.md"), "w", encoding="utf-8") as f:
            f.write(DECISIONS_MD)
        with open(os.path.join(project, "journal.md"), "w", encoding="utf-8") as f:
            f.write(JOURNAL_MD)
        self.script = os.path.join(install, "proto_query.py")

    def run(self, *args):
        p = subprocess.run([sys.executable, self.script] + list(args),
                           capture_output=True, text=True, encoding="utf-8")
        return p.returncode, json.loads(p.stdout)


class ProtoQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory(prefix="owfa-abi-test-")
        cls.fx = AbiFixture(cls._tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def run_q(self, *args):
        return self.fx.run(*args)

    # -- envelope fields ------------------------------------------------

    def test_batch_envelope_fields(self):
        code, out = self.run_q("list")
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["semantic"], "list")
        self.assertEqual(out["count"], len(out["items"]))
        self.assertEqual(out["count"], 4)  # 2 decisions + 2 journal entries
        for item in out["items"]:
            for field in ("addr", "title", "kind", "mtime", "protocol", "proto_ver"):
                self.assertIn(field, item)
            self.assertEqual(item["protocol"], "project")
        kinds = {i["kind"] for i in out["items"]}
        self.assertEqual(kinds, {"decision", "journal"})
        addrs = {i["addr"] for i in out["items"]}
        self.assertEqual(addrs, {"decisions/D-1", "decisions/D-2",
                                 "journal/2026-11-14-1", "journal/2026-11-15-1"})

    def test_proto_ver_derived_from_pkg_yaml(self):
        with open(PKG_YAML, encoding="utf-8") as f:
            m = re.search(r"^version:\s*(\S+)", f.read(), re.M)
        self.assertIsNotNone(m, "PKG.yaml must carry a version for proto_ver derivation")
        code, out = self.run_q("get", "decisions/D-1")
        self.assertEqual(code, 0)
        self.assertEqual(out["proto_ver"], m.group(1))

    # -- one example per semantic ---------------------------------------

    def test_semantic_list_kind_filter_and_unknown_kind(self):
        code, out = self.run_q("list", "--kind", "decision")
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        self.assertEqual([i["addr"] for i in out["items"]], ["decisions/D-1", "decisions/D-2"])
        code, out = self.run_q("list", "--kind", "__abi_smoke")  # unknown kind: empty, never an error
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["count"], 0)
        self.assertEqual(out["items"], [])

    def test_semantic_get_returns_verbatim_content(self):
        code, out = self.run_q("get", "decisions/D-2")
        self.assertEqual(code, 0)
        for field in ("addr", "title", "kind", "mtime", "content", "protocol", "proto_ver"):
            self.assertIn(field, out)
        self.assertEqual(out["title"], "Journal stays prepend-top")
        self.assertIn("## D-2 2026-11-14 Journal stays prepend-top", out["content"])
        self.assertIn("rolling window of 100", out["content"])
        self.assertNotIn("## D-1", out["content"])  # entry section only, not the whole file

    def test_semantic_search_substring(self):
        code, out = self.run_q("search", "ROLLING")  # case-insensitive
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        self.assertEqual([i["addr"] for i in out["items"]], ["decisions/D-2"])
        code, out = self.run_q("search", "ABI surface")  # hits a journal line
        self.assertEqual(out["count"], 1)
        self.assertEqual(out["items"][0]["addr"], "journal/2026-11-15-1")

    def test_semantic_recent_window_and_op(self):
        code, out = self.run_q("recent")  # default 7d; fixture files are fresh
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        self.assertGreaterEqual(out["count"], 4)
        ops = {i["addr"]: i["op"] for i in out["items"]}
        self.assertEqual(ops["decisions/D-1"], "create")   # journal mentions D-1
        self.assertEqual(ops["decisions/D-2"], "unknown")  # never mentioned, never guessed
        self.assertEqual(ops["journal/2026-11-15-1"], "create")
        self.assertNotIn("update", ops.values())           # never claimed (docs/abi.md)

    # -- error envelopes -------------------------------------------------

    def test_error_not_found(self):
        code, out = self.run_q("get", "decisions/D-99")
        self.assertEqual(code, 0)  # query-level failure: exit 0, ok:false
        self.assertFalse(out["ok"])
        self.assertEqual(out["error_code"], "not_found")
        self.assertTrue(out.get("message"))

    def test_error_bad_request_window(self):
        code, out = self.run_q("recent", "--window", "seven")
        self.assertEqual(code, 0)
        self.assertFalse(out["ok"])
        self.assertEqual(out["error_code"], "bad_request")
        code, out = self.run_q("get", "notes/whatever")  # malformed addr shape
        self.assertEqual(code, 0)
        self.assertEqual(out["error_code"], "bad_request")

    def test_error_unsupported_semantic(self):
        code, out = self.run_q("purge")
        self.assertEqual(code, 0)
        self.assertFalse(out["ok"])
        self.assertEqual(out["error_code"], "unsupported_semantic")


if __name__ == "__main__":
    unittest.main(verbosity=2)
