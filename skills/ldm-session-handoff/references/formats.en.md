# Session Handoff Formats

Used during full handoff. When the user requests only a single artifact, use only the corresponding section.

## Save structure

```text
<archive-root>/<YYYY-MM-DD>/
├── <YYYY-MM-DD>_full-transcript_<platform>_<topic>.md
└── <YYYY-MM-DD>_router_<platform>_<topic>.md
```

Topic in the filename should be short, recognizable, and free of keys or private identifiers. Always report with absolute paths.

## Full transcript file header

```markdown
# Full Transcript

> Platform: <platform>
> Session ID: <session id or source file identifier>
> Time range: <start> ~ <end or in-progress>
> Message count: <count and filtering notes>
> Export time: <timestamp>
> Export method: <native export / SQLite direct read / JSONL direct read>, not AI summary
> Truncation: none; or threshold and count
```

Body alternates between `## User` and `## Assistant` sections. Do not mix in tool output.

## Router

```markdown
# <date> <topic> — Router

> Platform and session: <identifier>
> Time: <range>

## Key Decisions

- <decision, rationale, boundaries that still apply>

## Deliverables

| Artifact | Absolute path or final link | Status |
|---|---|---|

## Current Progress

<what is being done, where it stands, what comes next>

## To-Do

- <specific task, quantity, or completion criteria>

## Lessons Learned

- <only newly emerged and reusable items from this session>
```

## Restart prompt

```text
Continue <task>.

Last session completed:
- <deliverable and status>

Next steps:
- <next action and completion criteria>

Read these files to restore context:
- <router absolute path>
- <additional originals or key deliverables absolute paths, if needed>

Constraints:
- <key restrictions that still apply>
```

The prompt should let the next session find key files without re-searching, but do not paste the entire router into it.
