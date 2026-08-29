# LDM-skill

**李大魔的 AI Skills 合集。** 每个 skill 都来自真实工作流里踩过的坑，先在自己身上用顺，再拿出来。

支持：Hermes / Claude Code / Codex / 豆包 / WorkBuddy 等任何支持 Skills 的 Agent。

---

## 一句话安装

```bash
npx -y skills add Holden323/ldm-skill -g --all
```

安装后你的 Agent 会自动按需加载这些 skill。也可以只装一个：

```bash
npx -y skills add Holden323/ldm-skill --skill ai-to-human-zh -g
```

---

## 合集里有什么

### 1. AI 人味儿汉译汉（ai-to-human-zh）

**把 AI 写的中文改成人话。**

你用 AI 写了一段中文，总觉得哪里不对——太光滑、太均匀、太"正确"，别人一眼看出是 AI 写的。这个 skill 是 14 年文字老编辑踩坑实录，9 章方法论 + Python 自动扫描脚本 + 实战改前改后对照。

| 问题 | 表现 |
|------|------|
| 句式暴露 | "不是X，而是Y""你以为X，其实Y"满屏都是 |
| 标点断裂 | 每句句号断开，读起来像机器人 |
| 词汇书面 | "此外""事实上""值得注意的是"扎堆 |
| 内容光滑 | 没有毛边，没有任何一处是作者自己也没想通的 |

用法：跟 Agent 说 **"帮我跑汉译汉"**，它会先出审查报告，确认后再改，输出新版本文件。

详见 [skills/ai-to-human-zh](./skills/ai-to-human-zh/)。

### 2. AI交接班三件套（ldm-session-handoff）

**AI 没有记性，但可以交接班。**

每次开新会话都要把背景重新讲一遍？会话崩了半小时铺垫全没了？让 AI 自己写总结再喂回去，它转述的记录会丢细节、甚至编造？

这套流程给你的 Agent 建一套交接班制度。每次会话结束产出**两个文件 + 一段提示语**：

| 产物 | 作用 | 给谁看 |
|------|------|--------|
| ① 对话全记录 | 从本地数据库逐条导出的原始对话（附导出脚本），可追溯可核查 | 人（档案原件） |
| ② 路由器 | 关键决策、产出清单、当前进度、待办，一页看完 | 人和AI（导航图） |
| ③ 重启提示语 | 一段文字，贴进新会话即恢复全部上下文 | AI（交接单） |

核心原则只有一条：**恢复上下文需要档案原件，不是转述。** 所以全记录必须从数据库直读导出，禁止摘要冒充。

用法：跟 Agent 说 **"准备退出重启，记录对话全记录"**，或单独跑脚本：
`python3 skills/ldm-session-handoff/scripts/export_transcript.py --list`

详见 [skills/ldm-session-handoff](./skills/ldm-session-handoff/)。

---

## 设计原则

1. **只收脱敏后的通用方法论。** 项目相关的私有 skill 不进合集。
2. **每个 skill 必须在作者自己的日常工作中真实用过。** 没跑过的不上架。
3. **机制优先于工具。** skill 里写清楚"为什么这么做"，换一个 Agent 也能照着迁移。

## 更新日志

- **2026-08-26** — 仓库升级为合集 ldm-skill；新增 agent-session-handoff（AI交接班三件套）

## 许可

MIT License
