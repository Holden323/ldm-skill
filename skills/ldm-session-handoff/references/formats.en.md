# Session Handoff Formats

Use for a full handoff; when the user wants a single artifact, use only the matching part.

The Chinese section names below are what `scripts/check_handoff.py` looks for (`## 新会话必守`, `## 当前进度与下一步`, `本窗口`); keep them as written even in an English router, or adapt the script.

## Save structure

```text
<archive root>/<YYYY-MM-DD>/
├── <YYYY-MM-DD>_对话全记录_<platform>_<topic>.md    (full transcript)
└── <YYYY-MM-DD>_路由器_<platform>_<topic>.md        (router)
```

Keep the topic short and recognizable, with no secrets or private identifiers. Report absolute paths.

## Full transcript header

```markdown
# 对话全记录

> 平台：<platform>
> 会话标识：<session id or source file>
> 起止时间：<start> ~ <end, or in progress>
> 消息数：<count and filtering notes>
> 导出时间：<time>
> 导出方式：<native export / SQLite read / JSONL read>, not an AI summary
> 截断：<none; or threshold and count>
> 打码：<none; or type×count> (written automatically by the export scripts)
```

The body alternates `## 用户` (user) and `## 助手` (assistant). Never mix in tool output.

## Router

The router is the main tool for restoring context; the restart prompt is only the entry point. The transcript is for looking things up; the router is for resuming.

```markdown
# <date> <topic> — router

> Platform and session: <id>
> Time: <range>

## 关键决策 (key decisions)

- <decision, reason, boundaries that still apply>

## 新会话必守 (must-keep rules for the next session)

> The mistakes the next session is most likely to repeat, and the red lines the user set. Say what enforces each one. Rows marked "self-discipline only" are the risk points; name them in the restart prompt.

| Rule | User's words or source | Enforced by | What happens if broken |
|---|---|---|---|
| <do / don't> | "<quote>" (date) | script <path> / hook / stop point waiting for user / self-discipline only | <consequence> |

## 存档点 (checkpoints)

> In time order, only gates completed and confirmed; unverified ones don't count.

1. <gate> —— evidence: <absolute path / link / verification result>

## 产出清单 (deliverables)

| Deliverable | Absolute path or final link | Status |
|---|---|---|

## 资源版本 (resource versions)

> Only things that would cause wrong work if the next session used the wrong version. Undecided states and unfinished work go under to-dos or next step. Write "none" if there are none.

- <skill / asset library / template / tool>: <version or snapshot id> (<current / superseded by which version>)

## 当前进度与下一步 (progress and next step)

- In progress: <started but not finished; "none" if none>
- Next step: <the concrete next action and its completion condition>
- Stop point: <where work must stop and wait for the user; "none" if none>
- Preconditions: <what must exist or be confirmed before starting; "none" if none>

## 待办 (to-dos)

- <concrete task, quantity or completion condition>

## 经验教训 (lessons)

- <only what is new this time and reusable>
```

### Paths must stay usable

The next session must be able to open every file the router and prompt cite.
- Do not cite temporary locations: `/tmp`, `/private/tmp`, `/var/folders`, any platform's scratchpad. If evidence lives there, copy it to a durable directory (the project or the archive's date directory) and cite the new path.
- Always write expanded absolute paths, never `~`.
- Run `scripts/check_handoff.py` afterwards; it checks that paths exist and are not temporary.

## Restart prompt

Split long tasks by stop point: one window works only up to the next stop point, then hands off to a new window. Each window's context stays short, so the later part of the work is less likely to drop rules.

```text
Continue <task>. 本窗口 (this window) only does: <scope of this stretch>; stop at <stop point or completion condition>, then <what to do after stopping: wait for the user / hand off to a new window>.

Done last time:
- <deliverable and status>

Next:
- <next step and completion condition>

Read these files first to restore context (progress, resource versions and preconditions follow the router):
- <router absolute path>
- <absolute paths of the transcript or key deliverables, when needed>

Must keep (name the self-discipline-only rules from the router's must-keep section):
- <rule>

Constraints:
- <key limits that still apply>
```

The prompt is an entry point, not the main tool: it lets the next session find the router without searching, but do not paste the whole router into it.
