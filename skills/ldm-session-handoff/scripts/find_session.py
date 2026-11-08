#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 ~/.hermes/state.db 直接定位会话 id，绕开 session_search 的 FTS 中文分词坑。

用法（在 ldm-session-handoff skill 的 scripts/ 目录，python3 -B 运行）：
  python3 -B find_session.py                # 列最近 7 天非 cron 会话
  python3 -B find_session.py --days 2       # 列最近 2 天
  python3 -B find_session.py --latest       # 只打印最近一个非 cron 会话的 id（供 export_transcript.py 用）
  python3 -B find_session.py --grep 巨幅石刻  # 在消息正文里 LIKE 检索，反查命中会话（中文兜底）
  python3 -B find_session.py --all          # 含 cron 会话

为什么需要它：session_search 走 FTS5，中文按「标点/ASCII 切分的整段」建词元，
长词查询（如「巨幅石刻壁画」）和带连字符的词（如「G2-2」会触发 FTS 语法错误）经常 0 命中
且不报错。找「当前/最近会话」用本脚本是确定性的；历史内容回忆再用 session_search（挑短词）。
"""
import argparse
import datetime
import os
import sqlite3
import sys

DB_PATH = os.path.expanduser("~/.hermes/state.db")


def fmt_ts(ts):
    if not ts:
        return "-"
    return datetime.datetime.fromtimestamp(ts).strftime("%m-%d %H:%M")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--latest", action="store_true")
    ap.add_argument("--grep", type=str, default=None)
    ap.add_argument("--all", action="store_true", help="包含 cron 会话")
    args = ap.parse_args()

    if not os.path.exists(DB_PATH):
        print(f"找不到 {DB_PATH}", file=sys.stderr)
        return 1

    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

    if args.grep:
        like = f"%{args.grep}%"
        rows = db.execute(
            """SELECT s.id, s.title, s.source, COUNT(m.id) AS hits,
                      MIN(m.timestamp), MAX(m.timestamp)
               FROM messages m JOIN sessions s ON s.id = m.session_id
               WHERE m.content LIKE ?
               GROUP BY s.id ORDER BY MAX(m.timestamp) DESC LIMIT 15""",
            (like,),
        ).fetchall()
        if not rows:
            print(f"LIKE {like!r} 0 命中（确认字串真实存在于原文；FTS 坑勿用 session_search 下结论）")
            return 0
        for sid, title, source, hits, t0, t1 in rows:
            print(f"{sid}  命中{hits}条  [{source}] {fmt_ts(t0)}~{fmt_ts(t1)}  {title or 'untitled'}")
        return 0

    since = datetime.datetime.now().timestamp() - args.days * 86400
    sql = ("SELECT id, title, source, message_count, started_at, last_activity_at "
           "FROM sessions WHERE started_at >= ?")
    if not args.all:
        sql += " AND source != 'cron'"
    sql += " ORDER BY started_at DESC LIMIT 30"
    rows = db.execute(sql, (since,)).fetchall()

    if args.latest:
        if rows:
            print(rows[0][0])
        else:
            print("近窗口内无非 cron 会话", file=sys.stderr)
            return 1
        return 0

    if not rows:
        print(f"最近 {args.days} 天无匹配会话")
        return 0
    for sid, title, source, mc, t0, t1 in rows:
        print(f"{sid}\n    [{source}] msg{mc}  {fmt_ts(t0)} → {fmt_ts(t1)}  {title or 'untitled'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
