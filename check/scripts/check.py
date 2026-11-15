#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check member attached audit: the protocol's health surface, mechanical items.

Project-protocol note: ctx.pages (the vaultwiki wiki/ scan) is empty in a project
workspace by design — this script walks PROJECT/ itself from ctx.root. Read-only,
zero side effects; repairs belong to commands/humans. Messages in Chinese.
"""
import datetime
import os
import re

TYPES = ("map", "save", "check", "plugin", "develop", "other")
DATE_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) ([A-Za-z]+)(?:[\uff1a:]|\s)")   # - YYYY-MM-DD type：one sentence
D_RE = re.compile(r"^## D-(\d+) (\d{4}-\d{2}-\d{2}) ")
JOURNAL_MAX = 100


def _walk_md(root_proj):
    """All .md files under PROJECT/ (repo-relative paths), excluding packages/ (machine zone)."""
    out = []
    if not os.path.isdir(root_proj):
        return out
    for dirpath, dirs, files in os.walk(root_proj):
        dirs[:] = sorted(d for d in dirs if d != "packages")   # machine zone: not the protocol's content
        for fn in sorted(files):
            if fn.endswith(".md"):
                out.append(os.path.relpath(os.path.join(dirpath, fn), root_proj).replace(os.sep, "/"))
    return out


def check(ctx):
    issues = []
    root = getattr(ctx, "root", os.getcwd())
    proj = os.path.join(root, "PROJECT")

    # workspace marker
    if not os.path.isfile(os.path.join(root, ".owfa", "WORKSPACE.yaml")):
        issues.append({"level": "info", "message": "工作区标记 .owfa/WORKSPACE.yaml 缺失（kernel-home F2 发现依赖它）"})

    # journal discipline: date + enum, main file and archive alike
    journal_files = []
    if os.path.isfile(os.path.join(proj, "journal.md")):
        journal_files.append(("PROJECT/journal.md", os.path.join(proj, "journal.md")))
    arch_root = os.path.join(proj, "archive")
    if os.path.isdir(arch_root):
        for dirpath, _dirs, files in os.walk(arch_root):
            for fn in sorted(files):
                if fn == "journal.md":
                    journal_files.append(
                        ("PROJECT/archive/.../journal.md", os.path.join(dirpath, fn)))
    main_count = 0
    for label, path in journal_files:
        for raw in open(path, encoding="utf-8").read().splitlines():
            if not raw.startswith("- "):
                continue
            m = DATE_RE.match(raw)
            if not m:
                issues.append({"level": "error", "message": f"{label}: 无日期或格式不对的条目（{raw[:40]!r}）"})
                continue
            try:
                datetime.date.fromisoformat(m.group(1))
            except ValueError:
                issues.append({"level": "error", "message": f"{label}: 日期不真实（{m.group(1)}）"})
            if m.group(2) not in TYPES:
                issues.append({"level": "error", "message": f"{label}: 类型 {m.group(2)!r} 不在枚举 map/save/check/plugin/develop/other"})
        if label == "PROJECT/journal.md":
            main_count = sum(1 for raw in open(path, encoding="utf-8").read().splitlines() if raw.startswith("- "))
    if main_count > JOURNAL_MAX:
        issues.append({"level": "warning", "message": f"PROJECT/journal.md 条目 {main_count} 超窗（>{JOURNAL_MAX}，跑 pipeline.py journal 触发机械归档）"})

    # decisions discipline: D-n headings, monotone and unique
    dpath = os.path.join(proj, "decisions.md")
    if os.path.isfile(dpath):
        nums = []
        for raw in open(dpath, encoding="utf-8").read().splitlines():
            m = D_RE.match(raw)
            if m:
                try:
                    datetime.date.fromisoformat(m.group(2))
                except ValueError:
                    issues.append({"level": "error", "message": f"decisions.md: D-{m.group(1)} 日期不真实（{m.group(2)}）"})
                nums.append(int(m.group(1)))
            elif re.match(r"^## D-\d+\b", raw):
                issues.append({"level": "error", "message": f"decisions.md: 条目标题不符合 `D-<n> YYYY-MM-DD`（{raw[:40]!r}）"})
        if nums != sorted(nums):
            issues.append({"level": "error", "message": "decisions.md: D-<n> 序号非单调递增"})
        if len(nums) != len(set(nums)):
            issues.append({"level": "error", "message": "decisions.md: D-<n> 序号重复"})
    else:
        issues.append({"level": "info", "message": "PROJECT/decisions.md 尚未建立（锚页，卸载保护对象）"})

    # index drift: page list vs tree (compare against the rendered expectation)
    pages = _walk_md(proj)
    expected = {p for p in pages
                if p not in ("index.md", "journal.md") and not p.startswith("archive/")}
    listed = set()
    ipath = os.path.join(proj, "index.md")
    if os.path.isfile(ipath):
        in_list = False
        for raw in open(ipath, encoding="utf-8").read().splitlines():
            if raw.startswith("## "):
                in_list = raw.startswith("## Pages")
            m = re.match(r"^- `(.+?\.md)`", raw) if in_list else None
            if m:
                listed.add(m.group(1))
        missing = expected - listed
        extra = listed - expected
        if missing or extra:
            parts = []
            if missing:
                parts.append("缺 " + ", ".join(sorted(missing)))
            if extra:
                parts.append("多 " + ", ".join(sorted(extra)))
            issues.append({"level": "warning",
                           "message": "PROJECT/index.md 页清单与树漂移（" + "；".join(parts) + "）——跑 pipeline.py index 重建"})
        # anchor drift: anchors block entries must exist in the repo
        in_anchor = False
        for raw in open(ipath, encoding="utf-8").read().splitlines():
            if "<!-- project-anchors:" in raw:
                in_anchor = "start" in raw
                continue
            if in_anchor:
                m = re.match(r"^- `([^`]+)`", raw)
                if m and not os.path.exists(os.path.join(root, m.group(1))):
                    issues.append({"level": "warning", "message": f"锚点漂移：声明的 {m.group(1)!r} 在仓库中不存在（更新 index.md 的 Anchors 块）"})
    return issues
