---
name: ldm-memory-system
description: >
  Design, audit, and maintain a long-term cognitive asset system composed of Memory,
  project docs, Skills, and pointers. Triggered when the user says "搭建记忆系统"
  (build memory system), "清理 memory" (clean up memory), "memory 体检" (memory health check),
  "整理知识库" (organize knowledge base), "检查真源或失效指针" (check source of truth or
  stale pointers), or "Skill 太多了" (too many skills).
  Not used for ordinary file archiving, session handoff, code deployment, or general project cleanup.
---

# Cognitive Asset Governance

The goal is to place important information at the right layer, maintain a single updatable source of truth, and keep everything accurate and findable.

## Determine the task mode first

- **Diagnosis or health check:** Read-only inspection; produce evidence and candidate lists.
- **Build or restructure:** Understand existing projects and entry points first, then propose a reviewable structure.
- **Execute cleanup:** Modify within the user's explicitly authorized scope; when the scope of deletion or batch moves is unclear, present a specific list first.
- **Single write:** Determine whether to write to Memory, docs, Skills, or config; no need to run a full scan.

When the user has explicitly specified how to keep, move, or delete a piece of content, follow the current instruction. Do not override user choices with the skill's default workflow.

## Four questions

Apply uniformly to Memory entries, documents, Skills, and pointers:

- **Which layer:** Is this a long-term preference, project fact, reusable workflow, or environment config?
- **Where's the source of truth:** Which location is responsible for updates? Are the others just indexes or stale copies?
- **Still accurate:** Can paths, links, numbers, versions, and project status be verified on the spot?
- **Findable:** Is the entry point sufficient for humans and Agents to locate quickly? Add indexes only when there is a real navigation difficulty.

## Layering principles

- **Skills:** Repeatable methods, domain rules, and tool workflows.
- **Project docs:** Project facts, decisions, materials, deliverables, and history.
- **Memory:** Cross-session preferences, current state, and short pointers frequently needed.
- **Config / key store:** Credentials, runtime parameters, and environment facts.

Each piece of information has exactly one source of truth. Other layers may hold brief pointers but must not duplicate body text. Memory capacity should be determined by retrieval value, not treated as a full database.

## Maintenance workflow

When scanning a directory or knowledge base:

1. Define the scan scope and current task; do not default to the entire workspace.
2. Run a read-only scan on the directory:

   ```bash
   python3 scripts/scan.py <target-directory> [--depth 2] [--compact]
   ```

3. Interpret candidates in context. The script finding same-named items, missing READMEs, or scattered files does not automatically mean they must be deleted or moved.
4. Output candidates for action: duplicates or zombies, information that should be migrated, stale pointers. Each item includes evidence, target location, and risk.
5. Execute modifications that have been explicitly authorized; deletions, overwrites, or batch migrations with unclear scope require user confirmation of the specific list.
6. Re-verify pointers, entry points, and sources of truth after changes; do not repeat a full scan just to fill the process.

Detailed maintenance steps are in [references/scan-workflow.md](references/scan-workflow.md). Load [references/folder-rules.md](references/folder-rules.md) only when the task involves directory structure.

## Setup workflow

For building from scratch or major restructuring, read [references/setup-guide.md](references/setup-guide.md). Start by inferring structure from existing READMEs, directories, and Memory; only ask questions when missing information would change the plan.

Do not force every directory to have a README, and do not decide whether a document needs sections by line count. The complexity of indexing and layering should be proportional to actual lookup cost.

## Safety and authenticity

- Do not write complete keys, tokens, or sensitive credentials into Memory, docs, or reports.
- Project completion status cannot be inferred solely from inactivity, departure, or discontinued updates; if an action depends on this status, list it as a fact pending confirmation.
- "Demoting" means moving details to the appropriate source of truth and retaining necessary pointers — not making still-valuable information disappear.
- Before deleting existing content, confirm the target and source of truth; when the user has already named and authorized deletion, do not re-request the same confirmation.
- Prefer read-only verification for external links, cloud docs, and scheduled tasks.

## Lessons and evaluations

Load [references/pitfalls.md](references/pitfalls.md) only when investigating historical incidents or maintaining this skill; do not load the full case library into ordinary governance tasks.

Completion criteria: the user can explain where important information is updated; duplicate rules are reduced; key pointers are valid; unauthorized content has not been moved or deleted; reports do not leak credentials.
