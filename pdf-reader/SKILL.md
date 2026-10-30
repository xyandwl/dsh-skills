---
name: pdf-reader
description: "读取 PDF 文件内容：页数、文本层、逐页正文、页内图片导出。适合合同、报告、画册、扫描件、几百 MB 的大 PDF。用户说「读一下这个 PDF」「PDF 里写了什么」「把 PDF 转成文字」「扫描件看不出来」时使用。"
---

# PDF 读取

读 PDF 不要自己手写解析，也不要凭文件名猜内容。直接用本技能目录里的 `pdf_read.py`：先看有没有文本层，有就抽文本，没有就把页面图片导出来看。

## 0. 用哪个 Python

本机器上 **DSH 自带的 Python 没有 pypdf，而且没网装不了**；`%USERPROFILE%\.local\lib\python312\python.exe` 里装了 pypdf 6.x 和 Pillow，**默认用它**。

```powershell
$py = "$env:USERPROFILE\.local\lib\python312\python.exe"
if (!(Test-Path $py)) { $py = "python" }   # 换机器时退回 PATH 上的 python
& $py "<本技能目录>\pdf_read.py" info "C:\path\file.pdf"
```

如果报 `缺少 pypdf`，才考虑 `$py -m pip install pypdf`（本机离线会失败，别硬试）。

## 1. 先摸清底细：info

```powershell
& $py "<本技能目录>\pdf_read.py" info "C:\path\file.pdf"
```

输出：大小、页数、标题/生产者、**文本层有没有**、每页字符数、无文本层页、疑似竖排/旋转文字页。

判断规则：

- `文本层：有` → 走 `text`，最省事。
- `文本层：没有` → 扫描件，走 `images` + 视觉读图。
- 字符数很少（每页 < 50）或列在「疑似竖排」里 → 文本会串字，那几页走 `images`。

## 2. 抽文本：text

```powershell
# 全文写入 md（推荐，几百页也稳）
& $py "<本技能目录>\pdf_read.py" text "C:\path\file.pdf" --out ".\xxx-text.md"

# 只读几页；表格多的合同加 --mode layout 保留版面
& $py "<本技能目录>\pdf_read.py" text "C:\path\file.pdf" --pages 1-5,12 --mode layout
```

`--pages` 支持 `1-10`、`3`、`1-3,7,20-`。大文件先 `info` 再分批 `--pages`，不要一次全读进上下文。

## 3. 看页面图：images

```powershell
& $py "<本技能目录>\pdf_read.py" images "C:\path\file.pdf" --pages 1-3 --out ".\pdf_pages" --max-width 1500
```

导出后用 `read_image` 逐张看（一次 1–3 张，别一口气 20 张）。`--max-width 1500` 控制体积和 token；看不清小字时提到 2200 再导一次。

## 4. 一次读到底的推荐流程

1. `info` → 判断每页是文本页还是图片页；
2. `text --out` 抽正文，通读；
3. 缺的页（无文本层 / 竖排）用 `images` 只导那几页，看细节；
4. 汇报时区分「PDF 里写的」和「从图上看出来的」，没读到的不编。

## 5. 已知边界（别浪费时间踩）

- **没有 OCR 引擎**（无 pytesseract/paddle，也无网装）：扫描件靠 `images` 导出后交给视觉模型读，中文识别基本够用，密集小字会有误差，关键数字要标注「图上读到，待核」。
- **不能把整页栅格化**：本机没有 PyMuPDF / LibreOffice，Edge 无头截图在沙箱下也被拦（`mojo platform_channel` 拒绝访问）。所以：
  - 扫描件（一页一张大图）→ `images` 直接可用；
  - **设计排版稿**（CorelDRAW / AI 导出的画册、海报）→ 一页由十几个图块拼成，`images` 导出来是碎片，不是整页效果。要整页视觉就请用户截图，或直接看碎片图 + 文本标签拼信息。
- 竖排/旋转文字由 pypdf 抽出来是逐字换行（「厅/展/题/主」这样），不是乱码，**别当成加密或字体问题**，转图看。
- 加密 PDF 会尝试空密码解密，失败就明确告诉用户要密码。
- 412 MB / 24 页的文件，`info` 与 `text` 约几十秒，正常，不要中途杀进程。

## 6. 输出习惯

- 长文本先存 `.md`（带 `## 第 N 页` 分页标记），再按需要摘段落。
- 引用具体条款、金额、日期时，标注页码，方便用户回查。
- 涉及隐私（证件、合同主体）只摘必要信息，不外扩。
