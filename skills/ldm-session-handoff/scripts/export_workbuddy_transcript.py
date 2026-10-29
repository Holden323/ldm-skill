#!/usr/bin/env python3
"""
export_workbuddy_transcript.py — 会话交接 Step 1 导出器（WorkBuddy 后端）

Hermes 用 SQLite（export_transcript.py），Claude Code / Codex 用 JSONL（export_jsonl_transcript.py），
WorkBuddy 也用 JSONL，但字段结构不同，所以单独一个后端。

存储位置（2026-09-24 实测）：
  ~/.workbuddy-ai/projects/<工作目录编码>/<sessionId>.jsonl

  工作目录编码规则：绝对路径里的 `/` 和空格都换成 `-`
  例：/Users/likai/WorkBuddy AI/2026-09-23-23-17-40
    → Users-likai-WorkBuddy AI-2026-09-23-23-17-40

行结构（type 字段区分）：
  message                 ← 唯一要导出的原文。role=user/assistant，content=[{type:input_text|output_text, text}]
  reasoning               ← 模型推理记录，过滤
  function_call           ← 工具调用，过滤
  function_call_result    ← 工具输出，过滤
  session-meta / file-history-snapshot / ai-title   ← 元数据，过滤

user 消息里会带环境注入：`<system-reminder ...>...</system-reminder>`，
真正的用户输入包在 `<user_query>...</user_query>` 里。本脚本优先取 user_query，取不到就剥掉 system-reminder。

用法：
  # 列出会话
  python3 export_workbuddy_transcript.py --list
  python3 export_workbuddy_transcript.py --list --date 2026-09-23
  python3 export_workbuddy_transcript.py --list --project "WorkBuddy AI"

  # 导出（sessionId 或路径片段都行）
  python3 export_workbuddy_transcript.py --session 2880e118-b9e0-457f-830e-5de7336bda02 -o /abs/path/全记录.md

  # 调试格式变化
  python3 export_workbuddy_transcript.py --inspect <某个.jsonl路径>
"""

import argparse
import datetime
import glob
import json
import os
import re
import sys

TRUNCATE_LIMIT = 0

PROJECTS_ROOT = "~/.workbuddy-ai/projects"

# user 消息里整块剥掉的环境注入
SYSTEM_REMINDER_RE = re.compile(r"<system-reminder\b.*?</system-reminder>", re.DOTALL)
USER_QUERY_RE = re.compile(r"<user_query>(.*?)</user_query>", re.DOTALL)
# 还有别的注入标签，作为兜底再剥一层
EXTRA_INJECT_RE = re.compile(
    r"<(?:user_info|identity_context|product_identity|project_context|"
    r"manually_attached_skills|craft_mode)\b.*?</(?:user_info|identity_context|"
    r"product_identity|project_context|manually_attached_skills|craft_mode)>",
    re.DOTALL,
)


def fmt_ts(ts) -> str:
    """WorkBuddy 的时间戳是毫秒。同时兼容秒级和 ISO 字符串。"""
    if isinstance(ts, (int, float)):
        v = float(ts)
        if v > 1e11:          # 毫秒
            v /= 1000.0
        try:
            return datetime.datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:%M:%S")
        except (OverflowError, OSError, ValueError):
            return str(ts)
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
    if max_chars and len(text) > max_chars:
        stats["truncated"] += 1
        return text[:max_chars] + "\n[已截断]"
    return text


def clean_user_text(raw: str):
    """返回 (干净文本, 是否过滤掉了注入)。"""
    m = USER_QUERY_RE.findall(raw)
    if m:
        text = "\n".join(x.strip() for x in m if x.strip()).strip()
        return text, True
    stripped = SYSTEM_REMINDER_RE.sub("", raw)
    stripped = EXTRA_INJECT_RE.sub("", stripped)
    stripped = re.sub(r"<[^<>]{0,80}>", "", stripped)  # 残留的空标签
    stripped = stripped.strip()
    return stripped, stripped != raw.strip()


def project_dirs():
    base = os.path.expanduser(PROJECTS_ROOT)
    if not os.path.isdir(base):
        return []
    return sorted(glob.glob(os.path.join(base, "*")))


def session_files(project_filter=None):
    """返回 [(mtime, jsonl路径, sessionId, 项目目录名)]"""
    rows = []
    for proj in project_dirs():
        name = os.path.basename(proj)
        if project_filter and project_filter not in name:
            continue
        for f in glob.glob(os.path.join(proj, "*.jsonl")):
            sid = os.path.basename(f)[:-6]
            rows.append((os.path.getmtime(f), f, sid, name))
    rows.sort(reverse=True)
    return rows


def cmd_list(date=None, limit=10, project_filter=None):
    rows = session_files(project_filter)
    if date:
        d = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        rows = [r for r in rows if datetime.datetime.fromtimestamp(r[0]).date() == d]
    if not rows:
        print(f"(没有符合条件的会话。确认 {PROJECTS_ROOT}/ 下有 *.jsonl)")
        return
    print(f"{'sessionId':<40} {'最后活动':<20} 消息数  工作目录")
    for mtime, f, sid, name in rows[:limit]:
        n = sum(1 for d in read_jsonl(f) if d.get("type") == "message")
        print(f"{sid:<40} {fmt_ts(mtime):<20} {n:<7} {name}")


