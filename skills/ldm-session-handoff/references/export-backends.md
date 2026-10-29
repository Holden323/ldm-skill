# 会话原文导出后端

只有需要选择、运行或排查导出方式时读取。优先使用平台提供的完整原文导出能力；没有合适能力时再使用脚本。

## Hermes

Hermes 会话位于 SQLite 数据库时：

```bash
python3 scripts/export_transcript.py --list --date <YYYY-MM-DD>
python3 scripts/export_transcript.py --session <session_id> -o <输出文件.md>
```

默认数据库为 `~/.hermes/state.db`。数据库结构变化时先只读检查表结构，不修改原库。

## Claude Code

```bash
python3 scripts/export_jsonl_transcript.py --list --agent claude --date <YYYY-MM-DD>
python3 scripts/export_jsonl_transcript.py --agent claude --session <session_id> -o <输出文件.md>
```

默认从 `~/.claude/projects/` 查找 JSONL。

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

## 失败处理

- 找不到会话：列出候选会话并核对日期、平台和工作目录。
- 多个结果命中：不要静默猜测；缩小到唯一标识。
- 格式变化：先用 `--inspect <文件>` 查看记录类型分布，再修改解析器。
- 无法完整导出：报告已获得的范围并标记“待补存”，不要生成伪原文。
