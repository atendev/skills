#!/usr/bin/env python3
"""Time and event breakdown for Wayfinder tickets, read from Claude Code transcripts.

Usage:
  wf-time.py close --slug S --ticket N [--name NAME] [--ticket-file PATH] [--dry-run]
  wf-time.py close --slug S --run RUN [--dry-run]          # a wayfinder-master run
  wf-time.py report [--slug S] [--since ISO] [--phases]

A thread joins a ticket by running `printf 'wfr-%s\\n' '<slug>-<N>-<unix>'` (or the wfm-
form) once. Every top-level transcript that did so is one thread of the ticket, so
handoff threads and escalation resumes all count. Phase changes are marked with
`printf 'wft %s\\n' '<phase> [round]'`. Time before the first marker is `setup`.

`close` prints one Timing line, appends a JSON record to
~/.local/share/wayfinder/metrics.jsonl and, with --ticket-file, writes the Timing
line into the ticket (replacing an earlier one). `report` reads metrics.jsonl and
keeps the latest record per ticket.

Each gap between transcript entries is counted as one of:
  active   the agent or its subagents were working
  user     an AskUserQuestion was open, or the turn ended in a grill/gate phase
  wait     the turn ended in any other phase (master, CI), or a background wait ran
  blocked  a usage limit error until the next entry
Unclassified gaps longer than 15 minutes (60 during a tool call) count as wait.
"""
import argparse
import glob
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

PROJECTS = os.environ.get("WF_TIME_PROJECTS") or os.path.expanduser("~/.claude/projects")
METRICS = os.environ.get("WF_TIME_METRICS") or os.path.expanduser("~/.local/share/wayfinder/metrics.jsonl")
TAG_RE = re.compile(r"""printf\s+['"]wf[mr]-%s\\n['"]\s+['"]([^'"]+)['"]""")
MARK_RE = re.compile(r"""printf\s+['"]wft %s\\n['"]\s+['"]([^'"]+)['"]""")
LIMIT_RE = re.compile(r"(?:hit|reached) your ([\w -]+?limit)", re.I)
RESET_RE = re.compile(r"resets (\d{1,2})(?::(\d\d))?\s*(am|pm)\s*\(([^)]+)\)", re.I)
BLOCK_CAP = 5 * 3600
USER_PHASES = {"grill", "gate"}
WAIT_TOOLS = ("background_wait", "Monitor", "t3_thread_wait", "watch_pull_request")
IDLE_CAP = 15 * 60
TOOL_CAP = 60 * 60
CATS = ("active", "user", "wait", "blocked")
PRICES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "wayfinder-master", "prices.json")
USAGE = ("input", "cache_write_5m", "cache_write_1h", "cache_read", "output")


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def dur(s):
    s = int(s)
    if s < 60:
        return f"{s}s"
    h, m = divmod(s // 60, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m"


def reset_at(text, t):
    m = RESET_RE.search(text)
    if not m:
        return t + BLOCK_CAP
    try:
        tz = ZoneInfo(m.group(4))
    except Exception:
        return t + BLOCK_CAP
    h = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "pm" else 0)
    now = datetime.fromtimestamp(t, tz)
    r = now.replace(hour=h, minute=int(m.group(2) or 0), second=0, microsecond=0)
    if r <= now:
        r += timedelta(days=1)
    return r.timestamp()


def usage_row(d):
    msg = d.get("message") or {}
    u = msg.get("usage")
    if d.get("type") != "assistant" or not u or not msg.get("model") or msg["model"].startswith("<"):
        return None
    cc = u.get("cache_creation") or {}
    w1h = cc.get("ephemeral_1h_input_tokens", 0)
    w5m = cc.get("ephemeral_5m_input_tokens", u.get("cache_creation_input_tokens", 0) - w1h)
    vals = (u.get("input_tokens", 0), max(w5m, 0), w1h, u.get("cache_read_input_tokens", 0), u.get("output_tokens", 0))
    return msg.get("id") or id(d), msg["model"], dict(zip(USAGE, vals))


def costs(usage):
    try:
        prices = json.load(open(PRICES))
    except (OSError, json.JSONDecodeError):
        prices = {}
    by_model = defaultdict(float)
    for model, u in usage.values():
        p = prices.get(model)
        if p:
            by_model[model] += sum(u[k] * p[k] for k in USAGE) / 1e6
    return {m: round(c, 2) for m, c in by_model.items()}


