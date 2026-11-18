---
name: wayfinder-master
description: Dispatch Wayfinder frontier tickets to /wayfinder-runner child threads in batches, route each to the cheapest model that can do it, and merge each finished batch.
disable-model-invocation: true
---

This thread is a **dispatcher**. It routes tickets, watches CI, keeps the map and merges each batch. Children resolve every ticket, grilling included. The master's context stays small because it holds only `map.md`, one ticket body at a time, and each child's short report. Diffs, audit rounds, interviews and CI logs stay inside the children.

## Standing rules

- Run the Jev intake audit once for this thread, as CLAUDE.md says. Its halt rule covers this thread's own model only.
- The tracker is `.plan/` when the repo has `.plan/README.md`. Read its "Rules" and "Resolving a ticket" sections once. Otherwise use the issue tracker.
- Read `.plan/maps/<slug>/map.md` once at the start and again after each batch merges. Read a ticket body only right before routing it.
- Refer to every ticket by its name.
- The master works on the **master branch**, `wayfinder/<slug>-master`, cut from the default branch. It holds map edits (claims, Decisions lines, new tickets) and the merged work of every batch. Children's worktrees start from its HEAD, so commit there before spawning.
- Children commit and push their own branch. Only the master merges, and only at the end of a batch.
- Call `orchestrator_capabilities` once before the first spawn, to learn the valid model IDs and whether `effort` is an option.
- One master per map. Masters on different projects run side by side, and each has its own budget of 3 child threads, set in [Pick a batch](#loop). On Nov 13, five runs with no cap put 25 Opus threads in one hour and used up the 5-hour limit mid-batch. Before tagging this thread, run `python3 -I ~/.claude/skills/wayfinder-master/active-runs.py --slug <slug>`. A `same map:` run with 0 active child threads is an old master the user replaced to get a fresh context, so go ahead without asking. If a `same map:` run has active child threads, ask with AskUserQuestion: "Leave it to that master (Recommended)" or "Start anyway". On "Leave it", end the turn.
- At the start, note the UTC start time and set `<run>` to the Unix seconds. Then run `printf 'wfm-%s\n' '<slug>-master-<run>'` once, which tags this thread's transcript for the [Token report](#token-report).

## Loop

1. **Pick a batch.** Run `python3 -I ~/.claude/skills/wayfinder-master/active-runs.py --run <run>` and read its `slots free:` line, which counts only this run's children. A child stops holding a slot when its turn ends or it is cancelled. The batch size is the free slots, at most 3. With no slot free, tell the user which of this run's children hold them and end the turn. Take that many open, unblocked, unclaimed tickets from `map.md` with no blocking edge between them. A ticket ending in a `Last child thread:` line was given up in an earlier batch. Resume that thread as [Escalation](#escalation) describes, instead of steps 2 and 3.
2. **Pick each child's model.** The ticket's `type:` sets the default:
   - research: sonnet, medium effort
   - task: sonnet, high effort
   - grilling or design: opus, high effort

   Then run `ask_jev_model_audit` with `current_model` set to this thread's model ID and `task_prompt` set to the ticket body and its `type:` only. Jev can raise a sonnet default to opus, and only when it returns opus with `task_scope` of `complex_architecture` and `model_confidence` of 70% or more. Effort stays at the default, never above high. xhigh and max are reserved for [Escalation](#escalation) resumes. The audit's `model_match` and `recommended_skills` play no part in routing, and a Jev error leaves the default in place.

   Record the pick and the reason (default, or Jev raise with its confidence) for the final report.
3. **Claim and spawn.** Claim every ticket in the batch on the master branch in one commit. Then call `delegate_task` once per ticket with `isolation: "worktree"`, `mode: "async"`, `role` set to `implementation`, `research` or `design` (grilling), `target.model` and `target.options.effort` from step 2, a title of the ticket's name, and the brief from [Child brief](#child-brief). Keep each ticket's `taskId` and `childThreadId`.
4. **Point the user at grilling children.** A grilling child interviews the user in its own thread. Tell the user once which thread to open, using its link. Then end the turn and wait for reports.
5. **Answer each report** as it arrives. Each one starts with a status word:
   - `PUSHED`: run [CI](#ci).
   - `DONE`: mark the ticket done and wait for the rest of the batch.
   - `STOPPED`: run [Escalation](#escalation).
   - `HANDOFF`: run [Handoff](#handoff).
   - `QUESTIONS`: put the child's questions, options and recommendations into one `AskUserQuestion`, then send the answers to the child with `t3_thread_send`.
   - **No status word**: a child whose turn ended with no status word is idle, not working. Read its thread status with `t3_thread_read` (limit 3). If no run is active, send it `t3_thread_send` "Your turn ended without a status word. Continue now and return DONE, STOPPED, HANDOFF, PUSHED or QUESTIONS." and say so in the next message. Never tell the user "still waiting" about a child with no active run. Before any "waiting" message, check that every unreported child has a running run.
6. **Merge the batch** when every ticket in it is `DONE` or given up. Run [Batch merge](#batch-merge).
7. **Repeat** from step 1 until the frontier is empty or the user ends the run. Then write the final report.

## Child brief

Fill the angle-bracket fields and send the rest word for word:

```
/wayfinder-runner <ticket name>

Before anything else, run `printf 'wfm-%s\n' '<slug>-<ticket number>-<run>'` once. If the skill does not load, read ~/.claude/skills/wayfinder-runner/SKILL.md and follow it. The ticket is already claimed. Map: .plan/maps/<slug>/map.md. You are a child of a wayfinder-master thread. Run the runner with these changes:

- The parent session already ran the Jev audit and the user approved it. Ignore the Jev audit. Do not call `ask_jev_model_audit` and do not stop on a model mismatch.
- Leave map.md alone. Write the resolution into the ticket file only. Return the Decisions line and any surfaced tickets in your report, and the master adds them to the map.
- Grilling ticket: interview the user in this thread with AskUserQuestion. If you cannot reach the user, return QUESTIONS with the round's questions, options and your recommendation, and end your turn. The master sends back the answers.
- Research subagents: apply the "Research subagent limits" section of the runner skill. One sub-question each, its own wfs- tag with context-check every 15 tool calls, at most 60 tool calls, a stop on HANDOFF, small Bash output, findings written to the assets file as it goes.
- Step 5 (commit gate): commit every time, with no question to the user. Write the decision report to `.plan/maps/<slug>/assets/<ticket-file>-report.md`, run unslop on it, and commit it with the work. The master merges. Your branch never merges.
- Step 6 (CI): push the branch without forcing. If the repo works through PRs, open one against `wayfinder/<slug>-master` and link it. Return PUSHED and end your turn. The master watches CI and sends you the result.
- On a "CI red" message, run step 7 with the failure it names, then return PUSHED again.
- On "CI green" or "no CI", record the resolution in the ticket file, commit, push, and return DONE.
- After five audit rounds without APPROVE, three failed CI fixes, or a failure you cannot explain, return STOPPED with the open problems. Round five is the last round, even if a later message asks you to keep going. The master answers that by starting a new attempt.
- Never end your turn while waiting on council replies or any other background result. Wait inside your turn. End a turn only with a status word.
- Context limit: follow the runner's "Context limit" section with the wfm- tag above. On HANDOFF, commit, write the `## Handoff` section into the ticket file, return HANDOFF and end your turn.

- Timing: follow the runner's "Timing" section. Run its close before the DONE commit.

Report format, at most 7 lines plus the Surfaced list:
<STATUS> | <ticket name> | branch <branch> | sha <sha or -> | audit <verdict, round number, the three seat scores and the count of minor problems declined> | CI <state>
Work: <commits> commits | <files> files, +<added> -<removed> | <passing> tests pass   (from `git rev-list --count` and `git diff --shortstat` against the master branch)
Report: <decision report path>
PR: <url or ->
Decision: <one-line Decisions pointer, on DONE>
Timing: <the close's Timing line, on DONE>
Problems: <one line each, on STOPPED>
Surfaced: <title | type | blocked-by ticket names>, one per line, on DONE
```

## Ticket messages

Post one message to the user when each child is spawned and one when it returns `DONE`, `STOPPED` or `HANDOFF`. Use these templates as written. Fill fields from the master's own state and the child's report. Write `-` for a field you don't have, and leave out a line whose list is empty.

On spawn:

```
▶ **Started: #<number> <ticket name>**
<Type> · Batch <b>, slot <s> of 3 · Attempt <a>, handoff <h>

- **Model:** <model> · <effort>
- **Branch:** `<child branch>` from `wayfinder/<slug>-master`
- **Started:** <local time> · run `wfm-<slug>-master-<run>`
```

On `DONE`, using the child's `Timing:` line for Time, Phases, Events and Cost:

```
✅ **Done: #<number> <ticket name>**
<Type> · <model> · <effort> · Batch <b>: <done> of <size> done · <local time>

**Decision:** <the child's Decision line>

| | |
|---|---|
| **Work** | <n> commits · <files> files, +<added> −<removed> · <passing> tests pass |
| **Audit** | <verdict> in round <r> · Claude <score> · Gemini <score> · GPT <score> · <n> minor declined |
| **CI** | <Green or Red> in <duration> · PR #<number> |
| **Time** | <wall> wall · <active> active · <user> user · <wait> wait · <blocked> blocked |
| **Phases** | <phase> <time> · … · audit <time> (<r> rounds) · … |
| **Events** | <n> tools (<n> subagent) · <n> limit hits (<kinds>) · <n> compactions · <n> handoffs · <ctx peak> peak context |
| **Cost** | <$ per model> · Gemini and GPT seats not measured |
| **Report** | `<decision report path>` |

**Surfaced**
- #<number> <title> · <type> · blocked by <tickets>
```

Take CI duration from the watched run (`gh run view <id> --json startedAt,updatedAt`).

On `STOPPED` or `HANDOFF`, use the `DONE` layout with the header `■ **Stopped: …**` or `↻ **Handed off: …**`. Replace the Decision line with **Problems:** (one per line) or **Handoff:** `<branch>` · audit round <r>. Leave out Surfaced. These children return no `Timing:` line, so get it with `python3 -I ~/.claude/skills/wayfinder-runner/wf-time.py close --slug <slug> --ticket <number> --dry-run`, which records nothing.

## CI

If the child returned a PR URL, call `watch_pull_request` with it. When the watch wakes you, send the child "CI green" or "CI red: <failing job and run URL>" with `t3_thread_send` to its `childThreadId`. If the repo has remote CI but no PR, find the run with `gh run list --branch <branch>`, run `gh run watch <id> --exit-status` as a background command, wait on it with `t3_background_wait`, and send the result the same way. If the repo has no remote CI, send "no CI". After the child returns `DONE`, call `unwatch_pull_request`.

## Batch merge

1. On the master branch, merge each `DONE` child branch with `--no-ff`, in blocking order where one exists. Resolve conflicts with the `resolving-merge-conflicts` skill.
2. Add every child's Decisions line to `map.md`. Create the surfaced tickets with the next numbers after the map's highest, then wire blocking in a second pass. Graduate any fog the answers made specifiable. Commit this as one commit in the CLAUDE.md commit style.
3. Run typecheck and the tests on the merged master branch. Push it and let its CI finish. A failure here comes from the merge, so fix it on the master branch with a sonnet subagent and the same limits as a CI fix.
4. Ask the user once with `AskUserQuestion`, with a batch summary above it in the same message: each ticket's decision report path, SHA, audit verdict and CI result. The options are "Merge the batch to main", "Keep it on the master branch" and "Stop". On "Merge", merge the master branch to main and push without forcing. On "Keep", start the next batch from the master branch. On "Stop", write the final report.

## Escalation

A stopped ticket keeps its thread. The thread's worktree, branch and history hold everything the child learned, and a fresh child pays to learn it again. On Nov 13 and 14, re-spawned children cost $168 of the $480 the master runs spent.

1. **First `STOPPED`: resume.** Move the thread up one step with `t3_thread_configure` (`threadId` set to the child's `childThreadId`): a sonnet child goes to opus at high effort, and an opus child goes to xhigh effort. If the tool takes no effort option, change the model only. Then send it the open problems with `t3_thread_send`. The resume is the ticket's second attempt and gets five audit rounds of its own.
2. **Second `STOPPED`: give it up.** Tell the child to commit its work as a draft. On the master branch, unclaim the ticket and add `Last child thread: <childThreadId> | branch <branch>` as the ticket file's last line, in one commit. List the ticket in the batch summary.
3. **Picking it up later.** A later batch takes a ticket with that line only when the user asks or a merged decision changed its question. Claim it, then send the same thread with `t3_thread_send`: "Merge `wayfinder/<slug>-master` into your branch, then continue with these open problems: <problems>." That resume is one attempt with five rounds. If it stops, give the ticket up again as in step 2.

When the user asks to keep retrying a stopped ticket, each request buys one resume of its thread, as in step 3.

## Handoff

`HANDOFF` means the child passed 150k tokens of context, committed its work and wrote a `## Handoff` section into the ticket on its branch. A fresh thread that starts from that section costs less per turn than the old one. Handle it without asking the user:

1. Call `delegate_task` with the old child's model, effort, role and `isolation: "worktree"`, a title of `<ticket name> (handoff <n>)`, and the [Child brief](#child-brief) with this line added after the map line: "Pick up the `## Handoff` section in the ticket on branch `<branch>` at `<sha>`. Create a new branch from it, because the old worktree still holds that branch."
2. Replace the ticket's `taskId` and `childThreadId` with the new ones. Escalation acts on the new thread from now on.
3. A handoff does not count as an attempt, and the audit round count carries over in the `## Handoff` section. A ticket's fourth handoff means it is too large for one ticket. Give it up as in Escalation step 2 and mark it "needs a split" in the batch summary.

## Token report

Show it when the user asks, at any point in the run, and offer it at the end. Run:

```
python3 -I ~/.claude/skills/wayfinder-master/token-report.py --since <start time> --baseline <this thread's model> \
  master=wfm-<slug>-master-<run> '<ticket name>=wfm-<slug>-<ticket number>-<run>' ...
```

List the master first, then one entry per child spawned so far. The script reads Claude Code transcripts, so it covers the master, every child, and each child's Claude council seat and fixer subagents. The Gemini and GPT council seats have no transcript, so say they were not measured. It prints a table per thread and model with input, cache write, cache read, output and cost, then two savings lines:

- Routing savings are measured: the same tokens priced as if every thread ran on the baseline model, minus the actual cost.
- Fresh-context savings are an estimate: the cache reads one thread would have repeated if it had run every child ticket in turn.

Show the script's output as is, then add one line per child giving the model it ran on and why. The script names any thread it could not find. A child on a non-Claude provider has no transcript, so say it was not measured. Prices live in `prices.json` next to the script. Edit that file when prices change.

## Time report

The master marks its own phases the way the runner does, with one Bash call at each start: `printf 'wft %s\n' '<phase>'`. The phases are `route` (Loop steps 1 to 3), `ci`, `merge` (Batch merge steps 1 to 3) and `gate` (Batch merge step 4). Time spent waiting for child reports is counted without a mark. Do not mention the marks in replies.

Children close their own tickets and return the `Timing:` line. For the final report, run:

```
python3 -I ~/.claude/skills/wayfinder-runner/wf-time.py close --slug <slug> --run <run>
python3 -I ~/.claude/skills/wayfinder-runner/wf-time.py report --slug <slug> --since <start time> --phases
```

The first records this thread's own time. The second prints one row per ticket and one for the master, with wall, active, user-wait, other-wait and limit-blocked time, audit rounds, tool calls, limit hits, compactions and handoffs, then the totals per phase across tickets. Show its output as is. A child on a non-Claude provider has no transcript, so it has no row.

## Final report

For each ticket, give its name, the model and effort with the reason (default or Jev raise), any escalation, the commit SHAs, the CI result, the decision report path and the child's thread link. Then give each batch's merge answer, list the tickets still on the frontier, and say whether the master branch holds work that is not on main. Include the [Time report](#time-report) output. End with an `AskUserQuestion` offering "Show the token report" or "Skip".
