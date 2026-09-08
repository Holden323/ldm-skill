# Phase 1: Setup Workflow

> For building a cognitive asset system from scratch, or rebuilding when the system is messy. Refactored 2026-08-28, unified four-question framework.

## When to use

- New user setting up a memory system for the first time
- Existing user whose system is messy: no indexes, no categorization, no idea what should become a Skill
- User says "build a memory system," "start from scratch," or "my memory is a mess, rebuild it"

## Prerequisites

1. Load this skill (ldm-memory-system) as the referee
2. Read all current Memory entries (if any)
3. Understand the user's project structure (read READMEs, scan directories)

## Step 1: Three discovery questions

Ask the user 3 questions (the answers determine layering and graduation criteria):

```
① What long-term projects do you have?
   → Determines how the document layer is organized into folders

② Which files are referenced most often?
   → Determines which need indexes (README / sections)

③ Which operations have been repeated 3+ times?
   → Determines which should graduate into Skills
```

When the user's answers are incomplete, infer from existing files (READMEs, directory structure, skill list); do not force the user to answer every item.

## Step 2: Draw the three-layer structure

Use **the user's own projects as examples**, not generic templates. Example format:

```
Layer 3 — Skills (Playbooks)
  ├─ <Skill A>: <what it solves>
  └─ <Skill B>: <what it solves>

Layer 2 — Document System (Project Library)
  ├─ <Project A>/
  │   ├─ README.md (directory index)
  │   └─ <key-doc>.md (## sections)
  └─ <Project B>/

Layer 1 — Memory (Pocket Notebook, ~2000 chars)
  ├─ Rules: <rule 1> / <rule 2>
  ├─ Progress: <number 1> / <number 2>
  └─ Pointers: <to doc X> / <to Skill Y>
```

## Step 3: Build the document layer

Create folders by project; add README only when a directory has multiple entry points and lookup cost clearly rises:

```
project-folder/
├── README.md        # What's in this folder, what to read first
├── doc-A.md         # Long docs must have ## section headers (grep-searchable)
└── source-material/ # Source material subdirectory
```

Standards:
- READMEs should solve real navigation problems; do not create them mechanically by file count
- Long documents use section headers when multiple topics or jumps are needed; do not judge mechanically by line count
- Version naming: V1/V2/V3; never overwrite old versions (archive both local and cloud)
- Update the README after creating new files/directories

## Step 4: Build the Memory layer

Inventory existing entries (if any), categorize by the four questions:

| Determination | Action |
|---|---|
| Belongs in current layer (Memory) | Keep; rewrite in B-grade format |
| Duplicate (overlaps with another entry) | Add to pending deletion list (user approves) |
| Should be in lower layer (details in Skill/docs) | Add to pending demotion list (user approves) |
| Involves external token / count / path | Add to pointer verification list (verify on the spot) |

Write rules:
- B-grade format: conclusion + key numbers + reasoning summary
- One entry per line, § as separator
- No full API keys (source of truth is in config files)
- No full paths (source of truth is in docs/config)
- No raw conversation text (source of truth is in chat archives)
- Before writing, ask: will this entry be corrected? Yes → put it in the layer that can be corrected

## Step 5: Define graduation criteria

Specify "what content should be promoted to a Skill." All 4 conditions must be met:

```
① Repeatability: the same workflow has appeared 3+ times
② Transferable: another person / another Agent can execute it
③ Has trigger conditions: can clearly write "when to use it"
④ User confirms: the user explicitly says "this will be done regularly"
```

List the user's existing "repeated operations" and evaluate each one. Not met → stays in the document layer.

## Step 6: Trial run verification

After setup, run one maintenance scan (see scan-workflow.md) to confirm:

  - Every pointer points to an existing file
  - Key entry points have usable indexes
- Memory entries are clearly categorized and deduplicated
- The user can answer "where is my XX information?"

## Minimum viable version (for users who fear complexity)

Only do the first three steps; build the document and Skill layers as needed:

1. Memory categorization: sort existing entries into rules / progress / pointers
2. Root README: entry files → project directories → tools → archives → quick navigation
3. Run one maintenance scan for verification

Not everything has to be built at once. A working system matters more than a "complete" one.

## Notes

- Concurrent updates may occur during setup (other sessions modifying files at the same time); re-read before operating
- When the user has not specified a target, deletions, overwrites, and batch migrations must present a specific list for confirmation first
- Use read-only operations (fetch/stat/ls) when verifying pointers; do not modify any external data
- Only write to `references/pitfalls.md` when a new lesson is reproducible and would affect future decisions
