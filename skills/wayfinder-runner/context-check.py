#!/usr/bin/env python3
"""Print this thread's current context size and whether it passed the handoff limit.

Usage: context-check.py MARKER [--limit 150000]

MARKER is the tag the thread echoed once with printf at its start. The script finds the
newest transcript under ~/.claude/projects where a Bash call printed it (subagent
transcripts included) and reads the context size of the last assistant turn.
Output is one line starting with OK or HANDOFF.
"""
import argparse
import glob
import json
import os
import time

PROJECTS = os.path.expanduser("~/.claude/projects")


def echoed(path, tail):
    with open(path, errors="replace") as f:
        for line in f:
            if tail not in line or "printf" not in line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            content = (d.get("message") or {}).get("content")
            if d.get("type") != "assistant" or not isinstance(content, list):
                continue
            for b in content:
                cmd = str((b.get("input") or {}).get("command", "")) if isinstance(b, dict) else ""
                if b.get("type") == "tool_use" and b.get("name") == "Bash" and "printf" in cmd and tail in cmd:
                    return True
    return False


def last_context(path):
    ctx = 0
    with open(path, errors="replace") as f:
        for line in f:
            if '"usage"' not in line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            u = (d.get("message") or {}).get("usage")
            if d.get("type") == "assistant" and u:
                ctx = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
    return ctx


ap = argparse.ArgumentParser()
ap.add_argument("marker")
ap.add_argument("--limit", type=int, default=150000)
a = ap.parse_args()
tail = a.marker.split("-", 1)[1] if a.marker.startswith(("wfm-", "wfr-", "wfs-")) else a.marker
cutoff = time.time() - 12 * 3600
paths = sorted((p for p in glob.glob(os.path.join(PROJECTS, "**", "*.jsonl"), recursive=True)
                if os.path.getmtime(p) >= cutoff), key=os.path.getmtime, reverse=True)
for p in paths:
    if echoed(p, tail):
        ctx = last_context(p)
        state = "HANDOFF" if ctx >= a.limit else "OK"
        print(f"{state} context {ctx // 1000}k of {a.limit // 1000}k limit")
        break
else:
    print(f"OK context unknown: no transcript echoed {a.marker} in the last 12 hours")
