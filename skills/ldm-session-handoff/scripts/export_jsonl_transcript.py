#!/usr/bin/env python3
"""
export_jsonl_transcript.py — AI交接班 Step 1 备用导出器（JSONL 格式 Agent）

Hermes 用 SQLite（export_transcript.py），Claude Code / Codex 用 JSONL 行存储。
本脚本覆盖后两者的真实存储格式（2026-08-29 实测）：

  Claude Code  ~/.claude/projects/<工作目录编码>/<sessionId>.jsonl
  Codex        ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl

机制与 export_transcript.py 一致：直读原始记录逐条导出，禁止 AI 摘要冒充档案。

用法：
  # 列出会话（两个后端都支持）
  python3 export_jsonl_transcript.py --list --agent claude
  python3 export_jsonl_transcript.py --list --agent codex --date 2026-08-28

  # 全量导出（claude 用 sessionId，codex 用 rollout 文件路径或路径片段）
  python3 export_jsonl_transcript.py --agent claude --session <sessionId> -o 全记录.md
  python3 export_jsonl_transcript.py --agent codex --session <rollout文件路径> -o 全记录.md

  # 自动探测本机存在的 Agent 类型
  python3 export_jsonl_transcript.py --list --agent auto

若某 Agent 改了存储格式，按报错提示看 --inspect 输出自行核对字段。
"""

import argparse
import datetime
import glob
import json
import os
import sys

TRUNCATE_LIMIT = 3000

# 过滤：这些开头的 user 消息是环境注入，不是用户说的话
CODEX_INJECT_PREFIXES = ("<recommended_plugins>", "<app-context>", "<user_instructions>",
                         "<environment_context>", "# Files mentioned by the user:")
CLAUDE_TOOL_RESULT = "tool_result"


def fmt_ts(ts) -> str:
    """兼容秒级 float 和 ISO 字符串。"""
    if isinstance(ts, (int, float)):
        return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(ts, str):
        try:
            return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")) \
                .astimezone().strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return ts[:19]
    return str(ts)


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue  # 损坏行跳过，不中断整个导出


def truncate(text, max_chars, stats):
    if len(text) > max_chars:
        stats["truncated"] += 1
        return text[:max_chars] + "\n[已截断]"
    return text


# ───────────────────────── Claude Code ─────────────────────────

def claude_project_dirs():
    base = os.path.expanduser("~/.claude/projects")
    if not os.path.isdir(base):
        return []
    return sorted(glob.glob(os.path.join(base, "*")))


def claude_list(date=None, limit=10):
    rows = []
    for proj in claude_project_dirs():
        for f in glob.glob(os.path.join(proj, "*.jsonl")):
            mtime = os.path.getmtime(f)
            if date:
                d = datetime.datetime.strptime(date, "%Y-%m-%d").date()
                if datetime.datetime.fromtimestamp(mtime).date() != d:
                    continue
            rows.append((mtime, os.path.basename(f)[:-6], proj))
    rows.sort(reverse=True)
    if not rows:
        print("(没有符合条件的会话。确认 ~/.claude/projects/ 下有 *.jsonl)")
        return
    print(f"{'sessionId':<40} {'最后活动':<20} 工作目录")
    for mtime, sid, proj in rows[:limit]:
        print(f"{sid:<40} {fmt_ts(mtime):<20} {proj}")


def claude_export(session_id, max_chars, stats):
    hits = []
    for proj in claude_project_dirs():
        p = os.path.join(proj, session_id + ".jsonl")
        if os.path.exists(p):
            hits.append(p)
    if not hits:
        sys.exit(f"[错误] 找不到 {session_id}.jsonl。用 --list 确认 sessionId 和所在项目目录。")
    if len(hits) > 1:
        print(f"[警告] {len(hits)} 个项目目录下存在同名 sessionId，取最近修改的", file=sys.stderr)
    hits.sort(key=os.path.getmtime, reverse=True)
    return hits[0]


def claude_extract(path, max_chars, stats):
    """从 Claude Code jsonl 提取真实对话。

    格式实测（v2.1.x）：
      type=user      message.content 是 str，或 block 数组（tool_result 要过滤）
      type=assistant message.content 是 block 数组，只取 type=text（thinking/tool_use 过滤）
    """
    msgs = []
    for d in read_jsonl(path):
        if d.get("type") not in ("user", "assistant"):
            continue
        content = (d.get("message") or {}).get("content")
        ts = d.get("timestamp")
        if isinstance(content, str):
            text = content.strip()
        elif isinstance(content, list):
            parts = []
            for b in content:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text" and b.get("text", "").strip():
                    parts.append(b["text"].strip())
            text = "\n".join(parts).strip()
        else:
            continue
        if not text:
            continue
        role = "user" if d["type"] == "user" else "assistant"
        msgs.append((role, text, ts))
    return msgs


# ───────────────────────── Codex ─────────────────────────

def codex_files():
    base = os.path.expanduser("~/.codex/sessions")
    if not os.path.isdir(base):
        return []
    return glob.glob(os.path.join(base, "*", "*", "*", "rollout-*.jsonl"))


def codex_list(date=None, limit=10):
    rows = []
    for f in codex_files():
        mtime = os.path.getmtime(f)
        if date:
            d = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            if datetime.datetime.fromtimestamp(mtime).date() != d:
                continue
        rows.append((mtime, f))
    rows.sort(reverse=True)
    if not rows:
        print("(没有符合条件的会话。确认 ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl 存在)")
        return
    print(f"{'最后活动':<20} rollout文件")
    for mtime, f in rows[:limit]:
        print(f"{fmt_ts(mtime):<20} {f}")


