#!/usr/bin/env python3
"""
export_transcript.py — AI交接班 Step 1：对话全记录导出脚本

从 Agent 本地会话数据库（默认 Hermes 的 ~/.hermes/state.db）逐条导出真实对话原文，
用于「AI交接班三件套」的第一步。禁止用 AI 摘要冒充档案原件。

用法：
  # 列出某天的会话（找到 session_id）
  python3 export_transcript.py --list --date 2026-08-26

  # 列出最近 10 个会话（不带日期）
  python3 export_transcript.py --list

  # 全量导出指定会话到 markdown 文件
  python3 export_transcript.py --session <session_id> -o 对话全记录.md

  # 指定其他数据库路径（适配其他 Agent 时）
  python3 export_transcript.py --list --db ~/other-agent/sessions.db

表结构假设（Hermes state.db 实测）：
  sessions(id TEXT PK, source TEXT, started_at REAL, ended_at REAL,
           title TEXT?, message_count INTEGER)
  messages(id INTEGER PK, session_id TEXT, role TEXT, content TEXT,
           timestamp REAL, active INTEGER DEFAULT 1)

若你的数据库列名不同，改 SQL 即可，机制不变。
"""

import argparse
import datetime
import os
import sqlite3
import sys

DEFAULT_DB = "~/.hermes/state.db"
TRUNCATE_LIMIT = 0


def open_db(db_path: str) -> sqlite3.Connection:
    path = os.path.expanduser(db_path)
    if not os.path.exists(path):
        sys.exit(f"[错误] 数据库不存在: {path}")
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)  # 只读打开，绝不写库
    return conn


