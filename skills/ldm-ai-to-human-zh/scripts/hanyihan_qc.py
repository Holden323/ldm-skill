#!/usr/bin/env python3
"""
汉译汉机械信号扫描器
用法：python3 hanyihan_qc.py <文章路径>
示例：python3 hanyihan_qc.py /path/to/article.md

检查项用于发现候选信号，不能脱离体裁和语境判定文章质量：
  1. 禁令句式（不是X而是Y、你以为X其实Y等）
  2. AI高频词 / 广告腔 / 学术报告腔
  3. 破折号
  4. 英文词
  5. 段落长度（每段>3句标记）
  6. 加粗金句密度
  7. 加粗金句单独成段
  8. 短句堆砌（连续相似短句，警告项）
  9. 伪装精确数字（1.7秒、2.3%等）
 10. 字数统计（仅报告，不设阈值）
"""

import sys
import re
import os


def count_chinese(text):
    """统计中文字符数"""
    return len(re.findall(r'[\u4e00-\u9fff]', text))


def load_file(path):
    """读取文件，返回(全文, 正文去掉标题, 行列表)"""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    body_lines = [l for l in lines if not l.startswith('# ') and l.strip()]
    body = '\n'.join(body_lines)
    return content, body, lines


# ============================================================
# 检查函数
# ============================================================

def check_forbidden_patterns(body):
    """禁令句式扫描（含变体）"""
    issues = []
    patterns = [
        (r'不是[^，。]{1,30}[，,]是[^。]+', '不是X，是Y'),
        (r'不是[^，。]{1,30}[，,]而是[^。]+', '不是X，而是Y'),
        (r'不是[^，。]{1,30}[，,]只是[^。]+', '不是X，只是Y'),
        (r'你以为[^，。]+[，,]其实[^。]+', '你以为X，其实Y'),
        (r'你不需要[^，。]+[，,]你只需要[^。]+', '你不需要X，你只需要Y'),
        (r'不在于[^，。]+[，,]而在于[^。]+', '不在于X，而在于Y'),
        (r'而不是[^，。！？\n]{2,}', '而不是...'),
        (r'我见过太多', '我见过太多——AI没有眼睛，没见过任何东西'),
        (r'我经历过', '我经历过——AI没有身体，没有经历'),
        (r'我身边就有', '我身边就有——AI没有身边的人'),
        # 变体：句号断开的禁令
        (r'不是[^。]+。恰恰相反[，]?', '不是X。恰恰相反Y'),
        (r'你以为[^。]+。其实[^。]*', '你以为X。其实Y'),
    ]
    for i, line in enumerate(body.split('\n')):
        l = line.strip()
        if not l or l.startswith('#'):
            continue
        for pat, name in patterns:
            if re.search(pat, l) and count_chinese(l) > 10:
                issues.append(f"  行{i+1} [{name}]: {l[:60]}")
    return issues


def check_ai_words(body):
    """AI高频词 / 广告腔 / 学术报告腔"""
    issues = []
    ai_words = [
        '此外', '事实上', '值得注意的是', '然而', '本质上', '归根结底',
        '至关重要', '关键作用', '充满活力的', '格局',
        '值得一提', '需要指出', '不难发现', '众所周知', '毋庸置疑',
        '综上所述', '由此可见',
    ]
    ad_words = [
        '赋能', '痛点', '闭环', '抓手', '颗粒度', '赛道',
        '差异化', '产品定位', '反常识的规律',
    ]
    academic_words = [
        '选择疲劳', '出厂设置', '深层需求', '情绪价值',
        '社交APP的死结',
    ]
    all_words = [(w, 'AI词') for w in ai_words] + \
                [(w, '商业词') for w in ad_words] + \
                [(w, '学术词') for w in academic_words]
    for w, cat in all_words:
        if w in body:
            issues.append(f"  [{cat}] {w}")
    return issues


def check_dashes(body):
    """破折号检查"""
    issues = []
    for i, line in enumerate(body.split('\n')):
        if '——' in line:
            issues.append(f"  行{i+1}: 破折号「——」→ 改为句号或逗号")
    return issues


