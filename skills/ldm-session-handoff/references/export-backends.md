# 会话原文导出后端

只有需要选择、运行或排查导出方式时读取。优先使用平台提供的完整原文导出能力；没有合适能力时再使用脚本。

## Hermes

Hermes 会话位于 SQLite 数据库时：

```bash
python3 scripts/export_transcript.py --list --date <YYYY-MM-DD>
python3 scripts/export_transcript.py --session <session_id> -o <输出文件.md>
```

默认数据库为 `~/.hermes/state.db`。数据库结构变化时先只读检查表结构，不修改原库。

**找会话 id 先跑 `scripts/find_session.py`**（直接查 state.db，结果确定，不受 FTS 分词影响）：`--latest` 查当前或最近一次会话，`--days N` 列出窗口内的会话，`--grep 关键词` 按消息正文 LIKE 反查。活跃会话不出现在 `export_transcript.py --list` 里，也照这样找。

- **session_search 是 FTS5，中文长词、带连字符的词会静默 0 命中**（2026-11-06 实测）：`'巨幅石刻壁画'` 0 命中；`'G2-2'` 被当成列过滤语法，报错后被吞成 0；`'州桥'` 却能命中。所以 0 命中 ≠ 会话不存在，下结论前用 `find_session.py --grep` 或 SQL LIKE 复核。非要用的话，只搜 2–4 字、大概率被标点隔开的短词。
- **不要按 `active = 1` 过滤**：上下文压缩会把老消息标成 `active = 0`，但它们仍是真实原文（实测按 active 过滤只剩 34/162 条）。只排除 `_compressed_summary = 1`（压缩生成的 AI 摘要）。确实只要当前上下文时用 `--active-only`。
- 上下文重建会把历史整块重插。脚本已去重：连续 3 条以上同序同文的块整块剔除；助手重复的长文只留第一次。用户消息不做全局去重（连发「1」是真实对话）。文件头写明两类各剔除多少。

## Claude Code

```bash
python3 scripts/export_jsonl_transcript.py --list --agent claude --date <YYYY-MM-DD>
python3 scripts/export_jsonl_transcript.py --agent claude --session <session_id> -o <输出文件.md>
```

默认从 `~/.claude/projects/` 查找 JSONL；同时查 `$CLAUDE_CONFIG_DIR/projects/` 和 `~/.claude-*/projects/`。本机有多套配置时（例如 `CLAUDE_CONFIG_DIR=~/.claude-2`），当前会话在哪一套，看文件头的「源文件」。

执行中途插入的用户消息存为 `attachment.type=queued_command`，脚本按时间顺序收入（其他窗口发来的跨会话消息过滤）；上下文压缩摘要（`isCompactSummary`）剔除。文件头注记会写明各自条数。

## Codex

```bash
python3 scripts/export_jsonl_transcript.py --list --agent codex --date <YYYY-MM-DD>
python3 scripts/export_jsonl_transcript.py --agent codex --session <rollout 路径或唯一片段> -o <输出文件.md>
```

默认从 `~/.codex/sessions/YYYY/MM/DD/` 查找 rollout JSONL。若当前平台提供原生线程读取或导出，优先使用平台能力，避免依赖内部格式。

## WorkBuddy

```bash
python3 scripts/export_workbuddy_transcript.py --list
python3 scripts/export_workbuddy_transcript.py --list --date <YYYY-MM-DD> --project "<工作目录片段>"
python3 scripts/export_workbuddy_transcript.py --session <session_id> -o <输出文件.md>
```

会话位于：

```
~/.workbuddy-ai/projects/<工作目录编码>/<sessionId>.jsonl
```

工作目录编码规则：绝对路径里的 `/` 和空格都换成 `-`。

与 Claude Code / Codex 的差别：

- **当前活跃会话会出现在 `--list` 里**，直接取 sessionId 导出，不需要绕 `session_search`。
- 时间戳是**毫秒**，不是秒。
- user 消息里塞了整段环境注入，真正的用户输入在 `<user_query>...</user_query>` 中。脚本优先取 user_query，取不到就剥 `system-reminder` 等标签。
- 一个 jsonl 里混着 `message` / `reasoning` / `function_call` / `function_call_result` / `session-meta` / `file-history-snapshot` / `ai-title`，只有 `message` 是原文。

跑脚本时加 `-B` 或设 `PYTHONDONTWRITEBYTECODE=1`，避免在仓库里生成 `__pycache__`。

## DSH（DeepSeek Harness）

```bash
node scripts/export_dsh_session.js <session.v4.jsonl.zstd> <原始.jsonl>
python3 scripts/export_dsh_transcript.py <原始.jsonl> <对话全记录.md> [会话id] [工作目录] [帧数]
```

- 会话位置：`~/.dsh/sessions/<工作区目录名>/<session-id>/session.v4.jsonl.zstd`。当前会话 id 读环境变量 `DSH_SESSION_ID`。
- 会话文件是**多帧拼接的 zstd**。`zstdDecompressSync` 只能解出第一帧（1.37 MB 的文件只解出 237 字节），必须逐帧循环解压，脚本已处理。实测 1.37 MB → 914 帧 → 1493 行 JSONL → 88 条可见消息。
- 事件类型：`user/message`（data.content[].text）、`assistant/message`（data.message.content[].text，里面的 reasoning、tool-call 要过滤）；tool/result、request/*、step/* 一律不导出。

## 失败处理

- 用户要求导出时，不要以「当前会话还在进行」为由放弃。每个后端都能导出活跃会话，先把本页对应的找会话办法试完；都失败了，再如实报告已拿到的范围，标「待补存」。

- 找不到会话：列出候选会话并核对日期、平台和工作目录。
- 多个结果命中：不要静默猜测；缩小到唯一标识。
- 格式变化：先用 `--inspect <文件>` 查看记录类型分布，再修改解析器。
- 无法完整导出：报告已获得的范围并标记“待补存”，不要生成伪原文。
