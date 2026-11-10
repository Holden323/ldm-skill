# Closeout Mode: Align Knowledge After a Project or Phase

> Added 2026-11-10. Absorbs neat-freak's completion contract, anti-patterns, and two-phase reporting, rewritten for content production and multi-agent collaboration. Use after a project, episode, phase, or delivery is done; when the user says "收尾" (wrap up), "洁癖" (neat), "/neat", or is clearly wrapping up.

Goal: after finishing something, docs, rules, memory, and the workspace all match reality, so the next session or a first-time newcomer finds the one current answer. Not "write more" but "subtract first, then add."

## Scope

| What the user says | Scope |
|---|---|
| "Wrap up" / "neat" with no target | Projects actually touched in this session, plus related memory entries |
| Names a project or episode | That project, plus related memory entries and the shared-tool notes it directly references |
| "The whole workspace" / "all projects" | Only then expand project by project; report size and expected time first |

The default write boundary is the in-scope projects and memory. Read upper-level rules and sibling project names only to find dead references; don't edit or move out-of-scope projects. Projects another window is actively working on are read-only.

## Completion contract: every fact surface gets a status

| Fact surface | Question to answer | Typical evidence |
|---|---|---|
| Project reality | How far along is it really? | The project's own progress files (process checklist, start-here doc, status table), final cuts and deliverables, code and tests |
| Project docs and entry points | Do entry docs, notes, and READMEs give the current answer? | Entry files, version numbers, paths, delivery notes |
| Rule files | Are agent constraints single-sourced, executable, free of dead references? | Layered CLAUDE.md, AGENTS.md, hooks, shared-tool notes |
| Memory | Are states, versions, and paths in memory still accurate? Any progress logs? | Memory index, related entries |
| Workspace residue | Any session leftovers, intermediates, uncommitted changes? | git status, temp scripts, test frames, old copies |
| Git and backups | Is what should be committed committed? Anyone else's staged changes? | git status, diff --cached, daily snapshot log |
| Shared knowledge layer | Did lessons that hold across projects flow back? | See "Flow back to the shared knowledge layer" below; mark `not-applicable` if the user has no shared layer |

Mark each surface as one of:

- `verified-current`: checked, matches reality, unchanged.
- `changed-and-verified`: changed, then re-verified.
- `pending`: can't be verified now, or needs the user's ruling. Never written into authoritative docs as fact.
- `out-of-scope`: not checked this time; say why.
- `not-applicable`: the project has no such surface (e.g. no Git); say so, don't fabricate evidence.

Don't treat "git status is clean," "the user said so," or "self-check passed" alone as fully synced.

## Flow

1. **Inventory.** List files changed or produced in this session (git status, diff, writes in the session); read the project entry, the active rule chain, and related memory entries; run `python3 scripts/scan.py <dir> --compact` once on the project directory and once on the memory directory, then review dead paths, broken links, index reconciliation, and "X wins" declarations in the details. For large projects, read the entry, rules, and files hit by this change rather than every doc.
2. **Align facts.** With project reality as the standard, rewrite stale entry docs, version numbers, paths, and status sentences in place ("uploaded," "not deleted," "size," "next step" are pointers too). Edit the existing entry rather than appending a parallel version. Mark what can't be verified as `pending`.
3. **Tidy memory.** Subtract first: delete finished to-dos, progress logs, and superseded statements; use absolute dates for state; progress stays in project files, memory keeps red lines, preferences, and pointers. Record only lessons that really happened and are reusable; "no new lesson this time" is a valid result. Update any topic pages touched by this round's changes (how topic pages work: "Topic pages" in [replay.en.md](replay.en.md)).
3a. **Flow back to the shared knowledge layer.** Follow the "Flow back to the shared knowledge layer" section below; with no cross-project lesson, write "nothing flowed back this time."
4. **Check for gates.** If an error from this session is the third occurrence in rules, memory, or the pitfall log, handle it per "Third time the same mistake happens, add a gate" in the main entry.
5. **Count residue.** One-off plan docs, debug scripts, `xxx_old`, `xxx_backup`, test frames, temporary previews. Where the user already has an explicit rule such as "delete regenerable intermediates directly," follow it and list what was deleted in the report; everything else goes on the deletion candidate list with reasons.
6. **Report, then stop.** Give the full report using the template below and keep the scene intact. Deletion candidates, commits, and pushes wait until the user explicitly confirms after reading the report. "Clean up when done" in the original request does not replace this post-report confirmation.
7. **Clean up (after confirmation).** Delete only confirmed items; re-check afterwards and add a short follow-up report of what was actually deleted and any remaining warnings.

