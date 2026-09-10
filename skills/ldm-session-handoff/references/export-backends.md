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

## Codex

```bash
python3 scripts/export_jsonl_transcript.py --list --agent codex --date <YYYY-MM-DD>
python3 scripts/export_jsonl_transcript.py --agent codex --session <rollout 路径或唯一片段> -o <输出文件.md>
```

默认从 `~/.codex/sessions/YYYY/MM/DD/` 查找 rollout JSONL。若当前平台提供原生线程读取或导出，优先使用平台能力，避免依赖内部格式。

## 失败处理

- 找不到会话：列出候选会话并核对日期、平台和工作目录。
- 多个结果命中：不要静默猜测；缩小到唯一标识。
- 格式变化：先用 `--inspect <文件>` 查看记录类型分布，再修改解析器。
- 无法完整导出：报告已获得的范围并标记“待补存”，不要生成伪原文。
