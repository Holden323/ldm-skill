#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ldm-memory-system 机械扫描脚本（只读，不修改任何文件）

确定性检查（借鉴 claude-obsidian wiki-lint 的设计：引擎只报告，AI负责解释和出清单）：
1. 无README目录      —— 目录缺索引 = 黑数据
2. 根目录散落文件    —— 超过阈值的散落文档 = 待归位信号
3. 同名文件跨位置    —— 疑似版本分叉/旧副本
4. 同名目录跨位置    —— 疑似旧工作副本
5. 空目录            —— 无内容目录
6. 同名文件在目录内  —— 疑似多副本（如 rules.md 两份）
7. 失效绝对路径      —— Markdown 里写的 /Users/… 或 ~/… 已不存在（含空格的路径可能被截断，已尽量排除）
8. 断掉的 [[链接]]   —— 找不到同名 .md 文件
9. 记忆索引对账      —— 目标目录有 MEMORY.md 时：索引指向的文件缺失、条目文件没进索引、索引超过 200 行或 25 KB
10. 真源声明         —— 「以 X 为准」「先读 X」「唯一真源」等句子的位置，供人工核对 X 是否真的最新

用法：
    python3 scan.py <目标目录> [--depth N] [--max-scatter N]

输出：JSON 报告（stdout）。所有发现均为"候选"，处置需用户拍板。
原则：只读扫描；不推断意图；孤儿可能是故意的。
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import unquote

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "chrome-user-data", ".obsidian", ".DS_Store",
}

# 白名单：设计上就该每个目录一份的文件，跨目录同名不是分叉（claude-obsidian allowlist思想）
# 决策事件标准结构：每个决策事件目录都含 原始信息.md / 决策工作区.md，内容各不相同属正常
# SKILL.md/references：每个skill目录一份，同名正常
ALLOWLIST_NAMES = {"readme.md", ".ds_store", "原始信息.md", "决策工作区.md",
                   "skill.md"}


def file_hash(path, limit_mb=50):
    """对大文件只读前 N MB 做哈希（足够判定相同，避免读巨大文件）"""
    try:
        size = os.path.getsize(path)
        if size > limit_mb * 1024 * 1024:
            return f"partial:{size}"
        h = hashlib.md5()
        with open(path, "rb") as f:
            h.update(f.read())
        return h.hexdigest()
    except OSError:
        return "unreadable"


def is_text_file(path):
    ext = os.path.splitext(path)[1].lower()
    return ext in {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".js",
                   ".sh", ".html", ".css", ".csv"}


PATH_RE = re.compile(r"((?:/Users/|~/)[^\s`\"'<>|（）()「」『』，。；：、*\[\]]+)")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
MDLINK_RE = re.compile(r"\]\(([^)\s]+\.md)\)")
CLAIM_RE = re.compile(
    r"以[^。\n]{1,40}?为准|先读|唯一真源|source of truth|takes precedence",
    re.IGNORECASE)
PLACEHOLDER_MARKS = ("{", "<", "YYYY", "...", "…", "*", "$")
MEMORY_INDEX_MAX_LINES = 200
MEMORY_INDEX_MAX_BYTES = 25 * 1024
REF_LIST_CAP = 100


def path_state(raw):
    """返回 'ok' / 'missing' / 'skip'。含空格的路径常在空格处被截断，前缀能匹配到真实文件时跳过。"""
    p = raw.rstrip(".,:;：；，。、")
    if any(m in p for m in PLACEHOLDER_MARKS):
        return "skip"
    if "%" in p:
        p = unquote(p)
    p = os.path.expanduser(p)
    if os.path.exists(p):
        return "ok"
    parent, base = os.path.dirname(p), os.path.basename(p)
    try:
        if os.path.isdir(parent) and any(
                e.startswith(base) for e in os.listdir(parent)):
            return "skip"
    except OSError:
        pass
    return "missing"


def check_refs(root, md_files, all_basenames):
    """检查 7、8、10：失效绝对路径、断掉的 [[链接]]、真源声明。"""
    dead, broken, claims = [], [], []
    for rel in md_files:
        try:
            with open(os.path.join(root, rel), encoding="utf-8",
                      errors="ignore") as f:
                lines = f.read().split("\n")
        except OSError:
            continue
        for no, line in enumerate(lines, 1):
            for raw in PATH_RE.findall(line):
                if path_state(raw) == "missing" and len(dead) < REF_LIST_CAP:
                    dead.append({"file": rel, "line": no,
                                 "path": raw.rstrip(".,:;：；，。、")})
            for name in WIKILINK_RE.findall(line):
                name = name.strip()
                if (name.lower() not in all_basenames
                        and len(broken) < REF_LIST_CAP):
                    broken.append({"file": rel, "line": no, "link": name})
            if CLAIM_RE.search(line) and len(claims) < REF_LIST_CAP:
                claims.append({"file": rel, "line": no,
                               "text": line.strip()[:100]})
    return dead, broken, claims


