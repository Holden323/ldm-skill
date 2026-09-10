# LDM-skill

**李大魔的 AI Skills 合集。** 每个 skill 都来自真实工作流里踩过的坑，先在自己身上用顺，再拿出来。

支持：Hermes / Claude Code / Codex / 豆包 / WorkBuddy 等任何支持 Skills 的 Agent。

简体中文 | [English](README.en.md)

---

## 一句话安装

```bash
npx -y skills add Holden323/ldm-skill -g --all
```

安装后你的 Agent 会自动按需加载这些 skill。也可以只装一个：

```bash
npx -y skills add Holden323/ldm-skill --skill ldm-ai-to-human-zh -g
```

---

## 合集里有什么

### 1. AI 人味儿汉译汉（ldm-ai-to-human-zh）

**把 AI 写的中文改成人话。**

你用 AI 写了一段中文，总觉得哪里不对——太光滑、太均匀、太"正确"，别人一眼看出是 AI 写的。这个 Skill 提供精简入口、按需审稿参考和 Python 候选信号扫描脚本。

| 问题 | 表现 |
|------|------|
| 句式暴露 | "不是X，而是Y""你以为X，其实Y"满屏都是 |
| 标点断裂 | 每句句号断开，读起来像机器人 |
| 词汇书面 | "此外""事实上""值得注意的是"扎堆 |
| 内容光滑 | 没有毛边，没有任何一处是作者自己也没想通的 |

用法：跟 Agent 说“检查这篇稿子的 AI 痕迹”或“把这段改得像人话”。直接要求改写时会直接完成；处理文件且未指定覆盖时，默认输出下一个版本。

详见 [skills/ldm-ai-to-human-zh](./skills/ldm-ai-to-human-zh/)。

### 2. 认知资产统一治理（ldm-memory-system）

**给 AI 的记忆建一套"断舍离+对账"制度。**

AI 的记忆用久了会得三种病：只进不出越堆越满、指针失效没人管（记的飞书链接早改版了）、同一规则存三处互相打架。你让它"清理一下"，它可能上来就乱删——删完你再问"我的 API 配置是啥"，它俩大眼瞪小眼。

这套 Skill 给 Agent 一套统一四问：**住哪层？真源在哪？还准吗？有索引吗？** 每条记忆、每个文档、每个 Skill 都按任务范围检查；该搬的搬（降级=详情搬到低层+留指针），该删的删（范围不明时先列清单确认）。

| 机制 | 干什么 |
|------|--------|
| 四问框架 | Memory/文档/Skill/指针统一体检，不分类目一套问法 |
| 三层架构 | Skill=操作手册、文档=项目资料库、Memory=随身小本子，各住各的层 |
| SOT链 | 一条知识只允许一个真身，其他地方最多放指针 |
| scan.py | 机械扫描脚本，6类确定性检查，只报告不动手 |

用法：跟 Agent 说 **"清理 memory"** 或 **"memory 体检"**，它会按范围检查并给出处置建议；批量范围不明时先列清单确认。

详见 [skills/ldm-memory-system](./skills/ldm-memory-system/)。

### 3. AI交接班三件套（ldm-session-handoff）

**AI 没有记性，但可以交接班。**

每次开新会话都要把背景重新讲一遍？会话崩了半小时铺垫全没了？让 AI 自己写总结再喂回去，它转述的记录会丢细节、甚至编造？

这套流程给你的 Agent 建一套交接班制度。每次会话结束产出**两个文件 + 一段提示语**：

| 产物 | 作用 | 给谁看 |
|------|------|--------|
| ① 对话全记录 | 从本地数据库逐条导出的原始对话（附导出脚本），可追溯可核查 | 人（档案原件） |
| ② 路由器 | 关键决策、存档点、产出清单、资源版本、下一步与前置条件，一页看完。恢复上下文靠它 | 人和AI（导航图） |
| ③ 重启提示语 | 一段文字，贴进新会话，指向路由器并交代约束 | AI（交接单） |

核心原则只有一条：**恢复上下文需要档案原件，不是转述。** 所以全记录必须从数据库直读导出，禁止摘要冒充。分工上，原文负责回查，路由器负责恢复，重启提示语只是入口。

用法：跟 Agent 说 **"准备退出重启，记录对话全记录"**，或单独跑脚本：
`python3 skills/ldm-session-handoff/scripts/export_transcript.py --list`

详见 [skills/ldm-session-handoff](./skills/ldm-session-handoff/)。

### 4. 个人实证追踪（ldm-empirical-life-tracker）

把重要想法、预测、决策和结果连接成可追溯的个人证据，支持记录、回填、复盘和低风险个人实验。它区分事实、体验、解释与假设，不从少量记录推断稳定人格，也不会在未获授权时扫描或写入私人数据。

详见 [skills/ldm-empirical-life-tracker](./skills/ldm-empirical-life-tracker/)。

### 5. 夹叙夹议写作（ldm-narrative-commentary-writing）

把已经确定的事件型或观点型选题写成事实可靠、叙议交替、普通读者容易理解的中文长文。支持直接成稿、结构设计和审稿，并按任务需要加载事实核查、六拍节奏、文风与可读性参考。

详见 [skills/ldm-narrative-commentary-writing](./skills/ldm-narrative-commentary-writing/)。

---

## 设计原则

1. **只收脱敏后的通用方法论。** 项目相关的私有 skill 不进合集。
2. **每个 skill 必须在作者自己的日常工作中真实用过。** 没跑过的不上架。
3. **机制优先于工具。** Skill 里写清楚“为什么这么做”，换一个 Agent 也能照着迁移。
4. **入口轻、细节分层。** 每个 Skill 的 SKILL.md 只保留触发、决策和资源路由，长案例与平台细节按需读取。

## 更新日志

- **2026-09-10** — ldm-session-handoff 路由器改版：新增存档点、资源版本、下一步与前置条件；明确重启提示语只是入口，恢复由路由器承担
- **2026-09-07** — 纳入 ldm-empirical-life-tracker 与 ldm-narrative-commentary-writing；统一多 Agent 真源
- **2026-08-29** — 新增 ldm-memory-system（认知资产统一治理）；README成员链接对齐改名后的目录（ldm-前缀）
- **2026-08-26** — 仓库升级为合集 ldm-skill；新增 agent-session-handoff（AI交接班三件套）

## 许可

MIT License
