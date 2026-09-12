# ldm-ai-to-human-zh

审查或改写中文内容，减少机械、空泛、均匀和模板化的 AI 痕迹，同时保留作者观点与语气。

## 安装

```bash
npx -y skills add Holden323/ldm-skill --skill ldm-ai-to-human-zh -g
```

## 使用

可以直接说：

- “检查这篇稿子的 AI 痕迹，只给报告。”
- “把这段改得像人话，保留原来的观点和长度。”
- “审查并改写这个文件，另存为 V2。”

Skill 会按当前请求选择审查、改写或两者都做，不会强制先停下来二次确认。

## 文件

- `SKILL.md`：Agent 使用的入口和核心流程。
- `references/editing-guide.md`：系统审稿和大幅改写时按需读取。
- `scripts/hanyihan_qc.py`：机械信号扫描器，结果需要人工结合语境判断。

自动扫描不能判断文章是否“像人”，只用于快速发现可能重复或僵硬的表达。
