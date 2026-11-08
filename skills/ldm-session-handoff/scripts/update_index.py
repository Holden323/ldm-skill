#!/usr/bin/env python3
"""把这次交接写进存档根目录的会话索引（session_index.json：{日期: [条目, …]}）。同一会话 id 再写会覆盖旧条目；改前自动备份。

  python3 -B update_index.py --record <对话全记录.md> --router <路由器.md> --title "<一句话：做了什么、停在哪>"

会话 id、起止时间、消息数、平台从全记录文件头读；读不到的用参数补（--id --started --ended --source --msg-count）。
索引位置：--index 指定；否则取全记录所在日期目录的上一层的 session_index.json。那里没有索引就什么都不做（说明这个存档根不用索引）。
"""
import argparse, datetime, json, os, re, shutil, sys


def head(text, *keys):
    for k in keys:
        m = re.search(rf'^>\s*{k}\s*[:：]\s*(.+)$', text, re.M)
        if m: return m.group(1).strip()
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--record', required=True); ap.add_argument('--router', required=True); ap.add_argument('--title', required=True)
    ap.add_argument('--index'); ap.add_argument('--date'); ap.add_argument('--id'); ap.add_argument('--started'); ap.add_argument('--ended')
    ap.add_argument('--source'); ap.add_argument('--msg-count', type=int)
    a = ap.parse_args()
    rec = os.path.abspath(a.record); day_dir = os.path.dirname(rec)
    idx = a.index or os.path.join(os.path.dirname(day_dir), 'session_index.json')
    if not os.path.exists(idx): print(f'[索引] 没有 {idx}，这个存档根不用索引，跳过'); return
    t = open(rec, encoding='utf-8').read()
    span = head(t, '起止时间') or ''
    s0, _, s1 = span.partition('~')
    src = head(t, '源文件', '会话标识') or ''
    sid = a.id or (os.path.splitext(os.path.basename(src))[0] if src else None)
    backend = head(t, '后端', '平台') or ''
    source = a.source or ('claude-code' if 'Claude' in backend else 'codex' if 'Codex' in backend else 'workbuddy' if 'WorkBuddy' in backend
                          else 'dsh' if 'DSH' in backend else 'hermes' if ('SQLite' in t[:600] or 'Hermes' in backend) else backend or 'unknown')
    m = re.search(r'(\d+)', head(t, '消息数') or ''); mc = a.msg_count or (int(m.group(1)) if m else 0)
    if not sid: sys.exit('[索引] 读不到会话 id，用 --id 补')
    date = a.date or os.path.basename(day_dir)
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date): sys.exit(f'[索引] 全记录不在「YYYY-MM-DD」日期目录里（{day_dir}），用 --date 指定')
    e = {'id': f'{source}-{sid}' if not sid.startswith(source) else sid, 'started': a.started or s0.strip()[:16], 'ended': a.ended or s1.strip()[:16],
         'title': a.title, 'source': source, 'msg_count': mc, 'router_file': os.path.basename(a.router), 'record_file': os.path.basename(rec), 'has_record': True}
    d = json.load(open(idx, encoding='utf-8'))
    shutil.copy(idx, idx + '.bak_' + datetime.datetime.now().strftime('%Y%m%d_%H%M'))
    L = d.setdefault(date, []); old = len(L); L[:] = [x for x in L if x.get('id') != e['id']] + [e]
    json.dump(d, open(idx, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'[索引] {"覆盖" if len(L) == old else "新增"} {date} 一条：{e["id"]}（{mc} 条消息）→ {idx}')


if __name__ == '__main__':
    main()