## Flow back to the shared knowledge layer

> Added 2026-11-10. Lessons kept in a project are read only by that project's agents; the part that holds across projects should sink to a place every agent reads.

The shared knowledge layer is a knowledge area the user keeps for several agents and projects, such as a shared section of an Obsidian vault. Where it is and how to write to it come from the user's rule files (global CLAUDE.md, AGENTS.md, etc.) or memory; the Skill doesn't hard-code a path. If the user has no such layer, mark this surface `not-applicable`.

1. From the lessons kept in step 3, pick only those that would still hold in a different project. Lessons useful to just this project stay in its methodology and don't flow back.
2. If the shared layer has its own writing guide or root rule file, read it first and let it decide which file each lesson goes into; edit existing entries rather than appending parallel statements. Each entry states its source (which project, which day, what situation).
3. If the shared layer keeps an update log, add an entry: date, project, which lessons flowed back, and where each went.
4. Follow the shared layer's own rules (common ones: don't restructure, keep the header format, don't commit for the user); ask the user before creating a new category.
5. List what flowed back and where in the report. Finding no cross-project lesson is a valid result: write "nothing flowed back this time"; don't force one.

## Noise to remove first (anti-patterns)

| Anti-pattern | Handling |
|---|---|
| Progress logs in memory ("on 11-02 did…, on 11-03 also…") | Progress goes back to project progress files; memory keeps red lines and pointers |
| Finished to-dos still listed | Verify, then delete or rewrite as a still-valid constraint |
| Long single-incident narratives in memory | Distill to a sentence or two of reusable lesson; the process stays in the retro doc or Git |
| Multiple versions each claiming to be current | Decide by project reality; mark old ones historical or move to a history folder |
| A declaration that an outdated copy wins | List for the user to decide; flip the source-of-truth direction; label the old copy as a historical archive |
| Config or rules that no tool actually reads | Delete together with the rules referencing them; rewrite the real intent as text the agent can follow |
| The same rule copied into global, project, and Skill | Keep one original; elsewhere a short pointer |
| "Kept for history" with no real reader | Demote to project docs if someone will read it; otherwise list as a deletion candidate |

## Memory surface: per-platform load limits

- Claude Code auto memory: the index `~/.claude/projects/<project>/memory/MEMORY.md` loads only the first 200 lines or 25 KB (whichever comes first) at session start; entry files are read on demand. The index holds one-line pointers only; bodies live in entry files.
- CLAUDE.md, AGENTS.md: loaded in full; aim for under about 200 lines — the longer, the less they're followed. This is a quality budget, not a hard cutoff.
- Machine-generated memory such as Codex's: usually not hand-editable; mark it `read-only` and submit corrections only through the product's own controls.
- Memory written through a memory tool, such as Hermes: has a character budget; operational gotchas in [pitfalls.en.md](pitfalls.en.md) #18.
- An unfamiliar platform: look for the official control surface first; if none, treat as read-only.

## Report template

```text
## Closeout done (<scope>)

**Impact**: <which misleading info, risks, or handoff costs were removed>

**Fact surfaces**
- Project reality: <status> — <evidence>
- Project docs and entry points: <status> — <what changed>
- Rule files: <status>
- Memory: <status> — <entries deleted / changed / added>
- Workspace residue: <status>
- Git and backups: <status>
- Shared knowledge layer: <status> — <which lessons flowed back and where; or "nothing flowed back this time">

**For you to confirm**
- Deletion candidates: <file + reason>; nothing deleted until you confirm
- Can't rule: <conflict + evidence on both sides>

**Leftovers**: <pending / out-of-scope / unresolved warnings; "none" if none>
```

Report memory index size only when it exceeds 70% of the platform limit. If a cleanup scene remains, say "scene kept, waiting for your confirmation before cleanup."

## Working with ldm-session-handoff

Closeout handles "knowledge matches reality"; handoff handles "session transcript, router, and restart prompt." When the user wants both, close out first, then hand off, so the handoff router points to the post-closeout current files.