def check_english_words(body):
    """英文词检查"""
    issues = []
    allowed = {'ok', 'vs', 'ai', 'app', 'pdf', 'csv', 'xlsx', 'md', 'py', 'sh', 'mb', 'gb'}
    for i, line in enumerate(body.split('\n')):
        l = line.strip()
        if l.startswith('#') or l.startswith('```') or 'http' in l:
            continue
        words = re.findall(r'\b[a-zA-Z]{3,}\b', l)
        for w in words:
            if w.lower() in allowed:
                continue
            issues.append(f"  行{i+1}: 英文词「{w}」→ 翻译成中文")
    return issues


def check_paragraph_length(body):
    """段落长度检查（>3句标记）"""
    issues = []
    paragraphs = body.split('\n\n')
    for idx, para in enumerate(paragraphs):
        para = para.strip()
        if not para or para.startswith('#') or para.startswith('---') or para.startswith('|'):
            continue
        sentence_count = len(re.findall(r'[。！？]', para))
        if sentence_count > 3:
            preview = para[:25].replace('\n', ' ')
            issues.append(f"  第{idx+1}段（{preview}...）：{sentence_count}句，建议拆成1-3句/段")
    return issues


def check_bold_density(body):
    """加粗金句密度检查"""
    issues = []
    cc = count_chinese(body)
    bold_matches = re.findall(r'\*\*[^*]+\*\*', body)
    bold_count = len(bold_matches)
    if cc > 0 and bold_count > 0:
        interval = cc / bold_count
        if interval < 400:
            issues.append(f"  加粗{bold_count}个，间隔{interval:.0f}字，过密（建议600-800字/个）")
        elif interval > 1200:
            issues.append(f"  加粗{bold_count}个，间隔{interval:.0f}字，偏低（建议600-800字/个）")
    elif cc > 500 and bold_count == 0:
        issues.append(f"  没有加粗金句（500字以上建议至少1个）")
    return issues, bold_count


def check_bold_standalone(body):
    """加粗金句单独成段检查"""
    issues = []
    paragraphs = body.split('\n\n')
    for idx, para in enumerate(paragraphs):
        para = para.strip()
        if re.match(r'^\*\*[^*]+\*\*$', para):
            preview = para[:30]
            issues.append(f"  第{idx+1}段：加粗单独成段「{preview}」→ 融入正文段落")
    return issues


def check_short_sentence_stacking(body):
    """短句堆砌检查（警告项，需人工判断）"""
    issues = []
    sentences = re.split(r'[。！？]', body)
    sentences = [s.strip() for s in sentences if s.strip()]
    consecutive_short = []
    for s in sentences:
        cc = count_chinese(s)
        if cc < 15:
            consecutive_short.append(s)
        else:
            if len(consecutive_short) >= 3:
                ccs = [count_chinese(x) for x in consecutive_short]
                avg = sum(ccs) / len(ccs)
                variance = sum((c - avg)**2 for c in ccs) / len(ccs)
                # 检查是否是排比/列举（有重复结构）
                texts = consecutive_short
                has_pattern = False
                for j in range(len(texts)-1):
                    if len(texts[j]) >= 3 and len(texts[j+1]) >= 3:
                        if texts[j][:3] == texts[j+1][:3] or texts[j][-3:] == texts[j+1][-3:]:
                            has_pattern = True
                            break
                if variance < 20 and avg < 12 and not has_pattern:
                    sample = '。'.join(texts[:3]) + '。'
                    issues.append(f"  连续{len(consecutive_short)}句相似短句(均{avg:.0f}字): {sample[:60]}...")
            consecutive_short = []
    # 末尾
    if len(consecutive_short) >= 3:
        ccs = [count_chinese(x) for x in consecutive_short]
        avg = sum(ccs) / len(ccs)
        variance = sum((c - avg)**2 for c in ccs) / len(ccs)
        texts = consecutive_short
        has_pattern = False
        for j in range(len(texts)-1):
            if len(texts[j]) >= 3 and len(texts[j+1]) >= 3:
                if texts[j][:3] == texts[j+1][:3] or texts[j][-3:] == texts[j+1][-3:]:
                    has_pattern = True
                    break
        if variance < 20 and avg < 12 and not has_pattern:
            sample = '。'.join(texts[:3]) + '。'
            issues.append(f"  连续{len(consecutive_short)}句相似短句(均{avg:.0f}字): {sample[:60]}...")
    return issues


