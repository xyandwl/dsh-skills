# 上架 / 推广文案（GitHub + 社媒）

直接复制粘贴用。占位符 `<your-name>` 替换成你的 GitHub 用户名。

---

## 一、GitHub 仓库元信息

**Repository name**：`viral-copy`

**About（一句话，≤120 字符，会显示在搜索结果里）**：

```
给你的 AI 装上能直接发出去的文案手感：小红书笔记 / 短视频脚本 / 标题钩子 / 合规自检。Agent Skill，零依赖。
```

英文版备选：

```
Agent Skill for viral short-form copy: Xiaohongshu notes, short-video scripts, hooks, titles, and a compliance linter. Zero deps.
```

**Topics（标签，选 10–15 个，决定能不能被搜到）**：

```
agent-skills  claude-skills  ai-agents  prompt-engineering  copywriting
xiaohongshu  douyin  short-video  content-marketing  growth-hacking
chinese  markdown  python  cli-tool  marketing-automation
```

**Social preview**：用 1280×640 图，左边大字 `爆款文案工坊`，右边 `27 分 → 85 分`，底部 `viral-copy · Agent Skill`。

---

## 二、Release v1.0.0

**Tag**：`v1.0.0`
**Title**：`v1.0.0 — 首个可发布版本：从选题到成稿到合规检查`

```markdown
## 这是什么

一个 Agent Skill：让 AI 按硬约束写小红书笔记、短视频脚本和标题，而不是给你一篇「看起来还行」的稿子。

## 包含

- **工作流**：Step 0 定人群 → 选题 8 条 → 标题 8 条 → 按平台结构写稿 → 评分卡自检
- **方法论库**：六维钩子矩阵、32 条标题公式、小红书/短视频平台手册、爆款潜力评分卡
- **合规检查**：`check_banned_words.py`，零依赖，命中即给替换建议（不是简单报错）
- **3 套完整案例**：小红书图文、60 秒口播分镜、烂稿改写（27 分 → 85 分）

## 安装

git clone https://github.com/<your-name>/viral-copy.git ~/.claude/skills/viral-copy

## 已验证

- 评分卡与合规脚本在 3 个案例上跑通
- 纯文本 + 单个 Python 脚本，无网络请求、无遥测

## 已知限制

- 平台规则随政策变化，`references/platform-rules.md` 需定期更新
- 中文优先；英文平台（TikTok/X）参考文件尚未提供，欢迎 PR
```

---

## 三、社媒发布稿

### 3.1 小红书 / 公众号（中文，主推）

**标题（8 选 1）**
1. 我把「怎么写爆款」拆成了 AI 能执行的 5 条硬规则
2. 同一个 AI，为什么别人写出来能爆，你写出来像通稿
3. 给 AI 装了个「爆款文案」技能包，27 分的稿子改到 85 分
4. 别再让 AI「帮我写篇小红书」了，它缺的是约束
5. 开源了一个文案 Skill：选题、标题、脚本、违禁词全包了
6. 文案写不好不是 AI 的问题，是它不知道这 5 条规矩
7. 我做了一个能自动查违禁词的开源文案工具，免费用
8. 从选题到成稿到合规检查，我把这套流程开源了

**正文**

