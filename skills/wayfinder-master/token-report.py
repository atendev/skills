#!/usr/bin/env python3
"""Token breakdown for a wayfinder-master run, read from Claude Code transcripts.

Usage:
  token-report.py --since 2026-11-12T18:00:00Z [--baseline claude-opus-5-5] LABEL=MARKER [LABEL=MARKER ...]

Each MARKER is a unique string the thread echoed once (see the skill's Token report
section). The script finds the session transcript containing it under ~/.claude/projects,
adds that session's subagent transcripts, and sums usage per model. The first LABEL is
the master; the rest are children, in the order they started.
"""
import argparse
import glob
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

PROJECTS = os.path.expanduser("~/.claude/projects")
FIELDS = ("input", "cache_write_5m", "cache_write_1h", "cache_read", "output")


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def echoed_marker(path, marker):
    """True if this thread ran the marker's printf in its own Bash call.

    The master's transcript also contains every child's marker, inside the
    delegate_task briefs, so a plain text match tags every thread as the master.
    """
    tail = marker[4:] if marker.startswith("wfm-") else marker
    with open(path, errors="replace") as f:
        for line in f:
            if tail not in line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            content = (d.get("message") or {}).get("content")
            if d.get("type") != "assistant" or not isinstance(content, list):
                continue
            for b in content:
                if (isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Bash"
                        and "printf" in str((b.get("input") or {}).get("command", ""))
                        and tail in str((b.get("input") or {}).get("command", ""))):
                    return True
    return False


def find_session(marker, since):
    cutoff = since.timestamp()
    return [p for p in glob.glob(os.path.join(PROJECTS, "*", "*.jsonl"))
            if os.path.getmtime(p) >= cutoff and echoed_marker(p, marker)]


def read_usage(path, since):
    """Return {model: Counter}, call count, first timestamp, last context size."""
    by_msg = {}
    first = None
    with open(path, errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") != "assistant":
                continue
            ts = d.get("timestamp")
            if ts and parse_ts(ts) < since:
                continue
            msg = d.get("message") or {}
            u = msg.get("usage")
            if not u or not msg.get("model") or msg["model"].startswith("<"):
                continue
            by_msg[msg.get("id") or id(d)] = (ts, msg["model"], u)
    totals = defaultdict(lambda: dict.fromkeys(FIELDS, 0))
    last_ctx = 0
    for ts, model, u in sorted(by_msg.values(), key=lambda x: x[0] or ""):
        first = first or ts
        cc = u.get("cache_creation") or {}
        w1h = cc.get("ephemeral_1h_input_tokens", 0)
        w5m = cc.get("ephemeral_5m_input_tokens", u.get("cache_creation_input_tokens", 0) - w1h)
        t = totals[model]
        t["input"] += u.get("input_tokens", 0)
        t["cache_write_5m"] += max(w5m, 0)
        t["cache_write_1h"] += w1h
        t["cache_read"] += u.get("cache_read_input_tokens", 0)
        t["output"] += u.get("output_tokens", 0)
        last_ctx = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
    return totals, len(by_msg), first, last_ctx


def cost(t, p):
    return sum(t[k] * p[k] for k in FIELDS) / 1e6


def fmt(n):
    return f"{n:,}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True, help="ISO timestamp of the run start")
    ap.add_argument("--baseline", default="claude-opus-5-5", help="model every ticket would use without routing")
    ap.add_argument("--prices", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.json"))
    ap.add_argument("threads", nargs="+", metavar="LABEL=MARKER")
    a = ap.parse_args()
    since = parse_ts(a.since)
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    prices = {k: v for k, v in json.load(open(a.prices)).items() if not k.startswith("_")}
    base = prices[a.baseline]

    rows, threads, missing = [], [], []
    master_sessions = set()
    for i, spec in enumerate(a.threads):
        label, _, marker = spec.partition("=")
        sessions = [s for s in find_session(marker, since) if s not in master_sessions]
        if i == 0:
            master_sessions.update(sessions)
        if not sessions:
            missing.append(label)
            continue
        calls, first, ctx = 0, None, 0
        for s in sessions:
            parts = [(label, s)]
            sub = os.path.join(os.path.dirname(s), os.path.basename(s)[:-6])
            parts += [(f"{label} subagents", p) for p in glob.glob(os.path.join(sub, "**", "*.jsonl"), recursive=True)]
            for lab, p in parts:
                totals, n, f, c = read_usage(p, since)
                for model, t in totals.items():
                    rows.append((lab, model, t))
                if lab == label:
                    calls += n
                    ctx = c
                    first = min(filter(None, [first, f]), default=None)
        threads.append((label, calls, first, ctx))

    print("| Thread | Model | Input | Cache write | Cache read | Output | Cost (USD) |")
    print("|---|---|--:|--:|--:|--:|--:|")
    actual = baseline_cost = 0.0
    unpriced = set()
    for lab, model, t in rows:
        p = prices.get(model)
        if p is None:
            unpriced.add(model)
            c = "n/a"
        else:
            cv = cost(t, p)
            actual += cv
            baseline_cost += cost(t, base) if not lab.endswith("subagents") else cv
            c = f"{cv:.2f}"
        print(f"| {lab} | {model} | {fmt(t['input'])} | {fmt(t['cache_write_5m'] + t['cache_write_1h'])} | {fmt(t['cache_read'])} | {fmt(t['output'])} | {c} |")
    print(f"\nTotal cost: ${actual:.2f}")

    print(f"\nRouting savings: ${baseline_cost - actual:.2f} measured. That is the cost of the same tokens with every thread on {a.baseline}, minus the actual cost. Subagents keep their own model in both figures.")

    children = sorted(threads[1:], key=lambda x: x[2] or "")
    extra, carried = 0, 0
    for _, calls, _, ctx in children:
        extra += calls * carried
        carried += ctx
    print(f"Fresh-context savings: about {fmt(extra)} cache-read tokens (${extra * base['cache_read'] / 1e6:.2f} at {a.baseline}) estimated. That is what one thread running every child ticket in turn would have re-read, because each call would carry the earlier tickets' final context.")

    if unpriced:
        print(f"\nNo price for {', '.join(sorted(unpriced))}. Add it to prices.json.")
    if missing:
        print(f"Not found: {', '.join(missing)}. Non-Claude providers keep no Claude Code transcript.")


if __name__ == "__main__":
    sys.exit(main())
