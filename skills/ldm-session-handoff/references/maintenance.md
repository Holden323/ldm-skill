# 维护本 Skill

只有修改这个 Skill 本身时才需要读。执行交接时不用读。

## 只改真源

真源在 ldm-skill 仓库的 `skills/ldm-session-handoff/`。各 Agent 的安装位置要么是软链，要么是复制目录，改安装副本会让两边分叉。

改完真源，先看清每个安装位置是哪种形态，不要凭记忆假设：

```bash
ls -la <Agent 的 skills 目录>/ldm-session-handoff
```

- **软链**（`lrwxr-xr-x … -> …/ldm-skill/skills/ldm-session-handoff`）：真源改了就生效，直接读回验证。
- **复制目录**（`drwxr-xr-x`）：要重新同步，否则那个 Agent 读到的还是旧版：

```bash
rsync -a --exclude=__pycache__ --exclude='*.pyc' --exclude=.DS_Store \
  <ldm-skill>/skills/ldm-session-handoff/ <Agent 的 skills 目录>/ldm-session-handoff/
```

教训（2026-09-24）：同一台机器上曾经软链和复制两种形态混用。一次更新只因为恰好是软链才没丢，复制的那几个都还是旧版。之后统一成了软链。

各平台说明：
- Hermes 用软链安装，`skill_manage` 会报 `not found in active profile`。改完从软链路径读回验证。
- Grok 是 thin bridge，只指向真源，不维护正文。

## 改脚本之后

- 每个脚本都要过 `python3 -B -m py_compile`，再用最小样例跑一遍。导出脚本要用真实会话导出一次，核对文件头的消息数和正文条数是否相等，并确认文件头有「打码」行。
- 跑脚本加 `-B`（或设 `PYTHONDONTWRITEBYTECODE=1`），不在仓库里留 `__pycache__`。
- 中文版改动后，英文版（`SKILL.en.md`、`references/*.en.md`）要标明落后，或者同步更新。