def resolve_session(session_ref):
    if os.path.isfile(session_ref):
        return session_ref
    hits = [r[1] for r in session_files() if session_ref in r[1] or session_ref in r[2]]
    if not hits:
        sys.exit(f"[错误] 找不到匹配的会话: {session_ref}。用 --list 确认 sessionId 或项目目录名。")
    if len(hits) > 1:
        print(f"[警告] {len(hits)} 个文件匹配，取最近修改的", file=sys.stderr)
    hits.sort(key=os.path.getmtime, reverse=True)
    return hits[0]


def extract(path, max_chars, stats):
    """只取 type=message 的 user/assistant 原文，过滤推理/工具调用/工具输出/元数据。"""
    msgs = []
    for d in read_jsonl(path):
        if d.get("type") != "message":
            continue
        role = d.get("role")
        if role not in ("user", "assistant"):
            continue
        parts = []
        for b in (d.get("content") or []):
            if isinstance(b, dict) and b.get("type") in ("input_text", "output_text"):
                t = (b.get("text") or "").strip()
                if t:
                    parts.append(t)
        raw = "\n".join(parts).strip()
        if not raw:
            continue
        if role == "user":
            text, had_inject = clean_user_text(raw)
            if had_inject:
                stats["filtered_env"] += 1
        else:
            text = raw
        if not text:
            stats["filtered_empty"] += 1
            continue
        msgs.append((role, text, d.get("timestamp")))
    return msgs


def write_markdown(msgs, meta_lines, out_path, max_chars, stats):
    lines = ["# 对话全记录", ""] + meta_lines + [""]
    label = {"user": "用户", "assistant": "助手"}
    for i, (role, text, ts) in enumerate(msgs, 1):
        head = f"## {label.get(role, role)}（第{i}条 · {fmt_ts(ts)}）"
        lines += [head, "", truncate(text, max_chars, stats).strip(), ""]
    if stats["truncated"]:
        lines.append(f"---\n注：{stats['truncated']} 条消息超长已截断至前 {max_chars} 字。原始内容仍在 jsonl 中，未丢失。")
    if stats["filtered_env"]:
        lines.append(f"注：已从 {stats['filtered_env']} 条用户消息中剥离环境注入（system-reminder / user_info 等），保留用户原文。")
    if stats["filtered_empty"]:
        lines.append(f"注：已跳过 {stats['filtered_empty']} 条剥离后为空的消息（纯环境注入，无用户原文）。")
    out = os.path.expanduser(out_path)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[完成] 导出 {len(msgs)} 条消息 → {out}（{os.path.getsize(out)/1024:.1f} KB，"
          f"截断 {stats['truncated']} 条，剥离注入 {stats['filtered_env']} 条，跳过空消息 {stats['filtered_empty']} 条）")


def main():
    ap = argparse.ArgumentParser(
        description="会话交接·对话全记录导出（WorkBuddy 后端）")
    ap.add_argument("--list", action="store_true", help="列出会话")
    ap.add_argument("--date", help="筛选日期 YYYY-MM-DD（配合 --list）")
    ap.add_argument("--project", help="按项目目录名片段筛选（配合 --list）")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--session", help="sessionId 或路径片段")
    ap.add_argument("-o", "--output", help="输出 markdown 路径")
    ap.add_argument("--max-chars", type=int, default=TRUNCATE_LIMIT,
                    help="单条消息截断阈值；默认0表示不截断")
    ap.add_argument("--inspect", metavar="FILE", help="打印某 jsonl 的 type 分布（调试格式变化用）")
    args = ap.parse_args()

    if args.inspect:
        from collections import Counter
        c = Counter()
        for d in read_jsonl(args.inspect):
            c[d.get("type")] += 1
        for k, v in c.most_common():
            print(f"{v:>6}  {k}")
        return

    if args.list or (not args.session and not args.output):
        cmd_list(args.date, args.limit, args.project)
        return

    if not args.session:
        sys.exit("[错误] 导出需要 --session <id>；-o 只能指定输出路径")

    path = resolve_session(args.session)
    stats = {"truncated": 0, "filtered_env": 0, "filtered_empty": 0}
    msgs = extract(path, args.max_chars, stats)

    if not msgs:
        sys.exit("[错误] 该会话没有可导出的 user/assistant 原文消息（用 --inspect 核对格式）")

    first, last = msgs[0][2], msgs[-1][2]
    sid = os.path.basename(path)[:-6] if path.endswith(".jsonl") else path
    trunc = "无" if not args.max_chars else f"单条上限 {args.max_chars} 字，实际截断 {stats['truncated']} 条"
    meta = [
        "> 平台：WorkBuddy",
        f"> 会话标识：{sid}",
        f"> 源文件：{path}",
        f"> 起止时间：{fmt_ts(first)} ~ {fmt_ts(last)}",
        f"> 消息数：{len(msgs)} 条（仅 user/assistant 非空原文；已过滤推理、工具调用、工具输出、元数据）",
        f"> 导出时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "> 导出方式：JSONL 直读逐条导出，非 AI 摘要",
        f"> 截断：{trunc}",
    ]
    out = args.output or f"./对话全记录_{os.path.basename(path)[:40]}.md"
    write_markdown(msgs, meta, out, args.max_chars, stats)


if __name__ == "__main__":
    main()
