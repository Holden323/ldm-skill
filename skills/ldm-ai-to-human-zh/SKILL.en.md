---
name: ldm-ai-to-human-zh
description: >
  Rewrite or review Chinese content to reduce mechanical, uniform, vague, and templated AI traces
  while preserving the author's viewpoint and voice. Triggered when the user says "去 AI 味"
  (remove AI smell), "改得像人话" (make it sound human), "汉译汉" (Chinese-to-Chinese rewrite),
  "检查 AI 痕迹" (check for AI traces), or requests Chinese colloquial polishing.
  Not triggered for ordinary proofreading, factual research, or style imitation.
---

# Chinese AI-to-Human Rewriting

The goal is to make text sound like a specific person expressing themselves in a specific context — not a mechanical swap of "high-frequency AI words."

## Determine what the user wants first

- **Review only:** Surface the most impactful candidate issues with a few representative examples; do not modify the original.
- **Rewrite directly:** Complete the rewrite without pausing to ask for confirmation.
- **Review then rewrite:** Summarize key findings first, then deliver the rewritten result.
- When the user specifies tone, length, platform, or content to leave unchanged, those requirements take priority.

If the input is inline chat text, return directly in the conversation. If it is a file, follow the user's preferred saving method; when overwrite is not specified, preserve the original and create the next `_V2/_V3` version by default.

## Method

Read through the full text and confirm four things: what the author wants to say, who the audience is, where it will be published, and which facts or expressions must not change. Only ask for missing information if it would materially change the outcome; otherwise, infer reasonably from context.

When rewriting, prioritize:

- **Vague judgments:** Replace with facts, actions, scenes, or perceivable details.
- **Templated patterns:** Reduce consecutive use of the same transitions, parallel structures, rhetorical questions, and summary formulas.
- **Fabricated identity:** Do not invent experiences, friends, interviews, or eyewitness accounts on the author's behalf.
- **Monotonous rhythm:** Adjust sentence length, paragraph breaks, and pauses by genre; do not deliberately introduce rough edges.
- **Jargon and boilerplate:** Use simple, precise language instead of presentation-speak, report-speak, or ad-speak.
- **Over-explanation:** When a point or story already lands, cut the redundant summary and forced epiphany.

These are contextual signals, not global banned words. Dashes, parallelism, three-part structures, technical terms, and contrasts can be preserved when the genre calls for them. Do not add grammatical errors, digressions, unverified details, or emotional outbursts just to "sound human."

## Authenticity boundaries

- Do not add unverifiable data, quotes, cases, or personal anecdotes.
- When the original contains suspicious facts, flag them or rewrite conservatively; do not fabricate sources during polishing.
- Fictional settings must retain their fictional nature and must not be disguised as facts.
- Preserve the author's core position, information density, and key qualifiers unless the user explicitly asks for a viewpoint rewrite.

## Tools and references

When processing local files with many mechanical signals, run:

```bash
python3 scripts/hanyihan_qc.py <article-path>
```

Script output is candidate signals only — always judge in context and by genre; never determine quality by hit count.

For systematic review or major rewrites, load [references/editing-guide.md](references/editing-guide.md). Simple polishing does not require the full reference.

## Output

By default, deliver only the result the user asked for. Review reports are ranked by impact, explaining "what's unnatural, why, and how to fix it." Rewritten results do not include lengthy self-praise or line-by-line explanations. Provide a change list only when the user requests a comparison.

Before finishing: verify that the viewpoint has not been swapped, facts have not been fabricated, genre and length meet requirements, obvious template repetition has been reduced, and the text reads smoothly while still sounding like the original author.
