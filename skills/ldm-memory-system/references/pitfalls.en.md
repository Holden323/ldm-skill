# Pitfall Log (Full Case Library)

> Continuously appended by Phase 2 (maintenance) scans. The SKILL.md body only keeps high-frequency rules; the full case library lives here.
> New pitfall format: `### N. Title (date)` + scenario description + **Lesson** in one line.

### 1. Follow the workflow strictly, never skip steps (2026-08-28, hard-won lesson)

The user asked me to run the memory declutter skill. I made the following mistakes:

**Mistake 1: Deleted 10 Memory entries directly without user confirmation**
- I judged on my own which to delete and which to keep, then executed
- Violated the core rule: "the list must be shown to the user; delete only when told, keep only when told"

**Mistake 2: After restoring, judged on my own again instead of producing three lists for user approval**

**Mistake 3: Pointer verification was incomplete** (only verified some tokens/paths; missed cron IDs and key checks)

**Mistake 4: Didn't read the skill carefully before acting** (loaded it but didn't follow the 5 steps strictly)

**Mistake 5: Made new mistakes while fixing old ones** (delete → restore → delete → vicious cycle)

**Root cause:** Didn't treat the workflow as mandatory steps; kept rushing to "finish" instead of "get each step right"; didn't realize "user approval" is a non-skippable hard gate.

**Correct workflow (must follow strictly):**
1. Evaluate each entry: identify its type (rule / progress / pointer / environment)
2. Verify pointers: fetch to confirm Feishu tokens exist, local paths exist, cron IDs exist; check whether Memory contains full API keys
3. Produce three lists: pending deletion review / pending demotion archive / stale pointer list
4. Execute after user approval: execute only when the user says "go ahead"; never judge and delete on your own
5. Record in pitfall log: document new findings from this scan

### 2. Pointer bloat: compression is busywork without an exit mechanism (2026-08-27)

Memory grew from 721 characters (compressed 8.26) back to 1,518 characters (8.27). Compression itself worked, but there was no elimination mechanism — new facts were stuffed in daily.

**Lesson:** Compression is treating symptoms; an elimination mechanism is the cure. After every compression, delete what should be deleted on the spot instead of just tightening wording.

### 3. Duplicate copies fighting: same knowledge living in two layers (2026-08-27)

"Restart prompt only checks status, doesn't execute without instructions" existed in both the user profile entry and a standalone Memory entry. "Psychology illustrated" existed in both the finished-work entry and the project entry.

**Lesson:** Duplicate entries during scanning are the first signal for deletion review — no need to wait for the user to say so. Before the SOT chain takes effect, deduplicate first.

### 4. Environment info leaked into Memory: keys/paths don't belong there (2026-08-27)

The full Zhipu API key, base_url, and model config lived in Memory for a long time — the source of truth is config.yaml. Having a key in Memory means the moment the user rotates the key, the Memory entry becomes a zombie.

**Lesson:** Credentials, full paths, and version numbers are "environment facts." The source of truth is in config files. Memory should only hold a pointer like "Zhipu as backup provider; switch with /model."

### 5. Project completion misjudgment risk: leaving ≠ project over (user corrected directly, 2026-08-27)

The user left Kaihuai at the end of July, but on 8.27 was still writing Kaihuai rankings as the executor. If entries had been cleaned based on "departure = completed," it would have been a wrongful deletion.

**Lesson:** The Agent always learns about project status after the user. Completion is only confirmed when the user explicitly says so. Any inference (departure / discontinued / inactive) can only go into the review list, never be executed directly.

### 6. Progress number conflicting between two sources (2026-08-27)

"Psychology illustrated: 6 issues completed" was in Memory, but the Skill progress table showed only 1 finished + 1 pending illustration. The two sources didn't match.

**Lesson:** Progress numbers must only be updated in the source-of-truth layer (Skill table / production log). Progress numbers in Memory are snapshots; during scanning, use the source of truth as ground truth and write back.

### 7. Index gap: session_index.json stopped at July 8 (discovered 2026-08-27)

60 days of archive directories, but the index only covered 30 days (through 7-08); the 30 days after 7-09 had no index at all.

**Lesson:** Every time a router file is written, session_index.json must be updated in the same pass. Indexes and archives are one thing, not "archive first, index later" — it's "write the index when you write the archive."

### 8. 27 files scattered in root with no navigation (discovered 2026-08-27)

The personal decision support system root had 27 files/directories with no master index — no idea what to read first.

**Lesson:** The root directory must have a README master index with entry files, project directories, and quick navigation. Update the README after creating new files.

### 9. Indexes are not a separate layer; they are discipline built into every layer (2026-08-28 refactor)

Previously drew the "index layer" as a standalone fourth layer; turned out to be overengineering. The essence of indexing is self-indexing discipline in each layer (Memory entries are themselves pointers, doc directories have READMEs, Skills have descriptions) — not an additional file.

**Lesson:** Don't create a standalone index layer. Each layer carries its own indexing discipline, reducing maintenance burden.

### 10. Only governing memory = category isolation (2026-08-28 refactor)

