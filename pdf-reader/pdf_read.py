# -*- coding: utf-8 -*-
"""pdf_read.py — 读取 PDF：页数、元数据、文本层、页内图片。

用法：
  python pdf_read.py info   <file.pdf>
  python pdf_read.py text   <file.pdf> [--pages 1-10,15] [--mode plain|layout] [--out out.md]
  python pdf_read.py images <file.pdf> [--pages 1-3] [--out DIR] [--max-width 1500] [--format png]
  python pdf_read.py plan   <file.pdf> [--pages 1-20]

依赖：pypdf（必需）、Pillow（images 命令用）。
扫描件 / 竖排文字页没有可用文本层，用 images 导出页面图，再交给视觉模型读。
"""
import argparse
import io
import os
import sys

CTRL = "".join(chr(c) for c in list(range(0, 9)) + list(range(11, 13)) + list(range(14, 32)))


def fail(msg, code=2):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(code)


def clean_text(t):
    if not t:
        return ""
    t = t.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    t = "".join(ch for ch in t if ch not in CTRL)
    lines = [ln.rstrip() for ln in t.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def read_pdf(path):
    if not os.path.isfile(path):
        fail("文件不存在：%s" % path)
    try:
        from pypdf import PdfReader
    except Exception:
        fail("缺少 pypdf。先执行 python -m pip install pypdf；\n"
             "若本机无网络，换用已装 pypdf 的解释器（例如 ~/.local/lib/python312/python.exe）。")
    size = os.path.getsize(path)
    try:
        reader = PdfReader(path, strict=False)
    except Exception as e:
        fail("打不开这个 PDF：%s" % e)
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            fail("PDF 有密码，先解除保护再读。")
    return reader, size


def parse_pages(spec, total):
    if not spec:
        return list(range(1, total + 1))
    out = []
    for part in spec.replace("，", ",").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            a = 1 if a.strip() == "" else int(a)
            b = total if b.strip() == "" else int(b)
            out.extend(range(a, min(b, total) + 1))
        else:
            n = int(part)
            if n <= total:
                out.append(n)
    return sorted({p for p in out if 1 <= p <= total})


def page_text(page, mode="plain"):
    try:
        if mode == "layout":
            return clean_text(page.extract_text(extraction_mode="layout"))
        return clean_text(page.extract_text())
    except Exception:
        try:
            return clean_text(page.extract_text())
        except Exception:
            return ""


def looks_vertical(t):
    lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
    if len(lines) < 8:
        return False
    short = sum(1 for ln in lines if len(ln) <= 2)
    return short / len(lines) > 0.5


def cmd_info(path):
    reader, size = read_pdf(path)
    total = len(reader.pages)
    meta = {}
    try:
        meta = reader.metadata or {}
    except Exception:
        pass
    print("文件：%s" % os.path.abspath(path))
    print("大小：%.2f MB" % (size / 1024 / 1024))
    print("页数：%d" % total)
    for k in ("/Title", "/Author", "/Producer", "/Creator", "/CreationDate"):
        v = meta.get(k) if hasattr(meta, "get") else None
        if v:
            print("%s：%s" % (k.lstrip("/"), v))
    chars, img_pages, vert_pages = [], [], []
    for i, page in enumerate(reader.pages, 1):
        t = page_text(page)
        n = len(t.strip())
        chars.append(n)
        if n and looks_vertical(t):
            vert_pages.append(i)
        if n == 0:
            img_pages.append(i)
    total_chars = sum(chars)
    print("文本层：%s（共 %d 字符）" % ("有" if total_chars else "没有", total_chars))
    if total_chars:
        print("每页字符数：%s%s" % (",".join(str(c) for c in chars[:40]), "..." if total > 40 else ""))
    if img_pages:
        print("无文本层页：%d 页，例如 %s → 用 images 命令转图" % (len(img_pages), img_pages[:12]))
    if vert_pages:
        print("疑似竖排/旋转文字页：%s → 文本会串字，建议转图" % vert_pages[:12])
    if not total_chars:
        print("\n下一步：python pdf_read.py images \"%s\" --pages 1-5 --out ./pdf_pages" % path)


def cmd_text(path, pages, mode, out):
    reader, _ = read_pdf(path)
    total = len(reader.pages)
    sel = parse_pages(pages, total)
    chunks, empty, vert = [], 0, []
    for i in sel:
        t = page_text(reader.pages[i - 1], mode)
        if not t.strip():
            empty += 1
            note = "[本页无文本层，用 images 命令转图看]"
        else:
            note = t
            if looks_vertical(t):
                vert.append(i)
                note = t + "\n[提示：本页像是竖排/旋转文字，原样可能串字，建议 images 转图核对]"
        chunks.append("## 第 %d 页\n\n%s" % (i, note))
    body = "# %s\n\n> 共 %d 页，本次读取 %d 页，%d 页无文本层\n\n%s\n" % (
        os.path.basename(path), total, len(sel), empty, "\n\n".join(chunks))
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(body)
        print("已写入：%s（%d 字）" % (os.path.abspath(out), len(body)))
    else:
        print(body)
    if empty:
        print("提示：%d 页没有文本层，用 images 命令导出这些页再看。" % empty)
    if vert:
        print("提示：%s 页疑似竖排/旋转文字，建议转图核对。" % vert[:12])


def cmd_images(path, pages, outdir, max_width, fmt):
    reader, _ = read_pdf(path)
    total = len(reader.pages)
    sel = parse_pages(pages, total)
    try:
        from PIL import Image
    except Exception:
        Image = None
    os.makedirs(outdir, exist_ok=True)
    made = []
    for i in sel:
        try:
            imgs = list(reader.pages[i - 1].images)
        except Exception:
            imgs = []
        if not imgs:
            print("第 %d 页：没有可导出的位图（纯矢量页），试 text 命令" % i)
            continue
        for k, img in enumerate(imgs):
            data = img.data
            name = "p%03d" % i + ("" if k == 0 else "_%d" % (k + 1))
            dst = os.path.join(outdir, name + "." + fmt)
            if Image is not None:
                try:
                    im = Image.open(io.BytesIO(data))
                    if im.mode not in ("RGB", "L"):
                        im = im.convert("RGB")
                    if max_width and im.width > max_width:
                        h = max(1, int(im.height * max_width / im.width))
                        im = im.resize((max_width, h))
                    if fmt == "jpg":
                        im.save(dst, quality=88)
                    else:
                        im.save(dst)
                    made.append(dst)
                    continue
                except Exception as e:
                    print("第 %d 页图片转换失败（%s），改为原样写出" % (i, e))
            with open(dst, "wb") as f:
                f.write(data)
            made.append(dst)
    for p in made:
        print(p)
    print("共导出 %d 张图到 %s" % (len(made), os.path.abspath(outdir)))


def cmd_plan(path, pages):
    reader, _ = read_pdf(path)
    total = len(reader.pages)
    sel = parse_pages(pages, total)
    have, lack, vert = [], [], []
    for i in sel:
        t = page_text(reader.pages[i - 1])
        if len(t.strip()) >= 30 and not looks_vertical(t):
            have.append(i)
        else:
            (vert if t.strip() else lack).append(i)
    print("共 %d 页，本次评估 %d 页" % (total, len(sel)))
    print("1) 直接 text 读：%s" % (have[:30] or "无"))
    print("2) 无文本层，转图：%s" % (lack[:30] or "无"))
    print("3) 竖排/串字，转图核对：%s" % (vert[:30] or "无"))


def main():
    ap = argparse.ArgumentParser(description="读取 PDF：文本层、页数、页面图片")
    sub = ap.add_subparsers(dest="cmd")

    p1 = sub.add_parser("info")
    p1.add_argument("pdf")

    p2 = sub.add_parser("text")
    p2.add_argument("pdf")
    p2.add_argument("--pages", default="")
    p2.add_argument("--mode", default="plain", choices=["plain", "layout"])
    p2.add_argument("--out", default="")

    p3 = sub.add_parser("images")
    p3.add_argument("pdf")
    p3.add_argument("--pages", default="1-3")
    p3.add_argument("--out", default="./pdf_pages")
    p3.add_argument("--max-width", type=int, default=1500)
    p3.add_argument("--format", default="png", choices=["png", "jpg"])

    p4 = sub.add_parser("plan")
    p4.add_argument("pdf")
    p4.add_argument("--pages", default="")

    a = ap.parse_args()
    if not a.cmd:
        ap.print_help()
        return
    if a.cmd == "info":
        cmd_info(a.pdf)
    elif a.cmd == "text":
        cmd_text(a.pdf, a.pages, a.mode, a.out)
    elif a.cmd == "images":
        cmd_images(a.pdf, a.pages, a.out, a.max_width, a.format)
    elif a.cmd == "plan":
        cmd_plan(a.pdf, a.pages)


if __name__ == "__main__":
    main()
