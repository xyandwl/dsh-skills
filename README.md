# DSH Skills

DeepSeek Harness（DSH）里正在使用的技能合集，托管成公开 GitHub 仓库，供 **技能管理器 → 技能仓库** 订阅安装与在线更新。

## 为什么用仓库托管

技能管理器只对「有安装来源记录」的技能提供 `刷新并检查更新 → 差异预览 → 备份替换 → 回滚`。手工放进 `skills/` 目录的技能是「裸目录」，没有来源，永远不会出现在更新里。装进技能仓库之后，每个技能都有 `installs` 记录（仓库 id + 路径 + commit + 逐文件哈希），更新链路才成立。

## 目录结构

```
<repo>/
├─ auto-updater/SKILL.md
├─ viral-copy/SKILL.md
├─ viral-copy/references/...
├─ douyin-video-copy/SKILL.md
├─ douyin-video-copy/dy_copy.py
└─ ...
```

每个一级目录就是一个技能，目录里必须有 `SKILL.md`（YAML frontmatter 至少含 `name` 和 `description`）。技能管理器按 `<目录>/SKILL.md` 扫描，目录名即仓库内技能路径。

## 安装

技能管理器 → 技能仓库 → 添加仓库 → `owner/repo`（或完整 GitHub 地址）→ 刷新 → 逐个安装到「全局 DSH」。

安装要求目标位置没有同名技能；同名会显示「同名冲突」，需要先把本机副本移入回收站。

## 发布方式

```bash
git add -A
git commit -m "skills: sync"
git push
```

本地目录约定：`D:\dsh-skills-repo`。

## 说明

- 不含任何密钥：`config.json`、`.dsh-skill-store.json`、`__pycache__` 已排除。
- 部分技能正文里保留了 `C:\Users\...` 形式的本机路径（脚本依赖），换机器时需要自行调整。
- 技能内容分别来自 SkillHub / ClawHub 与本地编写，许可见各技能目录内的 LICENSE（如有）。
