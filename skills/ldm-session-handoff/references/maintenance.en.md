# Maintaining This Skill

Read only when modifying this skill itself. Not needed for running a handoff.

## Edit only the source of truth

The source of truth is `skills/ldm-session-handoff/` in the ldm-skill repo. Each agent's install location is either a symlink or a copied directory; editing an installed copy makes the two diverge.

After editing the source, check each install location's form; don't assume from memory:

```bash
ls -la <agent skills dir>/ldm-session-handoff
```

- **Symlink** (`lrwxr-xr-x … -> …/ldm-skill/skills/ldm-session-handoff`): edits take effect immediately; read back to verify.
- **Copied directory** (`drwxr-xr-x`): resync, otherwise that agent keeps reading the old version:

```bash
rsync -a --exclude=__pycache__ --exclude='*.pyc' --exclude=.DS_Store \
  <ldm-skill>/skills/ldm-session-handoff/ <agent skills dir>/ldm-session-handoff/
```

Lesson (2026-09-24): symlinked and copied installs were once mixed on the same machine. One update survived only because that install happened to be a symlink; the copied ones still had the old version. Everything was then unified as symlinks.

Per platform:
- Hermes installs via symlink; `skill_manage` reports `not found in active profile`. Read back from the symlink path to verify.
- Grok is a thin bridge that only points to the source; it keeps no body text.

## After changing scripts

- Every script must pass `python3 -B -m py_compile`, then run on a minimal sample. Export scripts must export one real session: check that the header message count equals the body count and that the header has the redaction line.
- Run scripts with `-B` (or set `PYTHONDONTWRITEBYTECODE=1`) so no `__pycache__` lands in the repo.
- After changing the Chinese files, update the English ones (`SKILL.en.md`, `references/*.en.md`) or mark them as lagging.
