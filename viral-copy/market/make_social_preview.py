"""生成 GitHub Social Preview 图（1280×640）。

用法：python market/make_social_preview.py
需要 Pillow 与中文字体（Windows 自带 msyh.ttc / Linux 用 Noto Sans CJK）。
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 640
OUT = Path(__file__).resolve().parent / "social-preview.png"

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\msyh.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    raise SystemExit("找不到中文字体，请把字体路径加入 FONT_CANDIDATES")


def main() -> None:
    img = Image.new("RGB", (W, H), "#0b0f17")
    d = ImageDraw.Draw(img)

    # 底部渐变感：几条横线制造层次，避免纯色单调
    for i in range(120):
        alpha = int(12 - i / 10)
        if alpha > 0:
            d.line([(0, H - i), (W, H - i)], fill=(30, 41, 59, alpha))

    d.rectangle([64, 96, 72, 152], fill="#ef4444")

    d.text((104, 92), "爆款文案工坊", font=load_font(78), fill="#f8fafc")
    d.text((104, 196), "viral-copy · Agent Skill", font=load_font(34), fill="#94a3b8")

    d.text(
        (104, 288),
        "选题 · 标题 · 脚本 · 合规检查",
        font=load_font(40),
        fill="#e2e8f0",
    )
    d.text(
        (104, 352),
        "给 AI 装上能直接发出去的文案手感",
        font=load_font(32),
        fill="#64748b",
    )

    # 右侧对比卡
    box = [830, 250, 1200, 470]
    d.rounded_rectangle(box, radius=18, fill="#111827", outline="#1f2937", width=2)
    d.text((872, 286), "27", font=load_font(64), fill="#64748b")
    d.text((872, 366), "→ 85", font=load_font(64), fill="#22c55e")
    d.text((880, 442), "评分卡：4 项 × 25 分", font=load_font(26), fill="#94a3b8")

    d.text(
        (104, 552),
        "MIT · 零依赖 · 中文优先",
        font=load_font(28),
        fill="#475569",
    )

    img.save(OUT)
    print(f"已生成 {OUT}")


if __name__ == "__main__":
    main()
