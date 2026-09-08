# Folder Organization Rules: Mode Selection + Archiving Standards

> Inspired by: claude-obsidian's wiki-mode (mode selection over forced templates) + PARA's project/archive boundary thinking.
> Principle: **Let directories grow naturally, but grow straight.** No rigid templates, no disrupting naturally evolved structure.

## I. Mode selection (three modes, pick one as primary)

| Mode | When to use | Structure | Your current system |
|---|---|---|---|
| **Project-based** (recommended default) | Few clear projects (<30), one directory each | Top level = project directories; free growth inside | ✅ Current mode |
| PARA-lite | Too many projects for one level; need active/inactive split | Top level splits into Projects/Areas/Resources/Archive | Alternative |
| Type-based | Projects are homogeneous (all same kind of output) | Split by type: drafts/source material/data | Alternative |

**Rules:**
- The primary mode only affects "where new things go" — **never batch-migrate existing directories**
- Switching modes = a standalone operation; preview first, user approves
- Do not mix: the top-level structure stays in one mode

## II. Five organization principles (project-based mode)

### ① One folder = one project
- A topic with 3+ related files → create a folder; scattered files go in
- Counterexample: `li-damo-energy-management.md` sits in the root while `writer-li-damo/` exists → orphan, should be moved in

### ② Project folder naming
- Use the project name, **no date/version/sequence prefix** (versions live in files as V1/V2, dates in filenames)
- Avoid duplicate names: one project, one source-of-truth directory (e.g., `kaihuai-beauty-ranking/` is unique)
- Counterexample: `10_beauty-ranking/` (old) coexists with `kaihuai-beauty-ranking/` (new) → old goes to archive

### ③ Root directory: active files only
- >10 scattered files in root = signal to re-home (check with scan.py)
- Historical decisions → project directory or `decisions/`
- Old versions → archive directory
- New incoming material → `_inbox/`; relocate after processing

### ④ Unified archive convention
```
project/
├── _archive/                    ← consistent naming (or "archive/", but stay consistent within one system)
│   └── old-direction_YYYY-MM-DD/   ← group by reason + date
│       └── (preserve as-is, don't reorganize)
```
- Archive block name explains "why archived" (old direction / completed / replaced by V2)
- Archive contents are preserved as-is; no secondary reorganization (saves maintenance cost)

### ⑤ Same name across locations = duplication signal
- Same-named file across directories: identical content = redundancy candidate; different = version fork candidate. Check references and source of truth first, then decide to keep, archive, or delete
- Same-named directory across locations: diff content + timestamps to determine the official version; mark the old one as "old working copy" pending user confirmation
- Modification time and content completeness are evidence only; they cannot determine the official version alone — also check references, project notes, and user's current conventions

## III. Scan check items (automated by scan.py)

| Check | Signal | Action |
|---|---|---|
| Directory without README | Has files but no README.md | Add index |
| Scattered root files | >10 files | Produce re-homing list |
| Same-named file across directories | Same/different content | Check references and source of truth |
| Same-named directory across locations | Multiple instances | Determine official version |
| Empty directory | 0 files, 0 subdirectories | Delete (user confirms) |
| Same-named file within directory | Different casing | Confirm if intentional |

## IV. Relationship to the four questions

Folder-rules is the expansion of four-question #1 (which layer) **within the document layer:**
- Which layer? → Memory / Docs / Skills (SKILL.md main entry)
- Which folder? → This file (project ownership, re-homing, archiving)

## V. Pitfalls

- **Don't force templates:** claude-obsidian offers four modes for users to choose from for exactly this reason — PARA is unfriendly to writing-oriented creators (Reddit feedback); project-based is a better fit
- **Don't batch-migrate:** Switching mode / renaming / moving only affects the future; moving existing files easily breaks pointers (same root cause as the 8.28 Feishu overwrite incident)
- **Don't number globally:** Johnny.Decimal numbering has low payoff for AI Agent scenarios (Agents use README + search to find things); optional prefixes only in piles-prone directories like archives/source material
