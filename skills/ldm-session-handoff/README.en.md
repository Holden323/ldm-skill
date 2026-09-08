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

- `SKILL.md`: Agent-facing entry point and core workflow.
- `references/formats.md`: Output format templates for transcript, router, and restart prompt.
- `references/export-backends.md`: Backend-specific export commands (Hermes SQLite, Claude Code JSONL, Codex JSONL).
- `scripts/export_transcript.py`: Export from Hermes SQLite database.
- `scripts/export_jsonl_transcript.py`: Export from Claude Code / Codex JSONL logs.

The transcript must come from a verifiable data source — the script reads the database directly, never generates from memory.
