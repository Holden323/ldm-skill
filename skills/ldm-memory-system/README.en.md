# ldm-memory-system

## What problem does it solve?

Your AI assistant has a memory space, and also stores documents, skills, paths, and tokens. Over time, it turns into chaos:

- **Memory only grows:** It fills up, you delete, then you forget.
- **Stale pointers go unmanaged:** That Feishu link expired months ago but is still taking up space.
- **Duplicate rules contradict each other:** The same rule lives in Memory, in docs, and in a Skill — you update one and forget the others.
- **No idea where things belong:** Workflows that should be Skills stay in docs; details that should be one-line pointers are stuffed into Memory.

## What changed?

**Before:** Only one action — "declutter memory" — and it only managed Memory, ignoring docs and Skills. Like cleaning the living room while the kitchen and bedroom stay messy.

**After:** One framework governs all categories — Memory entries, docs, Skills, and pointers — all checked through the same four questions:

```
① Which layer?      Should this live in Skill / Docs / Memory?
② Where's the truth? Which file is the single source of truth? Everything else is a copy/signpost?
③ Still accurate?    Does the target still exist? Are the numbers still correct?
④ Findable?          Does the directory have a README? Does a long doc have section headers?
```

One pass through the four questions — keep what stays, delete what goes, relocate what's misplaced.

## How does it work?

**Setup** (first time / system is messy):
Start by asking three questions (what long-term projects do you have? which files are referenced most often? which operations have been repeated?). Then build a three-layer structure based on your actual situation — Skill playbooks, project docs, pocket memory — each in its place.

**Maintenance** (daily / periodic):
Scan the specified scope through four questions → produce an action list with evidence → deletions, overwrites, or batch migrations with unclear scope are confirmed by you → verify sources of truth and pointers after execution.

## Core rules (three sentences)

1. **Memory is a pointer, not a database** — full content lives in docs/Skills; Memory only holds navigation.
2. **One piece of knowledge, one source of truth (SOT)** — other layers hold pointers at most; no parallel copies.
3. **Deletion requires authorization** — named targets can be executed directly; vague requests like "clean up" get a list first.

## How does it work with other skills?

- `ldm-session-handoff` (handoff) handles "no progress lost between sessions"; this skill handles "long-term memory doesn't decay."
- Project wrap-up (code/docs mismatch) is neat-freak's job; this skill doesn't touch code.

## When should I use it?

- You say "clean up memory"
- You say "my memory system is a mess, help me set it up"
- You say "organize my docs / too many skills"
- When the Agent writes new things into Memory, follow the write rules here
