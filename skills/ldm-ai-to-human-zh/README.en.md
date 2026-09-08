# ldm-ai-to-human-zh

Review or rewrite Chinese content to reduce mechanical, vague, uniform, and templated AI traces while preserving the author's viewpoint and voice.

## Install

```bash
npx -y skills add Holden323/ldm-skill --skill ldm-ai-to-human-zh -g
```

## Usage

Just say something like:

- "Check this draft for AI traces. Report only."
- "Rewrite this to sound human. Keep the original viewpoint and length."
- "Review and rewrite this file, save as V2."

The skill will choose review, rewrite, or both based on your request — it won't force a confirmation step first.

## Files

- `SKILL.md`: Agent-facing entry point and core workflow.
- `references/editing-guide.md`: Loaded on demand for systematic review and major rewrites.
- `scripts/hanyihan_qc.py`: Mechanical signal scanner. Results always need contextual judgment.

Automated scanning cannot judge whether an article "sounds human" — it is only for quickly spotting potentially repetitive or stiff expressions.
