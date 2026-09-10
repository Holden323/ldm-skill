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

The router is the primary carrier of resume context; the restart prompt is only an entry point. The transcript is for auditing, the router is for resuming.

```markdown
# <date> <topic> — Router

> Platform and session: <identifier>
> Time: <range>

## Key Decisions

- <decision, rationale, boundaries that still apply>

## Checkpoints

> In chronological order. Only completed and confirmed milestones; anything unverified does not count.

1. <milestone> — Evidence: <absolute path / link / verification result>

## Deliverables

| Artifact | Absolute path or final link | Status |
|---|---|---|

## Resource Versions

> Only write things where using the wrong version would make the next session do the work wrong. Undecided states and not-yet-done items belong in the to-do or next-step sections, not here. Write "none" if there is nothing.

- <skill / asset library / template / tool>: <version or snapshot id> (<currently in effect / superseded by which version>)

## Current Progress and Next Step

- In progress: <started but unfinished; write "none" if nothing>
- Next step: <the concrete next action and completion criteria>
- Preconditions: <what must be in place or confirmed before starting; write "none" if nothing>

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

Read these files to restore context (progress, resource versions, and preconditions live in the router):
- <router absolute path>
- <additional originals or key deliverables absolute paths, if needed>

Constraints:
- <key restrictions that still apply>
```

The prompt is an entry point, not the carrier: it should let the next session find the router without re-searching, but do not paste the entire router into it.