def fmt_ts(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def day_range(date_str: str):
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    start = d.timestamp()
    end = (d + datetime.timedelta(days=1)).timestamp()
    return start, end


def list_sessions(conn: sqlite3.Connection, date_str=None, source=None, limit=10):
    cur = conn.cursor()
    sql = "SELECT id, source, started_at, ended_at, title, message_count FROM sessions"
    conds, params = [], []
    if date_str:
        s, e = day_range(date_str)
        conds.append("started_at >= ? AND started_at < ?")
        params += [s, e]
    if source:
        conds.append("source = ?")
        params.append(source)
    if conds:
        sql += " WHERE " + " AND ".join(conds)
    sql += " ORDER BY started_at DESC LIMIT ?"
    params.append(limit)
    try:
        cur.execute(sql, params)
    except sqlite3.OperationalError as e:
        sys.exit(f"[错误] 查询失败（你的库结构可能不同，请按文件头注释改SQL）: {e}")
    rows = cur.fetchall()
    if not rows:
        print("(没有符合条件的会话)")
        return
    print(f"{'session_id':<24} {'开始时间':<20} {'来源':<8} {'消息数':>4}  标题")
    for sid, src, st, ed, title, mc in rows:
        t = (title or "")[:30].replace("\n", " ")
        print(f"{sid:<24} {fmt_ts(st):<20} {src or '-':<8} {mc or 0:>4}  {t}")


def export_session(conn: sqlite3.Connection, session_id: str, out_path: str,
                   max_chars=TRUNCATE_LIMIT, active_only=False):
    cur = conn.cursor()
    # 会话元信息
    cur.execute("SELECT started_at, ended_at FROM sessions WHERE id = ?", (session_id,))
    meta = cur.fetchone()
    if not meta:
        sys.exit(f"[错误] 找不到 session: {session_id}（先用 --list 确认 id）")

    # 真实消息：user/assistant 全部原文，按 id 升序
    #
    # 不要用 active = 1 过滤：上下文压缩会把已压缩的老消息标成 active = 0，
    # 但那些仍是被压缩前的真实原文，全记录必须保留。
    # （2026-09-11 实战教训：某会话按 active=1 只导出 34 条，实际原文 159 条。）
    # 只排除 _compressed_summary = 1 的行——那是压缩生成给模型看的 AI 摘要，不是原文。
    base_sql = ("SELECT role, content, timestamp FROM messages "
                "WHERE session_id = ? AND role IN ('user','assistant') ")
    if active_only:
        base_sql += "AND active = 1 "
    try:
        cur.execute(base_sql + "AND COALESCE(_compressed_summary, 0) = 0 ORDER BY id ASC",
                    (session_id,))
    except sqlite3.OperationalError:
        # 老库可能没有 _compressed_summary / active 列，退回最小过滤（尽力而为）
        try:
            cur.execute(
                "SELECT role, content, timestamp FROM messages "
                "WHERE session_id = ? AND role IN ('user','assistant') ORDER BY id ASC",
                (session_id,),
            )
        except sqlite3.OperationalError as e:
            sys.exit(f"[错误] 查询失败（检查 messages 表结构）: {e}")

    rows = cur.fetchall()
    if not rows:
        sys.exit("[错误] 该会话没有可导出的 user/assistant 消息")

    # 过滤空消息（纯工具调用轮次的占位消息，正文不在 content 里）
    skipped_empty = 0
    filtered = []
    for role, content, ts in rows:
        if not (content or "").strip():
            skipped_empty += 1
            continue
        filtered.append((role, content, ts))
    if not filtered:
        sys.exit("[错误] 该会话没有可导出的非空 user/assistant 消息")
    rows = filtered

    label = {"user": "用户", "assistant": "助手"}
    truncated_n = 0
    body_lines = []
    for i, (role, content, ts) in enumerate(rows, 1):
        text = content or ""
        if max_chars and len(text) > max_chars:
            text = text[:max_chars] + "\n[已截断]"
            truncated_n += 1
        head = f"## {label.get(role, role)}（第{i}条 · {fmt_ts(ts)}）"
        body_lines += [head, "", text.strip(), ""]
    if truncated_n:
        body_lines.append(f"---\n注：{truncated_n} 条消息超长已截断至前 {max_chars} 字。原始内容仍在数据库中，未丢失。")

    trunc_note = (f"{truncated_n} 条超长已截断（单条上限 {max_chars} 字符）"
                  if truncated_n else "无")
    lines = [
        "# 对话全记录",
        "",
        f"> session_id: {session_id}",
        f"> 起止时间: {fmt_ts(meta[0])} ~ {fmt_ts(meta[1]) if meta[1] else '进行中'}",
        f"> 消息数: {len(rows)} 条（user/assistant 非空原文；已过滤工具输出、空占位、压缩摘要行）",
        f"> 导出时间: {fmt_ts(datetime.datetime.now().timestamp())}",
        f"> 导出方式: SQLite 直读逐条导出，非AI摘要",
        f"> 截断: {trunc_note}",
        "",
    ] + body_lines

    out = os.path.expanduser(out_path)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    size_kb = os.path.getsize(out) / 1024
    print(f"[完成] 导出 {len(rows)} 条消息 → {out}（{size_kb:.1f} KB，截断 {truncated_n} 条）")


def main():
    ap = argparse.ArgumentParser(description="AI交接班·对话全记录导出（数据库直读，非摘要）")
    ap.add_argument("--db", default=DEFAULT_DB, help=f"会话数据库路径（默认 {DEFAULT_DB}）")
    ap.add_argument("--list", action="store_true", help="列出会话")
    ap.add_argument("--date", help="筛选日期 YYYY-MM-DD（配合 --list）")
    ap.add_argument("--source", help="筛选来源 cli/cron/feishu/telegram（配合 --list）")
    ap.add_argument("--limit", type=int, default=10, help="--list 返回条数（默认10）")
    ap.add_argument("--session", help="要导出的 session_id")
    ap.add_argument("-o", "--output", help="输出 markdown 路径")
    ap.add_argument("--max-chars", type=int, default=TRUNCATE_LIMIT,
                    help="单条消息截断阈值；默认0表示不截断")
    ap.add_argument("--active-only", action="store_true",
                    help="只导出当前活跃上下文（旧行为）；默认导出全部原文，含被上下文压缩的老消息")
    args = ap.parse_args()

    conn = open_db(args.db)
    try:
        if args.list or (not args.session and not args.output):
            list_sessions(conn, args.date, args.source, args.limit)
        elif args.session:
            out = args.output or f"./对话全记录_{args.session[:12]}.md"
            export_session(conn, args.session, out, args.max_chars, args.active_only)
        else:
            sys.exit("[错误] 导出需要 --session <id> 和 -o 输出路径")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
