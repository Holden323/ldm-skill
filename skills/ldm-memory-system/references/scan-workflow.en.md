# Phase 2: Maintenance Workflow

> First battle-tested 2026-08-27; refactored into the unified four-question framework on 2026-08-28.
> Execute within the task scope. The three lists are recommended output for bulk governance, not a mandatory format for every request.

## When to use

- User says "clean up memory," "memory health check," or "run through the project"
- The system has been in use for a while and feels messy
- New Memory entries follow the write rules (a subset of step four)

## Prerequisites

1. Clarify whether the user wants to check Memory, directories, Skills, or the entire cognitive asset system
2. Read only the scope needed to complete this task
3. When Memory is involved, identify entry types: long-term preference / current state / pointer / environment config that shouldn't be in Memory

## Step 1: Evaluate each entry (run the four questions)

For each item (Memory entry / document / Skill / pointer), run the four questions:

| Determination | Action |
|---|---|
| Belongs in current layer | Keep |
| Duplicate (overlaps with another entry) | Add to candidate deletion list; verify source of truth |
| Should be in a lower layer (details belong in Skill/docs) | Add to pending demotion list |
| Involves external token / count / path | Add to pointer verification list |

Four-question check:
```
① Which layer?     Should be in Skill / Docs / Memory? Wrong layer → demote or promote
② Where's truth?   Which file is the sole source of truth? Stale copy → delete copy; stale source → fix source
③ Still accurate?   Does the target still exist? Is the count correct? Is the project still alive?
④ Findable?         Does the directory have a README? Does a long doc have ## sections? Does a skill have a description?
```

## Step 2: Verify pointers (verify on the spot, don't trust cache)

For all pointers involving external data, verify immediately:

- Feishu token → fetch to confirm the document exists and the count is correct
- Local path → stat/ls to confirm the file exists and the size is reasonable
- Cron ID → cronjob list to confirm it exists and status is normal
- API key → confirm the source of truth is in config.yaml, and Memory does not contain the full key
- Version number → check whether a newer version has superseded it

## Step 3: Produce action lists

```markdown
① Pending deletion review (duplicates / zombies):
1. "Entry summary" → duplicate of XX / already consolidated into Skill

② Pending demotion archive (should be in lower layer):
1. "Entry summary" → source of truth is XX; Memory keeps only a pointer

③ Stale pointer list (verified as broken):
1. "Entry summary" → verification result: broken / valid / pending confirmation
```

## Step 4: Execute within authorization

- When the user has explicitly named targets and actions, execute within that scope directly; do not re-request the same confirmation
- When the user only said "clean up" or the scope is unclear, have the user confirm the specific deletion, overwrite, and batch migration lists first
- Execute using the memory tool's operations batch
- Report after execution: deleted N, demoted N, corrected N, Memory from X% down to Y%

## Step 5: Record in the pitfall log

New pitfalls found in this scan → append to `references/pitfalls.md` (full case library, sequentially numbered). High-frequency rules in the SKILL.md body only collect repeatedly recurring lessons; new findings go into pitfalls.md only.

## Notes

- Concurrent updates may occur during scanning (other sessions modifying Memory at the same time); re-read before executing
- Do not modify too many entries at once; the memory tool is all-or-nothing — one match failure rolls back the entire batch
- Use read-only operations (fetch/stat/ls) when verifying pointers; do not modify any external data
- Project completion is only confirmed when the user explicitly says so ("XX project is done/cancelled"); the Agent must not infer this
- Deletions, overwrites, and batch migrations with unclear scope must be confirmed with a specific list first
