#!/usr/bin/env python3
"""交接完成检查：路由器（和可选的重启提示语）里写的路径能不能长期用，必备小节在不在。

  python3 -B check_handoff.py <路由器.md> [--prompt <重启提示语.txt>] [--record <对话全记录.md>]

查这些，任何一条不过退出码 1：
  1. 每个绝对路径都存在（路径里夹着全角逗号、括号时，取最长的存在前缀）
  2. 没有临时位置（/tmp、/private/tmp、/var/folders、scratchpad、tmp 开头的会话目录）——这些会被清，换到长期目录再引用
  3. 没有 ~ 开头的路径（不算绝对路径）
  4. 路由器有「新会话必守」「当前进度与下一步」小节；重启提示语有「本窗口」范围
  5. 给了 --record 时：文件头消息数＝正文「## 用户」「## 助手」条数，文件头有「打码」行
只输出事实，不判断写得好不好。
"""
import argparse, os, re, sys

TEMP = re.compile(r'^(/tmp/|/private/tmp/|/var/folders/|/private/var/folders/)|/scratchpad(/|$)')
RUN = re.compile(r'(?<![\w/~.])(/(?:Users|home|private|tmp|var|opt|Volumes|mnt|srv|data)/[^\s`|<>\]\)"\'*]+)')
CUT = set('（）()，。、；：」「』『！？,;')


def paths_in(text):
    out = []
    for m in RUN.finditer(text):
        raw = m.group(1).rstrip('.:,;')
        if '<' in raw or '{' in raw or '…' in raw: continue   # 模板占位、省略号路径不查
        cuts = [len(raw)] + [i for i in range(len(raw) - 1, 0, -1) if raw[i] in CUT]
        hit = next((raw[:c].rstrip('/') for c in cuts if os.path.exists(raw[:c].rstrip('/'))), None)
        out.append((hit or raw[:min(cuts)], bool(hit)))
    return out


def check_paths(text, where, bad):
    seen = set()
    for p, ok in paths_in(text):
        if p in seen: continue
        seen.add(p)
        if TEMP.search(p): bad.append(f'{where}：临时位置会被清，换到长期目录再引用：{p}')
        elif not ok: bad.append(f'{where}：路径不存在：{p}')
    for m in re.finditer(r'(?<![\w/])~/[^\s`|）)，。]+', text): bad.append(f'{where}：「~」不是绝对路径：{m.group(0)}')
    return len(seen)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('router'); ap.add_argument('--prompt'); ap.add_argument('--record')
    a = ap.parse_args(); bad = []
    r = open(a.router, encoding='utf-8').read()
    n = check_paths(r, '路由器', bad)
    for sec in ('新会话必守', '当前进度与下一步'):
        if not re.search(rf'^##\s*{sec}', r, re.M): bad.append(f'路由器：缺「## {sec}」小节')
    if a.prompt:
        p = open(a.prompt, encoding='utf-8').read(); n += check_paths(p, '重启提示语', bad)
        if '本窗口' not in p: bad.append('重启提示语：没写「本窗口」做到哪、停在哪')
    if a.record:
        t = open(a.record, encoding='utf-8').read()
        m = re.search(r'消息数[:：]\s*(\d+)', t); u = len(re.findall(r'^## 用户', t, re.M)); s = len(re.findall(r'^## 助手', t, re.M))
        if not m: bad.append('全记录：文件头没有消息数')
        elif int(m.group(1)) != u + s: bad.append(f'全记录：文件头消息数 {m.group(1)}，正文 用户 {u} + 助手 {s} = {u + s}，对不上')
        if '> 打码：' not in t: bad.append('全记录：文件头没有「打码」行（导出后没跑 redact_secrets.py）')
    print(f'[交接检查] 查了 {n} 个路径，问题 {len(bad)} 处')
    for b in bad: print('  ✗', b)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
