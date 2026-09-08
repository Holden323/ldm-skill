# Session Transcript Export Backends

Load only when choosing, running, or troubleshooting an export method. Prefer the platform's built-in full transcript export capability; fall back to scripts only when no suitable capability exists.

## Hermes

When Hermes sessions are stored in a SQLite database:

```bash
python3 scripts/export_transcript.py --list --date <YYYY-MM-DD>
python3 scripts/export_transcript.py --session <session_id> -o <output.md>
```

Default database is `~/.hermes/state.db`. When the database schema changes, inspect the table structure read-only first; do not modify the original database.

## Claude Code

```bash
python3 scripts/export_jsonl_transcript.py --list --agent claude --date <YYYY-MM-DD>
python3 scripts/export_jsonl_transcript.py --agent claude --session <session_id> -o <output.md>
```

Looks for JSONL files in `~/.claude/projects/` by default.

## Codex

```bash
python3 scripts/export_jsonl_transcript.py --list --agent codex --date <YYYY-MM-DD>
python3 scripts/export_jsonl_transcript.py --agent codex --session <rollout-path-or-unique-segment> -o <output.md>
```

Looks for rollout JSONL in `~/.codex/sessions/YYYY/MM/DD/` by default. If the current platform provides native thread reading or export, prefer the platform capability and avoid depending on internal formats.

## Failure handling

- **Session not found:** List candidate sessions and verify date, platform, and working directory.
- **Multiple matches:** Do not silently guess; narrow to a unique identifier.
- **Format change:** Use `--inspect <file>` to check the record type distribution before modifying the parser.
- **Cannot export fully:** Report the obtained range and mark it as "pending"; do not generate fake transcripts.
