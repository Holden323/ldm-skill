import json, sys, os, datetime
src, dst = sys.argv[1], sys.argv[2]
# 可选参数：会话标识、会话工作目录、zstd 帧数。
# 不传时从环境变量 DSH_SESSION_ID 和当前目录推断；帧数取不到就不写。
SESSION_ID = sys.argv[3] if len(sys.argv) > 3 else os.environ.get('DSH_SESSION_ID', '（未知，导出时未提供，待补）')
WORKSPACE = sys.argv[4] if len(sys.argv) > 4 else os.getcwd()
FRAMES = sys.argv[5] if len(sys.argv) > 5 else ''
EXPORTED_AT = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
SKIP_PREFIX = ('Current runtime context', 'Background subagent', 'Agent ', 'Its closing message', 'Current runtime')
rows, skipped = [], 0
for line in open(src, encoding='utf-8'):
    line = line.strip()
    if not line: continue
    try: o = json.loads(line)
    except: continue
    if o.get('type') not in ('user/message', 'assistant/message'): continue
    ts = o.get('time')
    when = datetime.datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S') if isinstance(ts,(int,float)) else ''
    d = o.get('data') or {}
    if o['type'] == 'user/message':
        parts = [c.get('text','') for c in d.get('content',[]) if c.get('type')=='text']
        who = '用户'
    else:
        msg = d.get('message') or {}
        parts = [c.get('text','') for c in msg.get('content',[]) if c.get('type')=='text']
        who = '助手'
    text = '\n'.join(p for p in parts if p and p.strip()).strip()
    if not text: continue
    # 过滤环境注入 / 子 agent 消息
    if who == '用户' and text.startswith(SKIP_PREFIX):
        skipped += 1; continue
    if who == '用户' and text.startswith('【事实核查回报') :
        pass  # 子 agent 回报保留，属于会话内容
    rows.append((when, who, text))
with open(dst, 'w', encoding='utf-8') as f:
    f.write('# 对话全记录\n\n')
    f.write('> 平台：DSH（DeepSeek Harness）Web GUI\n')
    f.write(f'> 会话标识：{SESSION_ID}\n')
    f.write(f'> 会话工作目录：{WORKSPACE}\n')
    f.write(f'> 起止时间：{rows[0][0]} ~ {rows[-1][0]}（导出时会话仍在进行）\n')
    f.write(f'> 消息数：{len(rows)} 条（用户 {sum(1 for r in rows if r[1]=="用户")} / 助手 {sum(1 for r in rows if r[1]=="助手")}），另过滤环境注入 {skipped} 条\n')
    f.write(f'> 导出时间：{EXPORTED_AT}\n')
    f.write(f'> 导出方式：DSH 会话存储 JSONL 直读（session.v4.jsonl.zstd{"，" + FRAMES + " 帧逐帧解压" if FRAMES else " 逐帧解压"}），非 AI 摘要\n')
    f.write('> 过滤说明：只保留 user 可见输入与 assistant 可见文本；工具调用、工具输出、推理记录、环境注入（runtime context 等）已过滤\n')
    f.write('> 截断：无\n\n---\n\n')
    for when, who, text in rows:
        f.write(f'## {who}｜{when}\n\n{text}\n\n')
print('保留', len(rows), '条，过滤环境注入', skipped, '条')
print('起', rows[0][0], '止', rows[-1][0])