> 我发现一个事：让 AI「帮我写篇小红书」，出来的东西永远是同一个味道——「大家好，今天想跟大家聊聊」。
>
> 不是模型不行，是我们给的要求太软。软要求只能得到软结果。
>
> 所以我把这套东西拆成了硬约束，做成了一个开源的 Agent Skill：
>
> 1️⃣ **开头不许问候**。前两句必须是一个冲突或反常识结论。小红书前两行、短视频前 3 秒，决定 80%。
> 2️⃣ **必须给 8 条标题**，每条标注打法（数字型/反差型/身份型/痛点型/好奇缺口）和「为什么它会点开」。只给 1 条标题的，是没做工作。
> 3️⃣ **必须有具体数字**。3 个月、268 块、40 分钟。「效率翻倍」这种词一律删掉。
> 4️⃣ **一条只打一个点**。想同时说三件事 = 一件都没说。
> 5️⃣ **写完必查违禁词**。极限词、导流词会直接限流，这是最容易白干的地方。我顺手写了个脚本，零依赖，命中直接给替换建议，不是简单报个错。
>
> 还有一张 4×25 分的评分卡：钩子、信息增量、传播动机、结构合规。低于 60 分它不许交稿，必须告诉我短板在哪。
>
> 仓库里放了 3 套完整案例，包括一篇烂稿从 27 分改到 85 分的全过程对照——哪一句为什么改，都标了。
>
> MIT，随便用。装法就一行 git clone。
>
> 你最想让 AI 帮你写哪类内容？评论区说一个，我看看要不要加平台模板 👇
>
> `#AI工具` `#文案` `#自媒体运营` `#开源` / `#小红书运营` `#短视频脚本` `#AI写作` `#提示词` / `#我的工作流`

**首评**

> 补充：它不会反问你十个问题。信息不全时先给默认假设，把稿子写出来，再让你一句话纠正。我觉得这才是 AI 该有的工作方式——先干，再对齐。

### 3.2 X / Twitter（英文）

```
Most "AI writes my copy" prompts fail for one reason: soft instructions.

So I open-sourced an Agent Skill with hard constraints:

→ no "hey everyone" openers (first 2 lines must be a conflict)
→ always 8 titles, each labeled with its hook type
→ no adjective without a number
→ one post = one point
→ banned-word linter built in (zero deps)

It scores itself 4×25 before delivering. Under 60 = rewrite, not ship.

Includes 3 worked examples, one going from 27/100 to 85/100 with line-by-line rationale.

Chinese-first (Xiaohongshu / Douyin). MIT.

github.com/<your-name>/viral-copy
```

### 3.3 Hacker News（Show HN）

```
Show HN: Viral-copy – an Agent Skill that enforces copywriting constraints

I kept getting the same bland output from "write me a social post" prompts, so I
moved the requirements out of the prompt and into a skill file that the agent has
to follow: mandatory 8-title pass with labeled hook types, ban on greeting openers,
ban on adjectives without a number, one-point-per-post rule, and a 4×25 scoring
rubric that blocks delivery under 60.

It ships with a zero-dependency Python linter for advertising-law / platform
banned words (Chinese platforms), which returns replacement suggestions instead of
just flagging.

Everything is plain text plus one script — no network calls, no telemetry.

Caveat: the platform references are Chinese-first (Xiaohongshu, Douyin) and
platform rules change, so that file needs maintenance. English-platform
references are the obvious PR.

github.com/<your-name>/viral-copy
```

---

## 四、首周推广清单

| 渠道 | 动作 | 备注 |
| --- | --- | --- |
| GitHub | 发 Release，打 `good-first-issue` 标签 | 3 个入门 issue：英文平台参考、B 站模板、词库扩充 |
| 小红书 | 用 3.1 正文 + 一张「27 分 vs 85 分」对比图 | 封面主标：`AI 写文案的 5 条硬规矩` |
| 即刻 / V2EX | 发「我做了一个文案 Skill」+ 讲清一个反常识点 | 不要贴大段 README，讲一个点即可 |
| X | 3.2 英文串 | 配一张评分卡截图 |
| Hacker News | Show HN | 周二至周四 UTC 14:00–16:00 发 |
| 微信群 / 社群 | 只发一句话 + 链接 | 「做了个查违禁词的小工具，顺手开源了」 |

## 五、让仓库更容易被 star 的三个细节

1. **README 前 6 行必须说清「不用它会怎样」**——对比表比功能列表有效 10 倍（已放）。
2. **每个 claims 后面跟一个可验证的东西**：说「有评分卡」就贴分数，说「能查违禁词」就贴终端输出（已放）。
3. **降低贡献门槛**：写清「加一行就多一条行业规则」，让 PR 变成 30 秒的事（已放）。