The original skill only governed Memory, not docs or Skills — perpetuating the root cause of "duplicate rules fighting" (Memory had decluttering, docs had README rules, Skills had publishing rules; three rule sets that couldn't see each other).

**Lesson:** Governance must unify all categories (Memory / docs / Skills / pointers) with the same four questions. Otherwise it's as if nothing was governed.

### 11. Source of truth must be one git repo; all agents symlink to it (2026-08-28)

During setup, created two sources of truth: a Hermes local dev source + a GitHub copy, with other agents symlinking to the GitHub copy — the two could fall out of sync. Fixed by following the dbs official convention: source of truth = ldm-skill repo (git-managed), all agents (including Hermes) symlink to it; change one place, push = published.

**Lesson:** There can only be one source of truth, and it must be a git repo (with version history for rollback). Don't build a "dev source" under Hermes and have other agents read a GitHub copy.

### 12. Skill file-path references go stale; verify during scanning (2026-08-28 battle-tested)

The kaihuai-content-creation Skill's "reference files" section had 7 pointers, all broken: `04_素人投放计划/08_男性觉醒融合` was entirely archived to `_archive/old-direction_2026-08-03/`; 2 files didn't exist even in the archive, 3 were in the archive, 1 had a wrong path.

**Lesson:** When scanning, don't just check Memory pointers — also check file paths referenced in Skills. After directories are archived/moved, every Skill pointer referencing them breaks. Fix: exists → point to the new archive path; doesn't exist → delete the pointer and note "archived/old direction."

### 13. Root directory scattered docs = orphans; migrate into the right directory (2026-08-28 battle-tested)

`fitness-app-decision_V1.md` was scattered in the root, but the `decisions/` directory had 64 decisions — it belonged there. Similar docs: the root only keeps active running logs (daily output logs / project planning); all historical decisions go into `decisions/`.

**Lesson:** When the root has 10+ documents with no README navigation, check each one whether it should move into a subdirectory. Scattered = dark data.

### 14. Same-named file in knowledge-base and root = version fork (2026-08-28 battle-tested)

The knowledge-base/ versions of project-status/rules/user-preferences were updated (mid-to-late June); the same-named root files were older (early June). SOT rules were violated: two versions of the same document, neither stating "who is the source of truth."

**Lesson:** Source-of-truth documents (rules/preferences/status) may only exist in one place: `knowledge-base/`. Same-named old versions in the root must be deleted. During scanning, diff same-named files; different = fork; determine the source of truth by latest timestamp + content completeness.

### 15. Root README out of sync with actual structure (2026-08-28 battle-tested)

The Hermes_Workspace root README described "topic library / source material library / published / data analysis," but the reality was 18 real project directories — the README was written early in the project and never updated. Users following the README would find nothing.

**Lesson:** The root README must be periodically reconciled with the actual structure. During scanning, compare the README's described directories vs. the actual `ls` output; all mismatched = README is stale — rewrite it.

### 16. Same-named directory across locations = old copy (2026-08-28 battle-tested)

Root `douyin-transcript-extraction/` (8-09 old version) and `personal-decision-system/douyin-transcript-extraction/` (8-28 official version) were same-named duplicates. Judgment based on: modification time + content completeness (official version had README + full toolchain).

**Lesson:** When scanning finds same-named directories across locations, diff content + timestamps to determine the official version; mark the old one as "old working copy" pending user confirmation — don't delete directly.

### 17. Demoting ≠ deleting: details must be moved to a lower layer; information must not disappear (2026-08-29 battle-tested)

During memory cleanup, deleted the entire "Claude Code three APIs" entry, reasoning "environment config shouldn't be in Memory." The user pushed back: after you delete it, if I ask what the Zhipu API is or what Claude's three APIs are, how will you answer? — Does demoting mean deleting?

**Lesson:** The correct demotion action is "move details to a lower layer where they can be found + Memory keeps a one-line pointer" — not deletion. Execution order: ① Find the source of truth (config.yaml/.env/settings-*.json) → ② Confirm the source contains the full information → ③ Rewrite Memory as a pointer (pointing to the source file) → ④ Only information confirmed to have no source of truth anywhere may disappear. Deletion is only for "duplicate entries already consolidated into a Skill/docs." For anything that will be asked about again, before deleting you must be able to say "where to look it up."

### 18. Memory tool gotchas (2026-08-29~31 tested)

① Deletion must use `remove`; `replace` cannot accept empty content ② Entries may be merged with §; `old_text` must match the full entry text — matching only half gives "no entry matched"; on failure, check `current_entries` for real boundaries ③ Batch operations are all-or-nothing: one failure rolls back everything; the error identifies which operation # failed; fix it and resend the whole batch ④ When capacity is exceeded, new entries can't be written: within the same batch, you must shrink/merge old entries before adding new ones, and the shrink amount must ≥ the add amount; otherwise "would be over the limit" rolls back everything.

**Lesson:** The memory tool's gotchas all come from "wrong mental model" — not knowing entry boundaries or the budget mechanism leads to repeated failures. Consolidated: 2026-08-31.
