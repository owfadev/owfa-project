#!/usr/bin/env python3
"""tests/test_check_pin.py — rule 7 of the check member: the owfadevelop target pin.

The attached audit must parse `PROJECT/owfadevelop/target.md` when present:
exactly one `target: owfa/<kernel|protocol|package:<id>>` line plus a non-empty
`why:` line; anything else is an error. Absent file = no finding (generic loop).

Run: python3 -m unittest discover -s tests -p "test_*.py"
"""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "check" / "scripts" / "check.py"
_spec = importlib.util.spec_from_file_location("project_check", _SCRIPT)
check_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_mod)


class _Ctx:
    def __init__(self, root):
        self.root = str(root)


def _mk(root, files):
    for rel, text in files.items():
        p = Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


class PinTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # baseline healthy workspace: marker + journal + decisions, no pin
        _mk(self.root, {
            ".owfa/WORKSPACE.yaml": 'kernel_compat: ">= 0.4.6"\n',
            "PROJECT/journal.md": "- 2026-11-16 develop：pin rule session\n",
            "PROJECT/decisions.md": "## D-1 2026-11-16 first\n",
        })

    def issues(self):
        return check_mod.check(_Ctx(self.root))

    def test_absent_pin_no_finding(self):
        msgs = [i["message"] for i in self.issues()]
        self.assertFalse(any("target.md" in m for m in msgs))

    def test_wellformed_pin_passes(self):
        for target in ("owfa/kernel", "owfa/protocol", "owfa/package:owfa-cuhksz"):
            with self.subTest(target=target):
                _mk(self.root, {"PROJECT/owfadevelop/target.md":
                                f"target: {target}\nwhy: this workspace develops {target}\n"})
                msgs = [i["message"] for i in self.issues()]
                self.assertFalse(any("target.md" in m for m in msgs))

    def test_malformed_pin_errors(self):
        cases = {
            "two targets": "target: owfa/kernel\ntarget: owfa/protocol\nwhy: x\n",
            "bad component": "target: owfa/website\nwhy: x\n",
            "package without id": "target: owfa/package\nwhy: x\n",
            "missing why": "target: owfa/kernel\n",
            "empty why": "target: owfa/kernel\nwhy:   \n",
        }
        for name, text in cases.items():
            with self.subTest(case=name):
                _mk(self.root, {"PROJECT/owfadevelop/target.md": text})
                errs = [i for i in self.issues() if "target.md" in i["message"]]
                self.assertTrue(errs, name)
                self.assertTrue(all(e["level"] == "error" for e in errs), name)


if __name__ == "__main__":
    unittest.main()