def codex_resolve(session_ref):
    """session_ref 可以是完整路径或路径片段。"""
    if os.path.isfile(session_ref):
        return session_ref
    hits = [f for f in codex_files() if session_ref in f]
    if not hits:
        sys.exit(f"[错误] 找不到匹配的 rollout 文件: {session_ref}。用 --list 确认。")
    if len(hits) > 1:
        print(f"[警告] {len(hits)} 个文件匹配，取最近修改的", file=sys.stderr)
    hits.sort(key=os.path.getmtime, reverse=True)
    return hits[0]


def codex_extract(path, max_chars, stats):
    """从 Codex rollout jsonl 提取真实对话。

    格式实测（0.149.x）：
      type=response_item, payload.type=message, payload.role=user/assistant
      payload.content = [{type: input_text/output_text, text: ...}]
      环境注入消息（<recommended_plugins> 等开头）过滤，工具调用/推理记录过滤。
    """
    msgs = []
    for d in read_jsonl(path):
        if d.get("type") != "response_item":
            continue
        p = d.get("payload") or {}
        if p.get("type") != "message" or p.get("role") not in ("user", "assistant"):
            continue
        parts = []
        for b in (p.get("content") or []):
            if isinstance(b, dict) and b.get("type") in ("input_text", "output_text"):
                t = (b.get("text") or "").strip()
                if t:
                    parts.append(t)
        text = "\n".join(parts).strip()
        if not text:
            continue
        if p["role"] == "user" and any(text.startswith(px) for px in CODEX_INJECT_PREFIXES):
            stats["filtered_env"] += 1
            continue
        if p["role"] == "assistant" and text.startswith("<user_instructions>"):
            stats["filtered_env"] += 1
            continue
        ts = d.get("timestamp")
        msgs.append((p["role"], text, ts))
    return msgs


# ───────────────────────── 输出 ─────────────────────────

def write_markdown(msgs, meta_lines, out_path, max_chars, stats):
    lines = ["# 对话全记录", ""] + meta_lines + [""]
    label = {"user": "用户", "assistant": "助手"}
    for i, (role, text, ts) in enumerate(msgs, 1):
        head = f"## {label.get(role, role)}（第{i}条 · {fmt_ts(ts)}）"
        lines += [head, "", truncate(text, max_chars, stats).strip(), ""]
    if stats["truncated"]:
        lines.append(f"---\n注：{stats['truncated']} 条消息超长已截断至前 {max_chars} 字。原始内容仍在 jsonl 中，未丢失。")
    if stats["filtered_env"]:
        lines.append(f"注：已过滤 {stats['filtered_env']} 条环境注入消息（非用户原文）。")
    out = os.path.expanduser(out_path)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[完成] 导出 {len(msgs)} 条消息 → {out}（{os.path.getsize(out)/1024:.1f} KB，"
          f"截断 {stats['truncated']} 条，过滤环境注入 {stats['filtered_env']} 条）")


def main():
    ap = argparse.ArgumentParser(
        description="AI交接班·对话全记录导出（JSONL版：Claude Code / Codex）")
    ap.add_argument("--agent", choices=["auto", "claude", "codex"], default="auto",
                    help="目标 Agent（默认 auto：探测本机哪个存在）")
    ap.add_argument("--list", action="store_true", help="列出会话")
    ap.add_argument("--date", help="筛选日期 YYYY-MM-DD（配合 --list）")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--session", help="claude=sessionId / codex=rollout文件路径或片段")
    ap.add_argument("-o", "--output", help="输出 markdown 路径")
    ap.add_argument("--max-chars", type=int, default=TRUNCATE_LIMIT)
    ap.add_argument("--inspect", metavar="FILE",
                    help="打印某 jsonl 的 type 分布（调试格式变化用）")
    args = ap.parse_args()

    if args.inspect:
        from collections import Counter
        c = Counter()
        for d in read_jsonl(args.inspect):
            key = d.get("type")
            if d.get("type") == "response_item":
                key = f"response_item/{(d.get('payload') or {}).get('type')}"
            c[key] += 1
        for k, v in c.most_common():
            print(f"{v:>6}  {k}")
        return

    agent = args.agent
    if agent == "auto":
        has_claude = bool(claude_project_dirs())
        has_codex = bool(codex_files())
        if has_claude and not has_codex:
            agent = "claude"
        elif has_codex and not has_claude:
            agent = "codex"
        else:
            sys.exit("[错误] 本机 Claude Code 和 Codex 都有会话数据，--agent 必须显式指定 claude 或 codex")

    stats = {"truncated": 0, "filtered_env": 0}

    if args.list or (not args.session and not args.output):
        if agent == "claude":
            claude_list(args.date, args.limit)
        else:
            codex_list(args.date, args.limit)
        return

    if agent == "claude":
        path = claude_export(args.session, args.max_chars, stats)
        backend = "Claude Code (jsonl)"
        msgs = claude_extract(path, args.max_chars, stats)
    else:
        path = codex_resolve(args.session)
        backend = "Codex (rollout jsonl)"
        msgs = codex_extract(path, args.max_chars, stats)

    if not msgs:
        sys.exit("[错误] 该会话没有可导出的 user/assistant 原文消息（全是工具调用？用 --inspect 核对格式）")

    first, last = msgs[0][2], msgs[-1][2]
    meta = [
        f"> 后端: {backend}",
        f"> 源文件: {path}",
        f"> 起止时间: {fmt_ts(first)} ~ {fmt_ts(last)}",
        f"> 消息数: {len(msgs)} 条（仅 user/assistant 非空原文，已过滤工具输出与环境注入）",
        f"> 导出时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 导出方式: JSONL 直读逐条导出，非AI摘要",
    ]
    out = args.output or f"./对话全记录_{os.path.basename(path)[:40]}.md"
    write_markdown(msgs, meta, out, args.max_chars, stats)


if __name__ == "__main__":
    main()
