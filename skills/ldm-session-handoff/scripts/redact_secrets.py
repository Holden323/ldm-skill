#!/usr/bin/env python3
"""给导出的对话全记录打码：把常见格式的密钥、令牌替换成「[已打码:类型]」，并在文件头写一行「> 打码：…」。

导出脚本写完文件后会自动调用；也可以单独跑：
  python3 -B redact_secrets.py <对话全记录.md>            打码并改写文件
  python3 -B redact_secrets.py <对话全记录.md> --check    只报告，不改文件（有命中时退出码 1）

只认格式明确的密钥。「password = …」这类泛匹配会误伤，单独标成「候选」，不打码，只提示人工看一眼。
"""
import argparse, re, sys

PATTERNS = [
    ('github_token', r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b'),
    ('github_pat', r'\bgithub_pat_[A-Za-z0-9_]{60,}\b'),
    ('anthropic_key', r'\bsk-ant-[A-Za-z0-9_\-]{20,}'),
    ('openai_key', r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_\-]{32,}'),
    ('aws_access_key', r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b'),
    ('slack_token', r'\bxox[abposr]-[A-Za-z0-9\-]{10,}'),
    ('google_api_key', r'\bAIza[0-9A-Za-z_\-]{35}\b'),
    ('private_key', r'-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----'),
    ('bearer_token', r'(?i)\bBearer\s+[A-Za-z0-9_\-\.=]{30,}'),
]
CANDIDATE = re.compile(r'(?i)\b(?:api[_-]?key|secret|token|passwd|password)\s*[:=]\s*["\']?([A-Za-z0-9_\-\.]{16,})')


def redact_text(text):
    counts = {}
    for name, pat in PATTERNS:
        text, n = re.subn(pat, f'[已打码:{name}]', text)
        if n: counts[name] = n
    cands = [m.group(0)[:24] + '…' for m in CANDIDATE.finditer(text) if '已打码' not in m.group(0)]
    return text, counts, cands


def header_line(counts):
    return '> 打码：' + ('、'.join(f'{k}×{v}' for k, v in counts.items()) if counts else '无（按常见密钥格式扫描）')


def redact_file(path, check=False):
    text = open(path, encoding='utf-8').read()
    new, counts, cands = redact_text(text)
    if not check:
        lines = new.split('\n')
        lines = [l for l in lines if not l.startswith('> 打码：')]
        last_meta = max((i for i, l in enumerate(lines[:40]) if l.startswith('>')), default=None)   # 写在文件头最后一行「>」之后
        if last_meta is None: lines[1:1] = ['', header_line(counts)]
        else: lines.insert(last_meta + 1, header_line(counts))
        open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    msg = f'[打码] {sum(counts.values())} 处' + (f'（{"、".join(f"{k}×{v}" for k, v in counts.items())}）' if counts else '')
    if cands: msg += f'；另有 {len(cands)} 处候选（像密钥赋值，没打码，请人工看）：' + '；'.join(cands[:5])
    print(msg)
    return counts, cands


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('file'); ap.add_argument('--check', action='store_true', help='只报告不改文件')
    a = ap.parse_args()
    counts, cands = redact_file(a.file, a.check)
    sys.exit(1 if a.check and counts else 0)


if __name__ == '__main__':
    main()
