---
name: ldm-session-handoff
description: >
  Export raw conversation transcripts, generate task routers and restart prompts,
  and help long-running tasks resume across sessions. Triggered when the user says
  "会话存档" (session archive), "保存聊天记录" (save chat log), "导出对话全记录"
  (export full transcript), "生成路由器" (generate router), "准备退出重启"
  (prepare to exit and restart), or "给我重启提示语" (give me a restart prompt).
  Not used for ordinary file archiving.
---

# Session Handoff

The goal is to let the next session verify original records and quickly restore decisions, deliverables, progress, and to-dos.

## Select artifacts based on user request

- **Full handoff:** full transcript, router, restart prompt.
- When the user explicitly says "export the transcript only": generate only the full transcript.
- When the user explicitly says "update the router only": read existing records and deliverables, then update the router.
- When the user explicitly says "just the restart prompt," "no export," or "don't create files": give only the prompt; if reliable context is missing, clearly state what information is pending.

When the user says "load the handoff skill," "use the handoff skill," "session archive," "save conversation," or "prepare to exit and restart," default to full handoff — even if the same message also mentions "give me the restart prompt." Only switch to a single artifact when the user narrows scope with words like "only," "just," "no export," or "don't create files."

## Full handoff workflow

1. Confirm the current session, topic, and save directory. Prefer the user's configured archive root; otherwise use an explicit directory in the current workspace.
2. Read user/assistant originals via the platform's native export capability or this skill's scripts. Never generate the "full transcript" from memory.
3. Generate the router, keeping only decisions, deliverables, progress, to-dos, and new lessons needed to resume the task.
4. Verify that files exist, message counts are in the right order of magnitude, and source labels are accurate.
5. Report the absolute paths of all artifacts, then deliver the copyable restart prompt directly.

Formats are defined in [references/formats.md](references/formats.md). Load [references/export-backends.md](references/export-backends.md) only when choosing or troubleshooting an export backend.

## Transcript authenticity

- The "full transcript" must come from a verifiable session data source.
- By default, keep user/assistant visible text; filter out tool calls, tool output, reasoning traces, environment injections, and empty placeholders.
- Do not label summaries, routers, or model recollections as raw transcripts.
- When the export is incomplete, state the obtained range and mark it as "pending." Do not claim the data is necessarily permanent.
- Truncating individual messages loses originals; only truncate when the user requests size control or platform limits are unavoidable, and record the threshold and count in the file header.

## Router

The router is a navigation aid, not a conversation replay. At minimum it must cover:

- Key decisions and their rationale.
- Absolute paths and status of completed deliverables.
- Work in progress: where it stands and what comes next.
- Unresolved issues and explicit to-dos.
- Only newly emerged and reusable lessons from this session.

External links should record only the entry points that need continued use. Do not write sensitive credentials into the router.

## Export tools

- Hermes SQLite: `scripts/export_transcript.py`
- Claude Code / Codex JSONL: `scripts/export_jsonl_transcript.py`

Scripts only export raw transcripts; they do not generate routers. Use `--list` to find the session first, then specify session and output path; do not guess when multiple backends exist on the same machine.

**Active sessions** do not appear in `--list`. Export steps: `session_search` with keywords from the current conversation → extract `session_id` from results → `export_transcript.py --session <id> --output <absolute-path>`. This path works equally for active and completed sessions.

## Completion check

- Delivered artifacts match the scope the user requested.
- Full transcript file header records the data source, session identifier, time range, message count, and export method.
- For full handoff, both files have had their absolute paths reported, and the restart prompt has been delivered directly to the user.
- Failures and truncations are noted honestly; no summary has been passed off as raw transcript.

## Pitfalls

### 1. Never claim "can't export" (2026-09-04/09-08 battle-tested lesson)

When the user explicitly requests an export, never give up citing "this is the active session." Export path: `session_search` to extract session_id → `export_transcript.py --session <id>`. This works for both active and completed sessions.

This error has made the user furious twice. If `--list` doesn't find it, try `session_search`. If `session_search` doesn't find it either, report honestly — but exhaust both paths first.

### 2. Restart prompts and routers must use absolute paths (2026-09-04/09-08 battle-tested lesson)

- ❌ `~/Documents/Hermes_Workspace/...` (`~` is not an absolute path — the user will be furious)
- ✅ `/Users/likai/Documents/Hermes_Workspace/...`

All file paths must start with `/Users/likai/`. This applies to restart prompts, router deliverable lists, and user-provided guides. The user has corrected this multiple times.
