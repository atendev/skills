#!/usr/bin/env python3
"""Show wayfinder-master runs across all projects and one run's free child-thread slots.

Usage: active-runs.py [--minutes 15] [--per-master 3] [--slug SLUG] [--run RUN]

Each ticket counts through its newest tagged transcript. That transcript is active when
it changed within the window and its last turn did not end (an end_turn reply or an
interruption), so finished, handed-off and cancelled children free their slot at once.
Masters are listed when their transcript changed within 120 minutes, since a master sits
idle while its children work. Each master has its own budget of --per-master children.
With --slug, a line "same map: <run>" flags another master on that map (--run excludes
this thread's own run). With --run, the last line is "slots free: N of M" for that run.
"""
import argparse
import glob
import json
import os
import re
import time

PROJECTS = os.path.expanduser("~/.claude/projects")
TAG = re.compile(r"printf 'wfm-%s\\n' '([A-Za-z0-9._-]+)-(master|\d+)-(\d+)'")

ap = argparse.ArgumentParser()
ap.add_argument("--minutes", type=int, default=15)
ap.add_argument("--per-master", type=int, default=3)
ap.add_argument("--slug", default="")
ap.add_argument("--run", default="")
a = ap.parse_args()
now = time.time()


def scan(path):
    tag, last = None, None
    with open(path, errors="replace") as f:
        for line in f:
            if '"user"' not in line and '"assistant"' not in line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") not in ("user", "assistant"):
                continue
            last = d
            content = (d.get("message") or {}).get("content")
            if tag or d["type"] != "assistant" or not isinstance(content, list):
                continue
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Bash":
                    m = TAG.search(str((b.get("input") or {}).get("command", "")))
                    if m:
                        tag = m.groups()
                        break
    return tag, last


def turn_ended(last):
    if not last:
        return True
    msg = last.get("message") or {}
    if last["type"] == "assistant":
        return msg.get("stop_reason") == "end_turn"
    content = msg.get("content")
    text = content if isinstance(content, str) else " ".join(
        str(b.get("text", "")) for b in content or [] if isinstance(b, dict))
    return "[Request interrupted" in text


runs = {}
newest = {}
for p in glob.glob(os.path.join(PROJECTS, "**", "*.jsonl"), recursive=True):
    mtime = os.path.getmtime(p)
    if now - mtime > 120 * 60:
        continue
    with open(p, errors="replace") as f:
        if "printf 'wfm-" not in f.read():
            continue
    tag, last = scan(p)
    if not tag:
        continue
    slug, who, run = tag
    r = runs.setdefault((slug, run), {"master": False, "children": set()})
    if who == "master":
        r["master"] = True
    elif mtime > newest.get(tag, (0, None))[0]:
        newest[tag] = (mtime, last)
for (slug, who, run), (mtime, last) in newest.items():
    if now - mtime <= a.minutes * 60 and not turn_ended(last):
        runs[(slug, run)]["children"].add(who)
for (slug, run), r in sorted(runs.items()):
    print(f"{slug} run {run}: {'master, ' if r['master'] else ''}{len(r['children'])} active child thread(s) {' '.join(sorted(r['children']))}")
    if a.slug and slug == a.slug and r["master"] and run != a.run:
        print(f"same map: {run}")
if a.run:
    mine = sum(len(r["children"]) for (s, run), r in runs.items() if run == a.run)
    print(f"slots free: {max(a.per_master - mine, 0)} of {a.per_master}")
