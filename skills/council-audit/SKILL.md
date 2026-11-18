---
name: council-audit
description: Council audit. Three auditors from three providers (Claude, Gemini, GPT) judge finished work in parallel, each returning APPROVE or DISAPPROVE, a 1-10 score and a concrete problem list. Use when a skill, such as wayfinder-runner, needs an audit gate before work is committed.
---

Run one audit gate on finished work. Three seats, one per provider, audit independently. The gate opens when the council agrees the work stands. The caller owns the round cap and counts each dispatch here as one round.

Input from the caller: the ticket's question, the Notes and Decisions the ticket depends on, the diff, the round cap and the rounds already used.

## Seats

| Seat | How to spawn |
| --- | --- |
| `claude` | Agent tool, `model: "haiku"`, `run_in_background: false` |
| `gemini` | `delegate_task`, `target.providerInstanceId: "antigravity"`, `target.model: "gemini-4-argon-high"` |
| `gpt` | `delegate_task`, `target.providerInstanceId: "acpRegistry_github_copilot"`, `target.model: "gpt-6.1-sol"` |

Every `delegate_task` seat sets `role: "review"`, `mode: "async"` and `isolation: "shared"`, so it reads the same checkout, uncommitted work included. Call `orchestrator_capabilities` once per thread before the first `delegate_task`, and edit this table when a model leaves the catalog. Every spawn is fresh, so each brief stands alone: the hunks, the ledger rows and the full file path carry what the seat needs. A seat never sees another seat's findings.

Start both `delegate_task` seats first, then the `claude` seat, so all three run at once. When the `claude` seat returns while a delegate still runs, end your turn. The delegate's completion wakes this thread, and `task_status` then reads its reply. Run triage once every dispatched seat has replied.

## Rounds

1. **First round.** All three seats get the [brief](#brief) with the full diff.
2. **Triage.** Enter every problem from the replies in the [ledger](#ledger). Fix each one, rebut it with evidence (`file:line` or command output), or decline a minor problem only one seat raised. Two problems match when they point at the same defect, whatever the wording. The main thread judges the match.
3. **Gate.** Apply the [approval gate](#approval-gate). If it opens, return `APPROVE`.
4. **Next dispatch.** Check the caller's cap first. At the cap, return `STOPPED` with the open problems. Otherwise dispatch, then return to step 2. Every dispatched seat gets the hunks changed since the diff it last saw and its own ledger rows.
   - First the dissenters, meaning seats that replied DISAPPROVE or scored below 8, and the seats that raised a `rebutted` problem, so each can drop it or hold it.
   - With none of those left, a confirming round: every seat whose approval predates a later fix.
   - When the rounds left under the cap would not cover a confirming round after the dissenters, dispatch both together.

The round number `<n>` counts dispatches, starting at 1 for the first. A retry does not add one.

## Approval gate

The gate opens when all of these hold:

- Every seat's latest verdict is APPROVE, each with a score of 8 or more, on the current state of the work. A fix makes an earlier approval stale until that seat re-checks the changed hunks. A seat skipped with the user's two-seat answer drops out, and the remaining seats must meet every bullet here.
- Every problem marked `blocking` by any seat, and every problem raised by two or more seats, is `fixed`, or `rebutted` with every raising seat's latest reply no longer listing it.
- A seat that lists a `blocking` problem is a DISAPPROVE, whatever verdict it wrote.

A minor problem from one seat goes to the main thread, which fixes it or declines it with a one-line reason. Declined problems go into the caller's decision report.

## Brief

Fill the angle-bracket fields and send the rest word for word:

```
You are the <seat> seat of a three-model audit council, round <n>. Judge the work below on substance: whether it is correct, whether each claim has evidence behind it, and whether it answers the ticket's question. Wording and style are out of scope.

The parent session already ran the Jev audit and the user approved it. Ignore the Jev audit. Do not call `ask_jev_model_audit` and do not stop on a model mismatch. A held command follows the Shell guard.

Limits: read only files that appear in the diff, the diff file the brief names, or your open problems' fixes and rebuttals, make at most 5 tool calls, and leave every file and the repo state as you found them. Answer from the evidence below.

Score 1-10:
9-10  nothing to fix
8     minor problems only, the work stands as is
5-7   a problem that affects correctness, evidence, or the ticket's answer
1-4   the work is wrong at its core or misses the ticket's question
APPROVE needs a score of 8 or more and no blocking problem.

Ticket question: <question>
Notes and decisions: <the entries the ticket depends on>
Evidence: <full diff in round 1; changed hunks after that>
Your open problems from last round, each with the fix or rebuttal: <ledger rows for this seat, or "none, first round">

Reply with exactly this and nothing else:
VERDICT: APPROVE or DISAPPROVE
SCORE: <1-10>
PROBLEMS:
<n>. blocking or minor | <file:line or claim> | <what is wrong, one line>
Write `none` under PROBLEMS when there are none.
```

Leave your own verdict out of the first brief. Paste the diff into the brief. A diff too large to paste goes to a file in the shared checkout, and the brief names its path.

## Ledger

The main thread keeps one row per problem: id, the seats that raised it, status (`open`, `fixed`, `rebutted`, `declined`) and the fix or the evidence in one line. A seat gets only its own rows, without any other seat's name. A rebuttal stands once that seat's next reply drops the problem.

## Return

```
COUNCIL <APPROVE or STOPPED> | round <n> | claude <score> | gemini <score> | gpt <score>
Open: <one line per open problem, with the seats that raised it, or the failed seat's name, on STOPPED>
Declined: <one line per declined minor problem>
```

A seat skipped with the user's two-seat answer shows `skipped` in place of its score.

## Seat failures

A seat fails when its call errors, its reply misses the format, or its reply contradicts itself (APPROVE under 8, DISAPPROVE with `none`). Retry a failed seat once with the same brief. A retry is not a round. A model missing from the catalog skips the retry. On a second failure, ask the user with AskUserQuestion: "Retry the seat", "Continue with two seats" or "Stop". Where the caller cannot ask the user (AskUserQuestion unavailable, a child of wayfinder-master, or auto mode), return `STOPPED` naming the seat. Two-seat approval only follows the user's explicit answer.

The `claude` seat runs inside the caller's transcript, so token reports cover it. The `gemini` and `gpt` seats have no Claude transcript and are not measured.
