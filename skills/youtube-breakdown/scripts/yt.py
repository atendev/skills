#!/usr/bin/env -S uv run -q --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["youtube-transcript-api>=1.0"]
# ///
"""Print a compact YouTube transcript: title line, then paragraphs prefixed with [m:ss] every ~N seconds.

Usage: yt.py <url-or-id> [--lang en,de] [--every 120] [--out file.txt]
"""
import argparse, json, re, sys, urllib.request

from youtube_transcript_api import YouTubeTranscriptApi


def video_id(s):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/|live/)([\w-]{11})", s)
    return m.group(1) if m else s.strip()


def title(vid):
    try:
        u = f"https://www.youtube.com/oembed?format=json&url=https://youtu.be/{vid}"
        d = json.load(urllib.request.urlopen(u, timeout=10))
        return f"{d['title']} — {d['author_name']}"
    except Exception:
        return vid


def ts(s):
    s = int(s)
    h, m, s = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("--lang", default="en")
    p.add_argument("--every", type=int, default=120)
    p.add_argument("--out")
    a = p.parse_args()

    vid = video_id(a.video)
    langs = a.lang.split(",")
    api = YouTubeTranscriptApi()
    try:
        snippets = api.fetch(vid, languages=langs).snippets
    except Exception:
        tl = api.list(vid)
        t = next(iter(tl))
        snippets = (t.translate(langs[0]) if t.is_translatable else t).fetch().snippets

    paras, cur, mark, last = [], [], None, ""
    for sn in snippets:
        text = re.sub(r"\s+", " ", re.sub(r"\[[^\]]*\]|>>", " ", sn.text)).strip()
        if not text or text == last:
            continue
        last = text
        if mark is None or sn.start - mark >= a.every:
            if cur:
                paras.append(f"[{ts(mark)}] " + " ".join(cur))
            cur, mark = [], sn.start
        cur.append(text)
    if cur:
        paras.append(f"[{ts(mark)}] " + " ".join(cur))

    body = "\n".join(paras)
    out = f"# {title(vid)} (https://youtu.be/{vid}, {len(body.split())} words)\n{body}\n"
    if a.out:
        open(a.out, "w").write(out)
    sys.stdout.write(out)


if __name__ == "__main__":
    main()