def check_precise_numbers(body):
    """伪装精确数字检查（1.7秒、2.3%等）"""
    issues = []
    pattern = re.compile(r'\d+\.\d+\s*(?:秒|分钟|小时|天|%|倍|次|个|元|块)')
    for i, line in enumerate(body.split('\n')):
        for match in pattern.finditer(line):
            issues.append(
                f"  行{i+1}: 「{match.group(0)}」→ 确认精度是否有来源或真实观察")
    return issues


# ============================================================
# 主程序
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("用法: python3 hanyihan_qc.py <文章路径>")
        print("示例: python3 hanyihan_qc.py /path/to/article.md")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"文件不存在: {path}")
        sys.exit(1)

    content, body, lines = load_file(path)
    cc = count_chinese(body)
    filename = os.path.basename(path)

    print(f"{'='*60}")
    print(f"汉译汉机械信号报告")
    print(f"文件: {filename}")
    print(f"中文字数: {cc}")
    print(f"{'='*60}")

    total = 0

    # 1. 禁令句式
    print(f"\n【1】禁令句式")
    issues = check_forbidden_patterns(body)
    if issues:
        for i in issues: print(i)
        print(f"  → {len(issues)}处候选，结合语境判断")
        total += len(issues)
    else:
        print(f"  ✓ 通过")

    # 2. AI词汇
    print(f"\n【2】AI词汇 / 广告腔 / 学术腔")
    issues = check_ai_words(body)
    if issues:
        for i in issues: print(i)
        print(f"  → {len(issues)}处候选，结合体裁判断")
        total += len(issues)
    else:
        print(f"  ✓ 通过")

    # 3. 破折号
    print(f"\n【3】破折号")
    issues = check_dashes(body)
    if issues:
        for i in issues: print(i)
        print(f"  → {len(issues)}处候选，检查是否影响节奏")
        total += len(issues)
    else:
        print(f"  ✓ 通过")

    # 4. 英文词
    print(f"\n【4】英文词")
    issues = check_english_words(body)
    if issues:
        for i in issues: print(i)
        print(f"  → {len(issues)}处候选，专业词和专有名词可保留")
        total += len(issues)
    else:
        print(f"  ✓ 通过")

    # 5. 段落长度
    print(f"\n【5】段落长度（每段>3句）")
    issues = check_paragraph_length(content)
    if issues:
        for i in issues: print(i)
        print(f"  → {len(issues)}处较长段落，按发布体裁判断")
        total += len(issues)
    else:
        print(f"  ✓ 通过")

    # 6. 加粗密度
    print(f"\n【6】加粗金句密度")
    issues, bold_count = check_bold_density(body)
    if issues:
        for i in issues: print(i)
        total += len(issues)
    else:
        print(f"  ✓ 密度正常（{bold_count}个）")

    # 7. 加粗单独成段
    print(f"\n【7】加粗单独成段")
    issues = check_bold_standalone(body)
    if issues:
        for i in issues: print(i)
        print(f"  → {len(issues)}处")
        total += len(issues)
    else:
        print(f"  ✓ 通过")

    # 8. 短句堆砌（警告）
    print(f"\n【8】短句堆砌（⚠️ 警告，需人工判断）")
    issues = check_short_sentence_stacking(body)
    if issues:
        for i in issues: print(i)
        print(f"  → {len(issues)}处，检查是否有自然长句被句号断开")
    else:
        print(f"  ✓ 通过")

    # 9. 伪装精确数字
    print(f"\n【9】伪装精确数字")
    issues = check_precise_numbers(body)
    if issues:
        for i in issues: print(i)
        print(f"  → {len(issues)}处，确认是否真实数据")
    else:
        print(f"  ✓ 通过")

    # 总结
    print(f"\n{'='*60}")
    if total == 0:
        print(f"未发现预设机械信号")
    else:
        print(f"发现 {total} 处候选信号；请结合体裁和上下文人工判断")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
