---
name: ldm-session-handoff
description: >
  Export raw conversation transcripts, generate task routers and restart prompts, help long-running
  tasks resume across sessions, and keep the next session from repeating this session's mistakes.
  Triggered when the user says "会话存档" (session archive), "保存聊天记录" (save chat log),
  "导出对话全记录" (export full transcript), "生成路由器" (generate router), "准备退出重启"
  (prepare to exit and restart), "交接到新窗口" (hand off to a new window), or "给我重启提示语"
  (give me a restart prompt). Not used for ordinary file archiving.
---

# Session Handoff

Goal: the next session can verify the original record, quickly restore decisions, deliverables, progress and to-dos, and not repeat this session's mistakes.

## Select artifacts based on the request

- **Full handoff:** full transcript, router, restart prompt.
- User explicitly says "export the transcript only": produce only the full transcript.
- User explicitly says "update the router only": read the existing records and deliverables, then update the router.
- User explicitly says "just the restart prompt", "no export" or "don't create files": give only the prompt; if reliable context is missing, say which information still needs to be filled in.

"Load the handoff skill", "use the handoff skill", "session archive", "save the conversation" or "prepare to exit and restart" default to a full handoff. Even if the same sentence also asks for a restart prompt, do not skip the transcript and router. Narrow to a single artifact only when the user uses explicit limiting words such as "only", "just", "no export" or "don't create files".

## Full handoff workflow

1. **Locate:** confirm the current session, the topic and the save directory. A directory the user names takes priority; otherwise read `~/.config/ldm/session-archive-root` (if present, it holds the archive root as an absolute path), then fall back to another configured archive root or an explicit directory in the current workspace.
2. **Export the original text:** read user/assistant text through the platform's native export or this skill's scripts (below). Never write a "full transcript" from memory. The export scripts redact secrets automatically after writing (`scripts/redact_secrets.py`) and add a `> 打码：…` (redaction) line to the header; when it reports "candidates", look at them by hand.
3. **Write the router:** follow [references/formats.en.md](references/formats.en.md). Two sections matter most:
   - **Must-keep rules for the next session:** red lines the user set this time and mistakes the user corrected, each with what enforces it (script / hook / stop point waiting for the user / self-discipline only). Name the self-discipline-only rules in the restart prompt.
   - **Stop point:** where work must stop and wait for the user. Split long tasks by stop point: one window does only up to the next stop point.
4. **Check:** run `python3 -B scripts/check_handoff.py <router> --record <transcript> [--prompt <prompt file>]`. It checks that paths exist, are not in temporary locations (/tmp, scratchpad — they get cleaned), are not `~` paths, and that required sections, message counts and the redaction line are present. Fix until it passes. If evidence lives in a temporary location, copy it to a durable directory first and cite the new path.
5. **Index:** when the archive root has a `session_index.json`, run `python3 -B scripts/update_index.py --record <transcript> --router <router> --title "<what was done, where it stopped>"`. Archive roots without an index are skipped automatically.
6. **Report:** list every artifact's absolute path, then give the copy-ready restart prompt last. The prompt states this window's scope and stop point.

## Export tools

| Platform | Script |
|---|---|
| Claude Code, Codex (JSONL) | `scripts/export_jsonl_transcript.py --agent claude` (Codex: `--agent codex`) |
| Hermes (SQLite) | `scripts/find_session.py` to find the id → `scripts/export_transcript.py` |
| WorkBuddy (JSONL) | `scripts/export_workbuddy_transcript.py` |
| DSH | `scripts/export_dsh_session.js` → `scripts/export_dsh_transcript.py` |

First find the session with `--list` (Hermes: `find_session.py`), then pass the session and the output path; when several backends exist on the machine, do not guess. Session locations, how to find the active session and format pitfalls per platform are in [references/export-backends.en.md](references/export-backends.en.md); read it only when choosing or troubleshooting a backend. Run scripts with `-B`.

## Transcript authenticity

- The full transcript must come from a verifiable session data source.
- Keep visible user/assistant text by default; filter tool calls, tool output, reasoning, environment injections and empty placeholders.
- Never label a summary, a router or model recollection as the original text.
- When the export is incomplete, state the range obtained and mark it "pending re-export"; do not claim the data will necessarily persist.
- Truncating a message loses original text; truncate only when the user asks to limit size or a platform limit makes it unavoidable, and record the threshold and count in the header.
- When the user asks for an export, do not give up because "the session is still active": every backend can export an active session. Try the methods in export-backends first; report honestly only if they all fail.

## Router

The router restores context, the transcript is for looking things up, and the restart prompt is only an entry point. The router is navigation, not a retelling. At minimum it covers:

- Key decisions and their reasons.
- Must-keep rules for the next session: red lines, corrected mistakes, and what enforces each.
- Checkpoints: gates completed and confirmed, in time order, with evidence.
- Absolute paths and status of finished deliverables (paths must stay valid).
- Resource versions: only dependencies whose wrong version would cause wrong work on resume.
- Work in progress, next step, stop point and preconditions.
- Open questions and explicit to-dos.
- Only lessons that are new this time and reusable.

Keep only the final entry point of external links that are still needed. Never put credentials into the router or the prompt. Write every local path as an expanded absolute path, not `~`.

## Completion check

- Deliverables match the scope the user asked for.
- `check_handoff.py` passes: the header message count equals the body count, the redaction line is present, all paths exist and are not temporary, and the router has the must-keep rules section and the progress / next step section.
- For a full handoff: both files reported with absolute paths; the index updated where the archive root has one; the restart prompt sent directly to the user, stating this window's scope and stop point.
- Failures and truncation are stated honestly; no summary passes as the original text.

When modifying this skill itself (source of truth, install forms, syncing), read [references/maintenance.en.md](references/maintenance.en.md).