def blocks(d):
    c = (d.get("message") or {}).get("content")
    return [b for b in c if isinstance(b, dict)] if isinstance(c, list) else []


def text_of(b):
    c = b.get("content")
    if isinstance(c, list):
        return " ".join(str(x.get("text", "")) for x in c if isinstance(x, dict))
    return str(c or "")


def thread_tag(path):
    with open(path, errors="replace") as f:
        for line in f:
            if "printf" not in line or "wf" not in line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") != "assistant":
                continue
            for b in blocks(d):
                if b.get("type") == "tool_use" and b.get("name") == "Bash":
                    m = TAG_RE.search(str((b.get("input") or {}).get("command", "")))
                    if m:
                        return m.group(1)
    return None


def matches(tag, slug, ticket, run):
    if run:
        return tag == f"{slug}-master-{run}"
    m = re.fullmatch(r"(.+)-(\d+)-(\d+)", tag)
    return bool(m) and m.group(1) == slug and int(m.group(2)) == int(ticket)


def find_threads(slug, ticket, run, days):
    cutoff = time.time() - days * 86400
    out = []
    for p in glob.glob(os.path.join(PROJECTS, "*", "*.jsonl")):
        if os.path.getmtime(p) < cutoff:
            continue
        tag = thread_tag(p)
        if tag and matches(tag, slug, ticket, run):
            out.append(p)
    return out


