# LDM-skill

**AI Skills built from real workflows.** Every skill here was battle-tested in daily work before being published.

Supports: Hermes / Claude Code / Codex / Doubao / WorkBuddy, and any other Agent that supports Skills.

[简体中文](README.md) | English

---

## Install in one line

```bash
npx -y skills add Holden323/ldm-skill -g --all
```

Your Agent will load these skills on demand. To install just one:

```bash
npx -y skills add Holden323/ldm-skill --skill ldm-ai-to-human-zh -g
```

---

## What's included

### 1. AI-to-Human Chinese Rewriter (ldm-ai-to-human-zh)

**Rewrite AI-generated Chinese so it sounds like a real person wrote it.**

You asked AI to draft something in Chinese, but it feels off — too smooth, too uniform, too "correct." Anyone can tell a machine wrote it. This skill provides a concise entry point, on-demand review references, and a Python signal-scanning script.

| Problem | What it looks like |
|---------|-------------------|
| Formulaic patterns | "It's not X, but Y" and "You think X, but actually Y" everywhere |
| Broken rhythm | Every sentence ends with a period; reads like a robot |
| Stiff vocabulary | "Furthermore," "In fact," "It is worth noting" piling up |
| No rough edges | Nothing the author themselves hadn't fully figured out |

Usage: tell your Agent **"check this draft for AI traces"** or **"rewrite this to sound human."** Direct rewrite requests are completed immediately; when processing files without explicit overwrite, the default is to create the next version.

See [skills/ldm-ai-to-human-zh](./skills/ldm-ai-to-human-zh/).

### 2. Cognitive Asset Governance (ldm-memory-system)

**Give your AI's memory a declutter-and-reconcile system.**

AI memory accumulates three diseases over time: it only grows, never shrinks; stale pointers nobody maintains (that Feishu link was restructured months ago); and the same rule stored in three places, all contradicting each other. Ask it to "clean up" and it might delete blindly — then when you ask "what was my API config?" you both stare blankly.

This skill gives your Agent four universal questions: **Which layer? Where's the source of truth? Still accurate? Findable?** Every memory entry, document, skill, and pointer gets checked within the current task scope. Things that need moving get moved (demoting = moving details to a lower layer + leaving a pointer, not deletion). Things that need deleting get listed for your approval first.

| Mechanism | What it does |
|-----------|-------------|
| Four-question framework | Unified health check for Memory / docs / Skills / pointers — one set of questions regardless of category |
| Three-layer architecture | Skills = playbooks, docs = project library, Memory = pocket notebook — each stays in its layer |
| SOT chain | One piece of knowledge has exactly one source of truth; everywhere else holds at most a pointer |
| scan.py | Deterministic scanning script — 6 categories of checks, reports only, never acts |

Usage: tell your Agent **"clean up memory"** or **"memory health check."** It will check within scope and suggest actions; when the scope of deletion is unclear, it lists items for your confirmation first.

See [skills/ldm-memory-system](./skills/ldm-memory-system/).

### 3. Session Handoff (ldm-session-handoff)

**AI has no memory, but it can hand off between sessions.**

Tired of re-explaining context every time you start a new session? A crash wipes out 30 minutes of setup? Asking AI to summarize its own conversation, only to find it dropped details or made things up?

This workflow builds a handoff protocol for your Agent. Each session ending produces **two files + one prompt snippet**:

| Artifact | Purpose | Audience |
|----------|---------|----------|
| ① Full transcript | Raw conversation exported message by message from the local database (with export script). Traceable and auditable. | Human (archive original) |
| ② Router | Key decisions, checkpoints, deliverables, resource versions, next step and preconditions — one page. This is what resume depends on | Human and AI (navigation map) |
| ③ Restart prompt | A block of text you paste into a new session so it finds the router and knows the constraints | AI (handoff brief) |

There is one core principle: **restoring context requires the original record, not a retelling.** The transcript must be read directly from the database — summaries are never acceptable substitutes. Roles are split: the transcript is for auditing, the router is for resuming, and the prompt is only an entry point.

Usage: tell your Agent **"prepare to exit and restart, export the full transcript,"** or run the script directly:
`python3 skills/ldm-session-handoff/scripts/export_transcript.py --list`

See [skills/ldm-session-handoff](./skills/ldm-session-handoff/).

### 4. Personal Empirical Tracker (ldm-empirical-life-tracker)

Track important thoughts, predictions, decisions, and outcomes as traceable personal evidence. Supports recording, backfilling, retrospectives, and low-risk personal experiments. It distinguishes facts, experiences, interpretations, and hypotheses — never infers stable personality traits from a few records, and never scans or writes private data without explicit authorization.

See [skills/ldm-empirical-life-tracker](./skills/ldm-empirical-life-tracker/).

### 5. Narrative Commentary Writing (ldm-narrative-commentary-writing)

Write factually sound, narrative-and-commentary-alternating long-form Chinese articles from confirmed event or opinion topics — for general readers who should be able to retell what happened and why it matters. Supports direct drafting, structural planning, and editorial review, with on-demand references for fact-checking, six-beat rhythm, voice, and readability.

See [skills/ldm-narrative-commentary-writing](./skills/ldm-narrative-commentary-writing/).

---

## Design principles

1. **Only generalized, sanitized methods.** Project-specific private skills stay out of this collection.
2. **Every skill must be used in the author's own daily work.** If it hasn't been run in production, it doesn't ship.
3. **Mechanism over tooling.** Each skill explains *why* it works this way, so it can be ported to any Agent.
4. **Light entry, layered detail.** Each SKILL.md keeps only triggers, decision criteria, and resource routing; long examples and platform-specific details are loaded on demand.

## Changelog

- **2026-09-10** — ldm-session-handoff router revised: added checkpoints, resource versions, and next-step preconditions; the restart prompt is now explicitly an entry point, with the router carrying resume
- **2026-09-07** — Added ldm-empirical-life-tracker and ldm-narrative-commentary-writing; unified multi-Agent source of truth
- **2026-08-29** — Added ldm-memory-system (cognitive asset governance); README links aligned with renamed directories (ldm- prefix)
- **2026-08-26** — Repository upgraded to collection ldm-skill; added ldm-session-handoff (session handoff)

## License

MIT License
