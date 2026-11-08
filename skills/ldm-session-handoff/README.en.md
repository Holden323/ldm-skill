# ldm-session-handoff

Export raw conversation transcripts, generate task routers and restart prompts, and help long-running tasks resume across sessions.

## Install

```bash
npx -y skills add Holden323/ldm-skill --skill ldm-session-handoff -g
```

## Usage

Just say something like:

- "Prepare to exit and restart. Export the full transcript."
- "Save the conversation and generate a router."
- "Give me a restart prompt."

The skill will produce a full handoff by default (transcript + router + restart prompt). Use "only" to narrow scope: "only export the transcript" / "just the restart prompt."

## Files

- `SKILL.md` / `SKILL.en.md`: agent-facing entry point and core workflow.
- `references/formats.md`: templates for the transcript, router (including the must-keep rules section) and restart prompt (including this window's scope and stop point).
- `references/export-backends.md`: per-backend export commands and pitfalls (Hermes SQLite, Claude Code / Codex JSONL, WorkBuddy, DSH).
- `references/maintenance.md`: only for editing this skill (source of truth, install forms, syncing).
- `scripts/export_transcript.py`, `scripts/find_session.py`: Hermes SQLite.
- `scripts/export_jsonl_transcript.py`: Claude Code / Codex JSONL.
- `scripts/export_workbuddy_transcript.py`: WorkBuddy JSONL.
- `scripts/export_dsh_session.js`, `scripts/export_dsh_transcript.py`: DSH.
- `scripts/redact_secrets.py`: redacts common secret formats; the export scripts call it automatically.
- `scripts/check_handoff.py`: checks that paths in the router and prompt exist and are not temporary, and that required sections and counts are present.
- `scripts/update_index.py`: adds or updates this session in the archive root's `session_index.json`, with a backup.

Every `references/*.md` has an English `.en.md` counterpart.

The transcript must come from a verifiable data source: the scripts read the session store directly and never generate from memory.
