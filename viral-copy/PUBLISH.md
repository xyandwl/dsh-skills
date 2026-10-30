# 发布到 GitHub：5 步

> 当前机器上没检测到 `git`，先在命令行确认：`git --version`。
> 若未安装：Windows 用 `winget install --id Git.Git -e`，或到 https://git-scm.com/downloads 下载。

## 第 1 步 · 本地建仓并首次提交

在本仓库根目录（`viral-copy/`）执行：

```bash
git init
git add .
git commit -m "feat: viral-copy v1.0.0 — 爆款文案 Agent Skill"
git branch -M main
```

提交前确认没有把草稿带上去：

```bash
git status
```

应该只有：`SKILL.md` `README.md` `LICENSE` `CHANGELOG.md` `CONTRIBUTING.md` `PUBLISH.md` `.gitignore` `references/` `scripts/` `examples/` `market/`。

## 第 2 步 · 在 GitHub 建空仓库

1. https://github.com/new
2. Repository name：`viral-copy`
3. 可见性：**Public**（要传播就必须 public）
4. **不要**勾选 README / .gitignore / license（本地已有）
5. Create repository

## 第 3 步 · 推送

```bash
git remote add origin https://github.com/<your-name>/viral-copy.git
git push -u origin main
```

用 SSH 的话：`git@github.com:<your-name>/viral-copy.git`。
推送会要求登录：用 GitHub 的 **Personal Access Token** 当密码（Settings → Developer settings → Tokens），不要用账号密码。

## 第 4 步 · 配置 About 与 Topics（决定能不能被搜到）

仓库首页右侧齿轮 ⚙️ → About：

- Description：从 `market/listing.md` 第一节复制
- Topics：同样在 `market/listing.md` 第一节（10–15 个）
- Social preview：上传 `market/social-preview.png`（1280×640，已生成；改文案后跑 `python market/make_social_preview.py` 重新生成）

## 第 5 步 · 发 Release + 第一批 issue

**Release**：Releases → Draft a new release

- Tag：`v1.0.0`　Title：`v1.0.0 — 首个可发布版本`
- 说明：复制 `market/listing.md` 第二节

**第一批 issue**（给仓库“有生命”的信号，也降低贡献门槛）：

1. `good first issue` — 补充 TikTok / LinkedIn 英文平台参考文件
2. `good first issue` — 扩充医美、母婴、教培三个行业违禁词
3. `help wanted` — 增加 B 站与公众号两套平台手册
4. `enhancement` — 评分卡做成可交互的小网页

**顺便开启**：Settings → 勾选 Issues、Discussions；Insights → Community Standards 里补齐（LICENSE/README/CONTRIBUTING 都已有，会自动通过）。

---

## 推广（首周）

按 `market/listing.md` 第三节执行：

| 渠道 | 素材位置 |
| --- | --- |
| 小红书 / 公众号 | listing.md 3.1（标题 8 选 1 + 正文 + 首评） |
| X / Twitter | listing.md 3.2 |
| Hacker News Show HN | listing.md 3.3 |
| 社群 / 即刻 / V2EX | listing.md 第四节表格 |

## 发布前 60 秒自检

- [ ] `python scripts/check_banned_words.py examples/*.md` 全部通过
- [ ] README 渲染正常（表格、代码块、图片链接）
- [ ] 仓库里没有真实客户稿件、手机号、聊天截图
- [ ] About 描述与 Topics 已填
- [ ] LICENSE 年份与作者名已改（当前是 `viral-copy contributors`，建议换成你的名字）
