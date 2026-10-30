# -*- coding: utf-8 -*-
"""douyin-video-copy：扒抖音视频的文案。

用法：
  python dy_copy.py all     "https://v.douyin.com/xxxx/"  --out ./out
  python dy_copy.py extract "https://v.douyin.com/xxxx/"  [--json]
  python dy_copy.py asr     <音频或视频文件>  [--model <vosk模型目录>]
  python dy_copy.py download "https://v.douyin.com/xxxx/" --out ./out [--video]

依赖：websocket-client（浏览器抓取）、ffmpeg（音频转码，脚本会自动找）、vosk（可选，本地转写）。
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

FFMPEG_CANDIDATES = [
    r"C:\Users\徐彦\ffmpeg\bin\ffmpeg.exe",
    "ffmpeg",
]

DEFAULT_VOSK = r"C:\dsh-asr\vosk-cn"
LEGACY_VOSK = os.path.join(os.path.expanduser("~"), ".local", "share", "asr", "vosk-model-small-cn-0.22")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")


def die(msg, code=2):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(code)


# ---------------- 链接解析 ----------------
def find_browser():
    for p in EDGE_CANDIDATES:
        if os.path.isfile(p):
            return p
    die("没找到 Edge / Chrome")


def find_ffmpeg():
    for p in FFMPEG_CANDIDATES:
        if p == "ffmpeg":
            w = shutil.which("ffmpeg")
            if w:
                return w
        elif os.path.isfile(p):
            return p
    return None


def resolve_share_url(url):
    """把 v.douyin.com 短链跟到最终分享页；已经是 douyin.com/video 就直接用。"""
    if re.search(r"(douyin\.com|iesdouyin\.com)", url) and "v.douyin.com" not in url:
        m = re.search(r"/video/(\d+)", url)
        return url, (m.group(1) if m else None)
    out = subprocess.run(["curl.exe", "-sS", "-o", "NUL", "-w", "%{url_effective}", "-L",
                          "-A", UA, url], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    final = (out.stdout or "").strip()
    if not final:
        die("短链解析失败：%s" % (out.stderr or "")[:200])
    m = re.search(r"/video/(\d+)", final)
    return final, (m.group(1) if m else None)


# ---------------- CDP 抓页面 ----------------
def cdp_extract(url, port=9333, wait=7):
    try:
        import websocket  # noqa: F401
    except Exception:
        die("缺少 websocket-client：python -m pip install websocket-client")

    import websocket

    browser = find_browser()
    profile = os.path.join(tempfile.gettempdir(), "dsh-douyin-profile")
    os.makedirs(profile, exist_ok=True)
    proc = subprocess.Popen([
        browser, "--headless=new", "--remote-debugging-port=%d" % port,
        "--user-data-dir=%s" % profile, "--no-first-run", "--no-default-browser-check",
        "--disable-gpu", "--disable-crash-reporter", "--mute-audio", "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def http(path):
        req = urllib.request.Request("http://127.0.0.1:%d%s" % (port, path))
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))

    ws_url = None
    for _ in range(40):
        try:
            pages = [t for t in http("/json/list") if t.get("type") == "page"]
            if pages:
                ws_url = pages[0]["webSocketDebuggerUrl"]
                break
        except Exception:
            pass
        time.sleep(0.5)
    if not ws_url:
        proc.terminate()
        die("浏览器调试端口没起来")

    ws = websocket.create_connection(ws_url, timeout=30)
    mid = [0]

    def send(method, params=None):
        mid[0] += 1
        ws.send(json.dumps({"id": mid[0], "method": method, "params": params or {}}))
        return mid[0]

    send("Page.enable")
    send("Network.enable")
    send("Runtime.enable")
    send("Page.navigate", {"url": url})
    time.sleep(2)
    try:
        # 模拟一次点击播放（部分老视频不点不加载）
        send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": 640, "y": 480, "button": "left", "clickCount": 1})
        send("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": 640, "y": 480, "button": "left", "clickCount": 1})
    except Exception:
        pass
    try:
        send("Runtime.evaluate", {"expression":
             "const v=document.querySelector('video');if(v){v.muted=true;const p=v.play();if(p)p.catch(()=>{});}"})
    except Exception:
        pass

    # 先听网络事件，把媒体直链收下来（比 performance 条目可靠）
    media_evt = []
    t_end = time.time() + max(5, wait)
    while time.time() < t_end:
        try:
            ws.settimeout(0.8)
            msg = json.loads(ws.recv())
        except Exception:
            continue
        if msg.get("method") == "Network.responseReceived":
            resp = msg.get("params", {}).get("response", {})
            u = resp.get("url", "")
            if any(k in u for k in ("douyinvod", "/media-video", "/media-audio", ".mp4", ".m3u8")):
                if u not in media_evt:
                    media_evt.append(u)

    js = r"""