def check_memory_index(root):
    """检查 9：目标目录本身是记忆目录（有 MEMORY.md）时，索引和条目文件对账。"""
    index = os.path.join(root, "MEMORY.md")
    if not os.path.isfile(index):
        return None
    with open(index, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    links = {unquote(x) for x in MDLINK_RE.findall(text)
             if not x.startswith(("http://", "https://"))}
    linked = {x for x in links if "/" not in x}
    entries = {e for e in os.listdir(root)
               if e.endswith(".md") and e != "MEMORY.md"
               and os.path.isfile(os.path.join(root, e))}
    n_lines = text.count("\n") + (0 if text.endswith("\n") else 1)
    n_bytes = len(text.encode("utf-8"))
    return {
        "lines": n_lines,
        "bytes": n_bytes,
        "limit": f"{MEMORY_INDEX_MAX_LINES} 行或 {MEMORY_INDEX_MAX_BYTES} 字节（Claude Code 启动只加载这么多）",
        "over_limit": (n_lines > MEMORY_INDEX_MAX_LINES
                       or n_bytes > MEMORY_INDEX_MAX_BYTES),
        "over_70_percent": (n_lines > MEMORY_INDEX_MAX_LINES * 0.7
                            or n_bytes > MEMORY_INDEX_MAX_BYTES * 0.7),
        "linked_but_missing": sorted(
            x for x in links
            if not os.path.exists(os.path.join(root, os.path.expanduser(x)))),
        "not_indexed": sorted(entries - linked),
    }


def scan(root, max_depth, max_scatter):
    report = {
        "scanned_root": root,
        "scanned_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "max_depth": max_depth,
        "findings": {
            "no_readme_dirs": [],
            "root_scatter_files": [],
            "duplicate_files_across_dirs": [],
            "duplicate_dirs_across_locations": [],
            "empty_dirs": [],
            "same_name_files_in_dir": [],
            "dead_paths": [],
            "broken_wikilinks": [],
            "memory_index": None,
            "authority_claims": [],
        },
        "stats": {},
    }
    root = os.path.abspath(root)
    name_to_paths = {}       # 文件名 -> [路径]
    dir_name_to_paths = {}   # 目录名 -> [路径]
    md_files = []            # 供检查 7、8、10
    all_basenames = set()    # 不含扩展名、小写，供 [[链接]] 解析
    total_files = 0
    total_dirs = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # 跳过隐藏目录和依赖目录
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")]

        rel_dir = os.path.relpath(dirpath, root)
        depth = 0 if rel_dir == "." else rel_dir.count(os.sep) + 1
        if depth > max_depth:
            dirnames[:] = []
            continue

        total_dirs += 1

        # --- 检查1：无README目录（只查含文件的目录，跳过根本身） ---
        if rel_dir != "." and filenames:
            if "README.md" not in filenames:
                # 排除只有README该有的最小目录（1-2个文件的目录也该有）
                report["findings"]["no_readme_dirs"].append(
                    {"dir": rel_dir, "file_count": len(filenames)})

        # --- 检查5：空目录 ---
        if rel_dir != "." and not dirnames and not filenames:
            report["findings"]["empty_dirs"].append(rel_dir)

        # --- 检查6：同一目录内同名文件（大小写不敏感） ---
        seen_names = {}
        for fn in filenames:
            key = fn.lower()
            if key in seen_names:
                report["findings"]["same_name_files_in_dir"].append(
                    {"dir": rel_dir, "name": fn,
                     "conflict_with": seen_names[key]})
            seen_names[key] = fn

        # --- 收集 Markdown 和文件基名（供检查 7、8、10） ---
        for fn in filenames:
            all_basenames.add(os.path.splitext(fn)[0].lower())
            if fn.lower().endswith(".md"):
                md_files.append(
                    os.path.relpath(os.path.join(dirpath, fn), root))

        # --- 收集文件名（供跨目录查重） ---
        for fn in filenames:
            if not is_text_file(fn) and os.path.getsize(
                    os.path.join(dirpath, fn)) > 2 * 1024 * 1024:
                continue  # 跳过大二进制
            total_files += 1
            rel_path = os.path.relpath(os.path.join(dirpath, fn), root)
            name_to_paths.setdefault(fn.lower(), []).append(rel_path)

        # --- 收集目录名 ---
        for d in dirnames:
            rel_path = os.path.relpath(os.path.join(dirpath, d), root)
            dir_name_to_paths.setdefault(d, []).append(rel_path)

    # --- 检查2：根目录散落文件 ---
    try:
        root_entries = sorted(os.listdir(root))
    except OSError:
        root_entries = []
    scatter = [e for e in root_entries
               if os.path.isfile(os.path.join(root, e))
               and e not in {"README.md", ".DS_Store"}]
    if len(scatter) > max_scatter:
        report["findings"]["root_scatter_files"] = {
            "count": len(scatter), "threshold": max_scatter, "files": scatter}

    # --- 检查3：同名文件跨目录（同名但内容不同 = 版本分叉；相同 = 冗余副本） ---
    for name, paths in name_to_paths.items():
        if name in ALLOWLIST_NAMES:
            continue  # 设计上每目录一份的文件不报
        if len(paths) < 2:
            continue
        # 只关注不同目录下的同名
        dirs = {os.path.dirname(p) for p in paths}
        if len(dirs) < 2:
            continue
        hashes = {}
        for p in paths[:8]:  # 限制计算量
            full = os.path.join(root, p)
            if os.path.isfile(full):
                hashes[p] = file_hash(full)
        groups = {}
        for p, h in hashes.items():
            groups.setdefault(h, []).append(p)
        identical = [g for g in groups.values() if len(g) > 1]
        report["findings"]["duplicate_files_across_dirs"].append(
            {"name": name, "paths": paths,
             "identical_groups": identical,
             "note": ("内容完全相同=冗余副本" if identical
                      else "内容不同=疑似版本分叉")})

    # --- 检查4：同名目录跨位置 ---
    for name, paths in dir_name_to_paths.items():
        if len(paths) < 2:
            continue
        report["findings"]["duplicate_dirs_across_locations"].append(
            {"name": name, "locations": paths,
             "note": "疑似旧工作副本/重复目录，需diff内容+时间戳判定"})

    # --- 检查 7、8、10：引用和声明 ---
    dead, broken, claims = check_refs(root, md_files, all_basenames)
    report["findings"]["dead_paths"] = dead
    report["findings"]["broken_wikilinks"] = broken
    report["findings"]["authority_claims"] = claims

    # --- 检查 9：记忆索引对账 ---
    mem = check_memory_index(root)
    report["findings"]["memory_index"] = mem

    # --- 统计 ---
    report["stats"] = {
        "total_files": total_files,
        "total_dirs": total_dirs,
        "no_readme_dirs": len(report["findings"]["no_readme_dirs"]),
        "root_scatter_count": (
            report["findings"]["root_scatter_files"]["count"]
            if isinstance(report["findings"]["root_scatter_files"], dict)
            else 0),
        "duplicate_file_names": len(
            report["findings"]["duplicate_files_across_dirs"]),
        "duplicate_dir_names": len(
            report["findings"]["duplicate_dirs_across_locations"]),
        "empty_dirs": len(report["findings"]["empty_dirs"]),
        "dead_paths": len(dead),
        "broken_wikilinks": len(broken),
        "authority_claims": len(claims),
        "memory_index_issues": (
            None if mem is None else
            len(mem["linked_but_missing"]) + len(mem["not_indexed"])
            + (1 if mem["over_limit"] else 0)),
    }
    return report


def main():
    ap = argparse.ArgumentParser(description="ldm-memory-system 只读扫描")
    ap.add_argument("target", help="要扫描的目录")
    ap.add_argument("--depth", type=int, default=2,
                    help="扫描深度（默认2层）")
    ap.add_argument("--max-scatter", type=int, default=10,
                    help="根目录散落文件阈值（默认10，超过才报告）")
    ap.add_argument("--compact", action="store_true",
                    help="只输出统计和发现，不输出详情")
    args = ap.parse_args()

    if not os.path.isdir(args.target):
        print(json.dumps({"error": f"目录不存在: {args.target}"},
                         ensure_ascii=False))
        sys.exit(1)

    report = scan(args.target, args.depth, args.max_scatter)

    if args.compact:
        out = {"scanned_root": report["scanned_root"],
               "stats": report["stats"]}
    else:
        out = report
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
