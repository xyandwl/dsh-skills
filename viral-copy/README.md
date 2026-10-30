# 爆款文案工坊 · viral-copy

> 给你的 AI 装上「能直接发出去」的文案手感：小红书笔记、短视频脚本、标题钩子、合规自检。

[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-SKILL.md-111827)](./SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e)](./LICENSE)
[![Language](https://img.shields.io/badge/语言-中文-dc2626)](#)
[![No deps](https://img.shields.io/badge/依赖-无-0ea5e9)](#)

一个 Skill 文件 + 一套可执行的方法论。不是「让 AI 写得好一点」，而是**给它硬约束，逼它写出能爆的结构**。

![爆款文案工坊](./market/social-preview.png)

---

## 为什么不是「直接让 AI 写一篇」

| | 随口让 AI 写 | 用这个 Skill |
| --- | --- | --- |
| 开头 | 「大家好，今天想聊聊…」 | 前两句必须有冲突或反常识结论 |
| 内容 | 形容词堆叠，「超级好用」 | 必须有数字、型号、价格、顺序 |
| 标题 | 给 1 条，很平 | 一次给 8 条，标注打法与理由 |
| 结构 | 一大段，无节奏 | 按平台结构分点，每点带可执行细节 |
| 结尾 | 「希望对你有帮助」 | 低门槛互动动作 |
| 合规 | 极限词、导流词随便写 | 自动扫词库，命中即替换建议 |
| 可复用 | 每次都要重新说一遍要求 | 方法论沉淀在 references，稳定复现 |

---

## 安装

支持 **Agent Skills** 的客户端（Claude Code、DeepSeek Harness、各类 agent 框架）本质都是「把目录放进 skills 搜索路径」。

```bash
# 全局安装（Claude Code 等）
git clone https://github.com/<your-name>/viral-copy.git ~/.claude/skills/viral-copy

# 或项目内安装
mkdir -p .claude/skills && git clone https://github.com/<your-name>/viral-copy.git .claude/skills/viral-copy
```

其他客户端：把整个 `viral-copy/` 目录放进它的 skills / rules 目录即可；只支持单文件的客户端，直接粘贴 `SKILL.md`。

> 兼容性：`SKILL.md` 使用标准 frontmatter（`name` + `description`），无需任何依赖，纯文本、零运行时。

---

## 30 秒上手

装好后，直接说人话：

```
写一篇小红书，我做小户型收纳，想涨粉
```

```
帮我把这段改成能爆的开头：<粘贴你的稿子>
```

```
我做职场效率内容，出 3 条 60 秒口播选题，要有反差感
```

```
这篇发出去没什么流量，帮我诊断一下问题在哪
```

它不会反问你 10 个问题，而是**先给默认假设 + 直接出稿**，再让你一句话纠正。

### 你会拿到什么

```markdown
# 标题候选（8 选 1，标注打法与理由）
# 封面文案（主标 ≤12 字 / 副标 ≤18 字）
# 正文（按平台结构，含 emoji、分段、互动收口）
# 标签（核心 3 + 长尾 4 + 泛流量 2）
# 评论区首评
# 自检：钩子 23 · 增量 22 · 传播 20 · 结构 23 = 88/100 + 下一版 A/B 假设
```

完整成品见 [`examples/`](./examples)：

- [小红书图文完整案例](./examples/01-xiaohongshu-note.md)（选题 8 条 → 标题 8 条 → 成稿 → 自检）
- [60 秒口播 + 分镜表](./examples/02-short-video-script.md)（含逐镜头画面与字幕）
- [烂稿改写诊断](./examples/03-rewrite-diagnosis.md)（27 分 → 85 分的具体改法）

---

## 它到底改了什么

核心是五条硬规则，全部写在 `SKILL.md` 里，每次都生效：

1. **先定人，再定文** —— 没有人群画像的稿件一律不合格。
2. **前 20% 决定 80%** —— 小红书前两行、短视频前 3 秒。
3. **具体胜过优美** —— 「3 个月从 4800 到 2.3 万」＞「实现了指数级增长」。
4. **一条只打一个点** —— 想同时说三件事 = 一件都没说。
5. **合规是底线** —— 极限词、导流词会直接限流，写完必查。

再加上 4 项 × 25 分的**爆款潜力评分卡**，低于 60 分不交付——它必须告诉你短板在哪，而不是丢给你一篇「看起来还行」的稿子。

---

## 仓库结构

```
viral-copy/
├── SKILL.md                     # 主流程：Step 0–5、默认交付格式、反模式
├── references/
│   ├── hook-matrix.md           # 六维钩子矩阵 + 三秒钩子句库 + 40 选 8 筛选法
│   ├── title-formulas.md        # 32 条标题公式 + 封面文案规范 + 自检 5 问
│   ├── xiaohongshu.md           # 小红书结构、排版、封面、标签、评论区运营
│   ├── short-video.md           # 3 秒钩、60 秒口播模板、分镜表、节奏字幕
│   ├── platform-rules.md        # 广告法极限词、功效/金融/教育承诺、导流红线
│   ├── scoring-rubric.md        # 爆款潜力评分卡与迭代优先级
│   └── banned-words.txt         # 可扩充的违禁/限流词库（词|类别|替换建议）
├── scripts/
│   └── check_banned_words.py    # 零依赖合规检查，命中即给替换建议
├── examples/                    # 三个完整成品案例
├── market/
│   └── listing.md               # 上架/推广文案（名称、卖点、长描述、社媒稿）
├── CONTRIBUTING.md              # 贡献标准与词库格式
├── CHANGELOG.md
└── PUBLISH.md                   # 发布到 GitHub 的 5 步清单
```

## 合规检查脚本

零依赖，只要有 Python 3.9+：

```bash
python scripts/check_banned_words.py 稿件.md
```

```
⚠️  命中 5 处：绝对化 3，导流 2

稿件.md:1:13  【绝对化】全网最低
    … 这是我用过最好的面霜，全网最低价，7天见效
    → 改成对比价格事实
```

退出码：干净 `0`，命中 `1`。支持 `--json` 供流水线使用。词库是纯文本，**加一行就多一条行业规则**：

```
我的行业内部词|绝对化|改成 XX
```

## 自定义成你自己的

1. **加行业词**：编辑 `references/banned-words.txt`，一行一条。
2. **换语气**：在 `SKILL.md` 的「五条原则」下加一句人设，例如「你的读者是 40+ 男性，别用网络梗」。
3. **加平台**：复制 `references/xiaohongshu.md` 改成你的平台（公众号、知乎、B 站），并在 `SKILL.md` 的参考文件表里挂上。
4. **加案例**：往 `examples/` 丢你自己的爆款，AI 会照着它的密度写——这是提升效果最快的一步。

## FAQ

**Q：会让内容变成 AI 味吗？**
A：反了。它的主要工作是删掉 AI 味：禁止开场问候、禁止“希望对你有帮助”、禁止形容词堆叠，强制要求具体数字和失败经历。

**Q：我不是做自媒体的，有用吗？**
A：写周报开头、写产品介绍、写社群通知、写招聘 JD 都能用同一套「钩子—递进—收口」骨架。

**Q：数据会外传吗？**
A：整个仓库是纯文本 prompt + 一个本地 Python 脚本，无网络请求、无遥测。

**Q：能保证爆吗？**
A：不能，也没有任何东西能。它保证的是：**每条内容都有一个明确的爆款假设，且可以被下一次 A/B 验证**。

## 同一套方法论的其它 skill

这个仓库只解「内容」这一段。同一套「硬约束 + 可验证脚本」的写法，还有职场侧的五个：

| 仓库 | 解决什么 | 自检脚本 |
| --- | --- | --- |
| [`resume-tailor`](https://github.com/zhbehx/resume-tailor) | JD → 简历对岗改写 | 关键词覆盖率 / 量化率 / 弱动词 |
| [`interview-coach`](https://github.com/zhbehx/interview-coach) | 8 个 STAR 故事 + 三层追问链 | STAR 四要素 / 数字 / 空话句 |
| [`weekly-report`](https://github.com/zhbehx/weekly-report) | 周报月报 / 汇报 / 述职 | 结论位置 / 无数字 / 风险缺方案 |
| [`slide-story`](https://github.com/zhbehx/slide-story) | PPT 叙事大纲与页标题 | 废页 / 判断句检测 / 页数 |
| [`meeting-actions`](https://github.com/zhbehx/meeting-actions) | 纪要 → 决策 / 行动项 / 待定 | 责任人 / 产物 / 期限三要素 |

共同点：**零依赖、中文优先、每个 skill 都带一个确定性检查脚本**——它们不是提示词汇编，是能被 CI 验证的工具。

## 贡献

欢迎 PR：新增平台参考文件、扩词库、补案例。请保持「具体、可执行、无反模式」的写法——形容方法论好坏的最好方式是给例子。

## License

[MIT](./LICENSE) · 随意使用、修改、商用。
