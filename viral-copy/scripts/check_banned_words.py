#!/usr/bin/env python3
"""检查文案中的极限词、功效承诺与导流词。

用法：
    python scripts/check_banned_words.py draft.md
    python scripts/check_banned_words.py a.md b.txt --json
    python scripts/check_banned_words.py --words references/banned-words.txt draft.md
    type draft.md | python scripts/check_banned_words.py -

命中任意词时退出码为 1，干净时为 0。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_WORDS = Path(__file__).resolve().parent.parent / "references" / "banned-words.txt"


def load_words(path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    last_advice = ""
    with path.open(encoding="utf-8-sig") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            word = parts[0]
            if not word:
                continue
            advice = parts[2] if len(parts) > 2 and parts[2] else ""
            if advice == "同上":  # 继承上一条的具体建议，避免输出“同上”这种废话
                advice = last_advice
            elif advice:
                last_advice = advice
            entries.append(
                {
                    "word": word,
                    "category": parts[1] if len(parts) > 1 and parts[1] else "未分类",
                    "advice": advice,
                }
            )
    # 长词优先，避免「加微信」被「微信」先命中
    entries.sort(key=lambda e: len(e["word"]), reverse=True)
    return entries


def scan(text: str, entries: list[dict[str, str]]) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        taken: list[tuple[int, int]] = []
        for entry in entries:
            start = line.find(entry["word"])
            while start != -1:
                end = start + len(entry["word"])
                if not any(s < end and start < e for s, e in taken):
                    taken.append((start, end))
                    hits.append(
                        {
                            "line": lineno,
                            "column": start + 1,
                            "word": entry["word"],
                            "category": entry["category"],
                            "advice": entry["advice"],
                            "context": line.strip()[:120],
                        }
                    )
                start = line.find(entry["word"], end)
    hits.sort(key=lambda h: (h["line"], h["column"]))
    return hits


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="检查文案中的违禁/限流词")
    parser.add_argument("files", nargs="*", help="待检查的文件；用 - 表示从标准输入读取")
    parser.add_argument("--words", type=Path, default=DEFAULT_WORDS, help="词库文件路径")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    parser.add_argument("--quiet", action="store_true", help="只在一处命中时静默通过")
    args = parser.parse_args(argv)

    if not args.words.is_file():
        print(f"找不到词库：{args.words}", file=sys.stderr)
        return 2

    entries = load_words(args.words)
    targets = args.files or ["-"]
    all_hits: list[dict[str, object]] = []

    for target in targets:
        if target == "-":
            text = sys.stdin.read()
            name = "<stdin>"
        else:
            path = Path(target)
            if not path.is_file():
                print(f"找不到文件：{path}", file=sys.stderr)
                return 2
            text = path.read_text(encoding="utf-8-sig")
            name = str(path)
        hits = scan(text, entries)
        for hit in hits:
            hit["file"] = name
        all_hits.extend(hits)

    if args.json:
        print(json.dumps({"total": len(all_hits), "hits": all_hits}, ensure_ascii=False, indent=2))
        return 1 if all_hits else 0

    if not all_hits:
        if not args.quiet:
            print("✅ 未命中违禁/限流词")
        return 0

    by_category: dict[str, int] = {}
    for hit in all_hits:
        by_category[str(hit["category"])] = by_category.get(str(hit["category"]), 0) + 1

    print(f"⚠️  命中 {len(all_hits)} 处：" + "，".join(f"{k} {v}" for k, v in by_category.items()))
    print()
    for hit in all_hits:
        print(f"{hit['file']}:{hit['line']}:{hit['column']}  【{hit['category']}】{hit['word']}")
        print(f"    … {hit['context']}")
        if hit["advice"]:
            print(f"    → {hit['advice']}")
    print()
    print("按「替换」处理，不要整段删除：删掉信息量会崩，替换后意思更可信。")
    return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