(() => {
  const meta = {};
  document.querySelectorAll('meta').forEach(m => {
    const k = m.getAttribute('name') || m.getAttribute('property');
    if (k) meta[k] = m.getAttribute('content');
  });
  const media = performance.getEntriesByType('resource').map(e => e.name)
    .filter(n => /douyinvod|\/media-video|\/media-audio|\.mp4|\.m3u8/i.test(n));
  return JSON.stringify({
    url: location.href,
    title: document.title,
    meta: meta,
    text: document.body ? document.body.innerText : '',
    media: [...new Set(media)].slice(0, 12)
  });
})()
"""
    expr_id = send("Runtime.evaluate", {"expression": js, "returnByValue": True})
    data = None
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            ws.settimeout(1.0)
            msg = json.loads(ws.recv())
        except Exception:
            continue
        if msg.get("id") == expr_id:
            data = msg
            break
    ws.close()
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()

    if not data:
        die("页面求值没返回")
    val = data.get("result", {}).get("result", {}).get("value")
    if not val:
        die("页面返回空，可能被反爬拦了")
    page = json.loads(val)
    merged = list(page.get("media") or [])
    for u in media_evt:
        if u not in merged:
            merged.append(u)
    page["media"] = merged[:20]
    return page


# ---------------- 结构化 ----------------
def parse_page(page):
    text = page.get("text", "")
    lines = [x.strip() for x in text.split("\n")]

    title = (page.get("title") or "").replace(" - 抖音", "").strip()
    meta_desc = page.get("meta", {}).get("description", "")

    author = None
    fans = likes_total = None
    m = re.search(r"粉丝(\d+[\d\.]*万?)获赞(\d+[\d\.]*万?)", text)
    if m:
        fans, likes_total = m.group(1), m.group(2)
    # 作者：发布时间之后的第一行非空文本，或“粉丝…获赞…”上一行
    idx = next((i for i, x in enumerate(lines) if x.startswith("发布时间：")), None)
    if idx is not None:
        for x in lines[idx + 1: idx + 5]:
            if x and not re.fullmatch(r"[\d\.万]+", x):
                author = x
                break
    if not author and m:
        j = next((i for i, x in enumerate(lines) if x.startswith("粉丝") and "获赞" in x), None)
        if j:
            for x in reversed(lines[max(0, j - 3): j]):
                if x and not re.fullmatch(r"[\d\.万]+", x) and not re.search(r"\d{2}:\d{2}", x):
                    author = x
                    break

    publish = None
    m = re.search(r"发布时间：([0-9\-: ]+)", text)
    if m:
        publish = m.group(1).strip()

    # 章节要点（抖音自动生成的 AI 摘要）
    chapters = None
    if "章节要点" in text and "内容由AI生成" in text:
        seg = text.split("章节要点", 1)[1].split("内容由AI生成", 1)[0].strip()
        chapters = seg
    summary = None
    if chapters:
        first = chapters.split("\n")[0].strip()
        if first:
            summary = first

    # 互动数据：标题下面连续 3–4 个纯数字
    stats = {}
    if title:
        try:
            start = next(i for i, x in enumerate(lines) if x.startswith(title[:10]))
            nums = []
            for x in lines[start + 1: start + 12]:
                if re.fullmatch(r"\d+(\.\d+)?万?", x):
                    nums.append(x)
                elif nums:
                    break
            for k, v in zip(["点赞", "评论", "收藏", "分享"], nums):
                stats[k] = v
        except StopIteration:
            pass

    media = page.get("media", [])
    audio = next((u for u in media if ("media-audio" in u or "mime_type=audio" in u or "audio-und" in u)), None)
    video = next((u for u in media if ("media-video" in u or "video_mp4" in u) and u != audio), None)
    if audio is None:
        # 抓不到纯音频流时，拿视频当音源，交给 ffmpeg 抽音轨
        audio = video

    return {
        "标题": title,
        "作者": author,
        "粉丝": fans,
        "累计获赞": likes_total,
        "发布时间": publish,
        "互动": stats,
        "页面简介": meta_desc,
        "章节要点": chapters,
        "一句话概括": summary,
        "音频直链": audio,
        "视频直链": video,
        "页面地址": page.get("url"),
    }


# ---------------- 下载 ----------------
def curl_download(url, dst, referer="https://www.douyin.com/"):
    if not url:
        die("没有可下载的直链")
    r = subprocess.run(["curl.exe", "-sS", "-L", "--max-time", "300",
                        "-A", UA, "-H", "Referer: " + referer, "-o", dst, url],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 or not os.path.isfile(dst) or os.path.getsize(dst) < 10000:
        die("下载失败：%s" % (r.stderr or "")[:200])
    return dst


# ---------------- 转写 ----------------
def to_wav(src, dst):
    ff = find_ffmpeg()
    if not ff:
        die("没找到 ffmpeg，无法转码")
    r = subprocess.run([ff, "-y", "-i", src, "-vn", "-ar", "16000", "-ac", "1", "-f", "wav", dst],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not os.path.isfile(dst):
        die("转码失败：%s" % (r.stderr or "")[-300:])
    return dst


def ascii_model(src):
    """Vosk 在 Windows 上读不了带中文的路径：非纯 ASCII 就先拷到 C:\\dsh-asr 下再用。"""
    if not src or all(ord(c) < 128 for c in src):
        return src
    dst = os.path.join("C:\\dsh-asr", os.path.basename(src.rstrip("\\/")) or "vosk-cn")
    if not os.path.isdir(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copytree(src, dst)
    return dst


def asr(wav, model_dir):
    try:
        from vosk import Model, KaldiRecognizer, SetLogLevel
    except Exception:
        die("缺少 vosk：python -m pip install vosk（模型：vosk-model-small-cn-0.22）")
    if not os.path.isdir(model_dir):
        if os.path.isdir(LEGACY_VOSK):
            model_dir = LEGACY_VOSK
        else:
            die("找不到语音模型目录：%s" % model_dir)
    model_dir = ascii_model(model_dir)
    SetLogLevel(-1)
    import wave

    wf = wave.open(wav, "rb")
    model = Model(model_dir)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    pieces, last_end = [], 0.0
    while True:
        buf = wf.readframes(4000)
        if not buf:
            break
        if rec.AcceptWaveform(buf):
            r = json.loads(rec.Result())
            words = r.get("result", [])
            if not words and r.get("text"):
                pieces.append((0.0, r["text"]))
                continue
            for w in words:
                gap = w["start"] - last_end
                pieces.append((gap, w["word"]))
                last_end = w["end"]
    tail = json.loads(rec.FinalResult())
    for w in tail.get("result", []):
        gap = w["start"] - last_end if last_end else 0.0
        pieces.append((gap, w["word"]))
        last_end = w["end"]
    wf.close()

    out = []
    for gap, word in pieces:
        if out and gap > 2.0:
            out.append("。")
        elif out and gap > 0.45:
            out.append("，")
        out.append(word)
    text = "".join(out).replace("，。", "。")
    return re.sub(r"[，]{2,}", "，", text)


def write_report(info, out_dir, transcript=None, audio_path=None, video_path=None):
    os.makedirs(out_dir, exist_ok=True)
    md = ["# %s\n" % (info.get("标题") or "抖音视频文案")]
    md.append("- 作者：%s（粉丝 %s，累计获赞 %s）" % (info.get("作者") or "?", info.get("粉丝") or "?", info.get("累计获赞") or "?"))
    if info.get("发布时间"):
        md.append("- 发布时间：%s" % info["发布时间"])
    if info.get("互动"):
        md.append("- 互动：%s" % "，".join("%s %s" % (k, v) for k, v in info["互动"].items()))
    if info.get("页面地址"):
        md.append("- 链接：%s" % info["页面地址"])
    md.append("")
    if info.get("一句话概括"):
        md.append("## 一句话概括（抖音自动生成）\n\n%s\n" % info["一句话概括"])
    if info.get("章节要点"):
        md.append("## 章节要点（抖音自动生成）\n\n%s\n" % info["章节要点"])
    if transcript:
        md.append("## 口播全文（本地语音转写，标点与个别词可能有误差）\n\n%s\n" % transcript)
    else:
        md.append("## 口播全文\n\n（未转写：没有音频或未安装 vosk）\n")
    if audio_path:
        md.append("- 音频文件：%s" % audio_path)
    if video_path:
        md.append("- 视频文件：%s" % video_path)
    dst = os.path.join(out_dir, "douyin-copy.md")
    open(dst, "w", encoding="utf-8").write("\n".join(md))
    return dst


def cmd_extract(url, as_json=False, wait=7):
    final, vid = resolve_share_url(url)
    page = cdp_extract(final, wait=wait)
    info = parse_page(page)
    info["视频ID"] = vid
    if as_json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        for k, v in info.items():
            if k in ("音频直链", "视频直链", "页面简介"):
                continue
            if v:
                print("%s：%s" % (k, v if not isinstance(v, dict) else json.dumps(v, ensure_ascii=False)))
    return info


def cmd_all(url, out_dir, model_dir, want_video=False, wait=7):
    info = cmd_extract(url, as_json=True) if False else None
    final, vid = resolve_share_url(url)
    page = cdp_extract(final)
    info = parse_page(page)
    info["视频ID"] = vid
    os.makedirs(out_dir, exist_ok=True)

    audio = None
    if info.get("音频直链"):
        mp4 = os.path.join(out_dir, "%s-audio.mp4" % (vid or "audio"))
        try:
            curl_download(info["音频直链"], mp4)
            wav = os.path.join(out_dir, "%s-audio.wav" % (vid or "audio"))
            audio = to_wav(mp4, wav)
        except SystemExit:
            audio = None
    video_path = None
    if want_video and info.get("视频直链"):
        video_path = curl_download(info["视频直链"], os.path.join(out_dir, "%s.mp4" % (vid or "video")))

    transcript = None
    if audio:
        try:
            transcript = asr(audio, model_dir)
        except SystemExit:
            transcript = None

    dst = write_report(info, out_dir, transcript, audio, video_path)
    print("报告：%s" % dst)
    return dst


def main():
    ap = argparse.ArgumentParser(description="扒抖音视频文案（标题/数据/章节要点/口播转写）")
    sub = ap.add_subparsers(dest="cmd")

    p1 = sub.add_parser("extract")
    p1.add_argument("url")
    p1.add_argument("--json", action="store_true")
    p1.add_argument("--wait", type=int, default=7)

    p2 = sub.add_parser("all")
    p2.add_argument("url")
    p2.add_argument("--out", default="./douyin-out")
    p2.add_argument("--model", default=DEFAULT_VOSK)
    p2.add_argument("--video", action="store_true", help="同时下载视频")
    p2.add_argument("--wait", type=int, default=7, help="页面等待秒数，反爬慢时调大")

    p3 = sub.add_parser("asr")
    p3.add_argument("file")
    p3.add_argument("--model", default=DEFAULT_VOSK)

    p4 = sub.add_parser("download")
    p4.add_argument("url")
    p4.add_argument("--out", default="./douyin-out")
    p4.add_argument("--video", action="store_true")

    a = ap.parse_args()
    if a.cmd == "extract":
        cmd_extract(a.url, a.json, a.wait)
    elif a.cmd == "all":
        cmd_all(a.url, a.out, a.model, a.video, a.wait)
    elif a.cmd == "asr":
        wav = a.file
        if not wav.lower().endswith(".wav"):
            wav = to_wav(a.file, a.file.rsplit(".", 1)[0] + ".wav")
        print(asr(wav, a.model))
    elif a.cmd == "download":
        os.makedirs(a.out, exist_ok=True)
        final, vid = resolve_share_url(a.url)
        page = cdp_extract(final)
        info = parse_page(page)
        url2 = info["视频直链"] if a.video else (info["音频直链"] or info["视频直链"])
        dst = os.path.join(a.out, "%s.%s" % (vid or "file", "mp4"))
        print(curl_download(url2, dst))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