def load(path):
    rows = []
    with open(path, errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") in ("user", "assistant", "system") and d.get("timestamp"):
                rows.append(d)
    rows.sort(key=lambda d: d["timestamp"])
    return rows


def is_prompt(d):
    if d.get("type") != "user" or d.get("isMeta"):
        return False
    return not any(b.get("type") == "tool_result" for b in blocks(d))


def analyse(paths):
    phase_t = defaultdict(lambda: dict.fromkeys(CATS, 0.0))
    phase_tools = Counter()
    tools = Counter()
    sub_tools = 0
    ev = Counter()
    limit_kinds = Counter()
    rounds = 0
    first = last = None
    cwd = None
    models = Counter()
    timeline = []
    usage = {}
    ctx_peak = 0

    for path in sorted(paths, key=lambda p: (load(p) or [{"timestamp": "9"}])[0]["timestamp"]):
        rows = load(path)
        if not rows:
            continue
        cwd = cwd or next((d.get("cwd") for d in rows if d.get("cwd")), None)
        first = min(filter(None, [first, ts(rows[0]["timestamp"])]))
        last = max(filter(None, [last, ts(rows[-1]["timestamp"])]))
        phase = "setup"
        timeline.append((ts(rows[0]["timestamp"]), phase))
        pending = {}
        for i, d in enumerate(rows):
            t = ts(d["timestamp"])
            kind = None
            unblock = None
            in_tool = False
            if d.get("type") == "system" and d.get("subtype") == "compact_boundary":
                ev["compactions"] += 1
            if d.get("type") == "assistant":
                msg = d.get("message") or {}
                if msg.get("model") and not msg["model"].startswith("<"):
                    models[msg["model"]] += 1
                ur = usage_row(d)
                if ur:
                    usage[ur[0]] = ur[1:]
                    u = ur[2]
                    ctx_peak = max(ctx_peak, u["input"] + u["cache_write_5m"] + u["cache_write_1h"] + u["cache_read"])
                if d.get("isApiErrorMessage"):
                    err = " ".join(str(b.get("text", "")) for b in blocks(d))
                    m = LIMIT_RE.search(err)
                    if m:
                        ev["limit_hits"] += 1
                        limit_kinds[m.group(1).lower()] += 1
                        kind = "blocked"
                        unblock = reset_at(err, t)
                    else:
                        ev["api_errors"] += 1
                for b in blocks(d):
                    if b.get("type") != "tool_use":
                        continue
                    name = b.get("name", "")
                    cmd = str((b.get("input") or {}).get("command", "")) if name == "Bash" else ""
                    mk = MARK_RE.search(cmd)
                    if mk:
                        parts = mk.group(1).split()
                        phase = parts[0].lower()
                        timeline.append((t, phase))
                        if phase == "audit" and len(parts) > 1 and parts[1].isdigit():
                            rounds = max(rounds, int(parts[1]))
                        if phase == "handoff":
                            ev["handoffs_written"] += 1
                        continue
                    if TAG_RE.search(cmd):
                        continue
                    tools[name] += 1
                    phase_tools[phase] += 1
                    pending[b.get("id")] = name
                    in_tool = True
                    if name == "AskUserQuestion":
                        kind = "user"
                    elif any(w in name for w in WAIT_TOOLS) or "gh run watch" in cmd:
                        kind = kind or "wait"
            if d.get("type") == "user":
                for b in blocks(d):
                    if b.get("type") == "tool_result":
                        pending.pop(b.get("tool_use_id"), None)
                        if text_of(b).lstrip().startswith("HANDOFF context"):
                            ev["context_handoffs"] += 1
            if i + 1 == len(rows):
                break
            nxt = rows[i + 1]
            gap = max(ts(nxt["timestamp"]) - t, 0)
            if not kind:
                if is_prompt(nxt):
                    kind = "user" if phase in USER_PHASES else "wait"
                elif gap > (TOOL_CAP if in_tool else IDLE_CAP):
                    kind = "wait"
                else:
                    kind = "active"
            if kind == "blocked" and unblock is not None:
                b = min(gap, max(unblock - t, 0))
                phase_t[phase]["blocked"] += b
                phase_t[phase]["wait"] += gap - b
                continue
            phase_t[phase][kind] += gap

        sub = path[:-6]
        for sp in glob.glob(os.path.join(sub, "**", "*.jsonl"), recursive=True):
            for d in load(sp):
                ur = usage_row(d)
                if ur:
                    usage[ur[0]] = ur[1:]
                for b in blocks(d):
                    if d.get("type") == "assistant" and b.get("type") == "tool_use":
                        sub_tools += 1
                        t = ts(d["timestamp"])
                        ph = next((p for st, p in reversed(sorted(timeline)) if st <= t), "setup")
                        phase_tools[ph] += 1

    if first is None:
        return None
    totals = {c: sum(v[c] for v in phase_t.values()) for c in CATS}
    return {
        "threads": len(paths),
        "handoffs": max(len(paths) - 1, 0),
        "repo": cwd,
        "start": datetime.fromtimestamp(first, timezone.utc).isoformat(timespec="seconds"),
        "end": datetime.fromtimestamp(last, timezone.utc).isoformat(timespec="seconds"),
        "wall_s": round(last - first),
        **{f"{c}_s": round(totals[c]) for c in CATS},
        "phases": {p: {**{f"{c}_s": round(v[c]) for c in CATS}, "tools": phase_tools[p]}
                   for p, v in phase_t.items()},
        "audit_rounds": rounds,
        "tools_total": sum(tools.values()) + sub_tools,
        "subagent_tools": sub_tools,
        "tools_by_name": dict(tools.most_common()),
        "limit_hits": ev["limit_hits"],
        "limit_kinds": dict(limit_kinds),
        "api_errors": ev["api_errors"],
        "compactions": ev["compactions"],
        "context_handoffs": ev["context_handoffs"],
        "handoffs_written": ev["handoffs_written"],
        "models": dict(models),
        "ctx_peak": ctx_peak,
        "cost_usd": costs(usage),
    }


def timing_line(r):
    order = ["setup", "grill", "research", "implement", "audit", "fix", "gate", "ci", "ci-fix", "record", "handoff"]
    ph = sorted(r["phases"].items(), key=lambda kv: order.index(kv[0]) if kv[0] in order else len(order))
    parts = []
    for p, v in ph:
        w = sum(v[f"{c}_s"] for c in CATS)
        if w < 30:
            continue
        label = f"{p} {dur(w)}"
        if p == "audit" and r["audit_rounds"]:
            label += f" ({r['audit_rounds']} round{'s' if r['audit_rounds'] != 1 else ''})"
        parts.append(label)
    return (f"Timing: wall {dur(r['wall_s'])}, active {dur(r['active_s'])}, user {dur(r['user_s'])}, "
            f"wait {dur(r['wait_s'])}, blocked {dur(r['blocked_s'])} | {', '.join(parts) or '-'} | "
            f"tools {r['tools_total']} ({r['subagent_tools']} subagent) | limits {r['limit_hits']}"
            + (f" ({', '.join(r['limit_kinds'])})" if r["limit_kinds"] else "")
            + f", compactions {r['compactions']}, "
            f"handoffs {r['handoffs']} | ctx peak {r['ctx_peak'] // 1000}k | cost "
            + (" + ".join(f"${c:.2f} {m.replace('claude-', '')}" for m, c in r["cost_usd"].items()) or "-"))


def write_ticket(path, line):
    with open(path) as f:
        body = f.read()
    if re.search(r"^Timing: .*$", body, re.M):
        body = re.sub(r"^Timing: .*$", line, body, count=1, flags=re.M)
    else:
        body = body.rstrip("\n") + "\n\n" + line + "\n"
    with open(path, "w") as f:
        f.write(body)


def close(a):
    if not (a.ticket or a.run):
        sys.exit("close needs --ticket or --run")
    paths = find_threads(a.slug, a.ticket, a.run, a.days)
    r = analyse(paths) if paths else None
    if not r:
        who = f"run {a.run}" if a.run else f"ticket {a.ticket}"
        print(f"No transcript tagged for {a.slug} {who} in the last {a.days} days. Non-Claude threads keep none.")
        return
    rec = {"recorded": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "kind": "master" if a.run else "ticket", "slug": a.slug,
           "ticket": a.ticket, "run": a.run, "name": a.name, **r}
    line = timing_line(r)
    print(line)
    if a.dry_run:
        return
    os.makedirs(os.path.dirname(METRICS), exist_ok=True)
    with open(METRICS, "a") as f:
        f.write(json.dumps(rec) + "\n")
    if a.ticket_file:
        write_ticket(a.ticket_file, line)


def report(a):
    if not os.path.exists(METRICS):
        print("No metrics recorded yet.")
        return
    latest = {}
    for line in open(METRICS):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if a.slug and r.get("slug") != a.slug:
            continue
        if a.since and r.get("end", "") < a.since:
            continue
        latest[(r.get("repo"), r["slug"], r["kind"], r.get("ticket"), r.get("run"))] = r
    if not latest:
        print("No matching records.")
        return
    rows = sorted(latest.values(), key=lambda r: r["start"])
    print("| Ticket | Wall | Active | User | Wait | Blocked | Audit rounds | Tools | Limits | Compactions | Handoffs |")
    print("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
    tot = Counter()
    phases = defaultdict(Counter)
    for r in rows:
        label = r.get("name") or (f"{r['slug']} master {r['run']}" if r["kind"] == "master" else f"{r['slug']} #{r['ticket']}")
        print(f"| {label} | {dur(r['wall_s'])} | {dur(r['active_s'])} | {dur(r['user_s'])} | {dur(r['wait_s'])} | "
              f"{dur(r['blocked_s'])} | {r['audit_rounds']} | {r['tools_total']} | {r['limit_hits']} | "
              f"{r['compactions']} | {r['handoffs']} |")
        if r["kind"] != "ticket":
            continue
        for k in ("wall_s", "active_s", "user_s", "wait_s", "blocked_s", "tools_total", "limit_hits", "compactions", "handoffs"):
            tot[k] += r[k]
        for p, v in r["phases"].items():
            phases[p].update({k: v.get(k, 0) for k in ("active_s", "user_s", "wait_s", "blocked_s", "tools")})
    n = sum(1 for r in rows if r["kind"] == "ticket")
    if n:
        print(f"\nTickets {n}: wall {dur(tot['wall_s'])}, active {dur(tot['active_s'])}, user {dur(tot['user_s'])}, "
              f"wait {dur(tot['wait_s'])}, blocked {dur(tot['blocked_s'])}, tools {tot['tools_total']}, "
              f"limits {tot['limit_hits']}, compactions {tot['compactions']}, handoffs {tot['handoffs']}")
    if a.phases and phases:
        print("\n| Phase | Active | User | Wait | Blocked | Tools |")
        print("|---|--:|--:|--:|--:|--:|")
        for p, v in sorted(phases.items(), key=lambda kv: -kv[1]["active_s"]):
            print(f"| {p} | {dur(v['active_s'])} | {dur(v['user_s'])} | {dur(v['wait_s'])} | {dur(v['blocked_s'])} | {v['tools']} |")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("close")
    c.add_argument("--slug", required=True)
    c.add_argument("--ticket", type=int)
    c.add_argument("--run")
    c.add_argument("--name")
    c.add_argument("--ticket-file")
    c.add_argument("--days", type=int, default=30)
    c.add_argument("--dry-run", action="store_true")
    r = sp.add_parser("report")
    r.add_argument("--slug")
    r.add_argument("--since")
    r.add_argument("--phases", action="store_true")
    a = ap.parse_args()
    close(a) if a.cmd == "close" else report(a)


if __name__ == "__main__":
    main()
