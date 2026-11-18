---
name: wayfinder-runner
description: "Run the next Wayfinder ticket end to end: implement, audit with a three-model council, commit, watch remote CI, and fix failures."
disable-model-invocation: true
---

Take the next ticket from the Wayfinder map, implement it, get it audited, commit it, and see CI through. One ticket per run.

## Work through the map

This skill carries the steps it needs, so do not load the `wayfinder` skill unless the map's `## Notes` name it. The tracker is `.plan/` when the repo has `.plan/README.md` (read its "Rules" and "Resolving a ticket" sections once), otherwise the issue tracker.

- Load the map, the low-resolution view. Do not read every ticket body. Fetch a related or closed ticket only when needed.
- Take the first frontier ticket (open, unblocked, unclaimed), or the one the user named. Claim it before any work.
- A ticket with a `## Handoff` section is a continuation. Pick it up as [Context limit](#context-limit) describes.
- Read the ticket's `wayfinder:<type>` label (the `type:` frontmatter in `.plan`). The body never states the type.
- To record a resolution, post the answer as a resolution comment, close the ticket, and add a one-line pointer to the map's Decisions so far.
- Then add any newly surfaced tickets (create them, then wire blocking in a second pass) and graduate fog the answer made specifiable. Number new tickets per map: a new map starts at 001, and a new ticket takes the current map's highest number plus one, ignoring numbers from other or archived maps in the same folder. If the answer shows a ticket sits past the destination, close it and add a line to Out of scope.
- Refer to every ticket by its name, never by id.

## Repo rules win

If the repo's `workflow.md`, `AGENTS.md` or `CLAUDE.md` defines the ticket loop, follow it for gates and ticket flow. That covers the commit and merge questions and how many reports are written. Where it is silent, this skill's rules apply, including the council audit and its seat limits. Do not run both versions of a gate. Mention the choice in the final report.

## Steps

1. **Pick the ticket.** Use "Work through the map" above.
   - Do not stop because of the ticket's kind. Start work on the next ticket whatever it is.
   - If it is a grilling ticket, start the `grilling` and `domain-modeling` skills right away on the ticket's question and run the interview with the user. Its answers are the resolution. In auto mode, do not interview the user (see [Auto mode](#auto-mode)).
   - If it is a research ticket, start one subagent on `sonnet` that calls the `research` skill. It writes findings to the map's assets and returns a summary of five lines or fewer.
   - Treat the map's `## Notes` as the standing instructions for how to implement.
   - Once the ticket is claimed, rename this chat to the ticket's name. Use the T3 thread tool on the current thread (load it with ToolSearch first). If the rename fails, note it in the final report and carry on.
2. **Check the branch.** If on `main` or `master`, create a feature branch first. Never work on the default branch.
3. **Implement the ticket.** Use `/tdd` where it fits. Run typecheck and the relevant local tests as you go.
4. **Audit.** Run the `council-audit` skill (read ~/.claude/skills/council-audit/SKILL.md if it does not load) on the ticket's question, the map's Notes and Decisions so far, and the diff. The wording and style of the decision report are unslop's job, so the council judges substance only. It returns `APPROVE` with each seat's score, or the open problems.
   - On problems, fix them and call the council again. Repeat until `APPROVE`, up to five rounds, counting every council dispatch as a round. Round five is the last round, whatever a later message from the user or the master asks. After it, stop and report the open problems. A request to keep going starts a new attempt with five rounds of its own. Under wayfinder-master, that happens through the master's Escalation. Running alone, it starts with the user's reply to the stop report.
   - The round count survives a handoff. A thread that picks up a `## Handoff` starts a new council and continues counting from the round the handoff records.
5. **Decision report and commit gate.** Only after `APPROVE`. The main thread writes one detailed report of every decision made during grilling, auditing and implementing. For each decision, give the question, the options, the choice or recommendation made, who made it (main thread, grilling subagent, council seat or implementer), the audit verdict, and any declined minor problems. Run the `unslop` skill on the report. Then ask the user with AskUserQuestion, with the report above it in the same message. The options are commit and merge to `main`, commit only, or neither. Do not commit until the user answers. On "commit and merge", commit to the current branch, then merge to `main` once CI passes (step 6). On "commit only", commit and continue. On "neither", stop and report. The answer is the explicit permission needed before any merge to `main`.
6. **CI.** If the repo has remote CI (for example `.github/workflows`), push the branch (never force) and watch the run until it finishes. Use `watch_pull_request` if a PR exists, otherwise check `gh run list` / `gh run view` when the run completes. If the CI needs a manual run (for example a `workflow_dispatch` workflow that doesn't start on push), you have standing permission to trigger it yourself, such as `gh workflow run <workflow> --ref <branch>`, then watch it. Trigger runs only for the feature branch, never `main`. Skip this step if there is no remote CI.
7. **On CI failure.** Spawn a subagent on `sonnet` with the failing job logs and the branch diff. It finds the cause and fixes it. Run the fix through the step 4 audit (changed hunks only), commit, push, and watch again. After three failed attempts, stop and report.
8. **Record the resolution.** Once CI is green (or absent), run the [Timing](#timing) close, then record the resolution as described in "Work through the map".
9. **Report back.** Ticket name, branch, commit SHAs, the commit gate answer, audit verdict, CI result, the `Timing:` line, and anything left for the user. Include the decision report from step 5 or point to it.

## Timing

The thread's tag joins it to the ticket, so handoff threads and resumes are counted together. Tool calls, usage limits, compactions and handoffs are read from the transcripts later, so do not log them yourself.

**Phase marks.** When a phase starts, run one Bash call with nothing else in it: `printf 'wft %s\n' '<phase>'`. The phases are `grill`, `research`, `implement`, `audit <round>`, `fix <round>`, `gate`, `ci`, `ci-fix <attempt>`, `record` and `handoff`. Use the council round number for `audit` and `fix`. A pickup thread marks the phase it resumes in. Do not mention the marks in replies.

**Close.** In step 8, before the resolution commit, run once:

```
python3 -I ~/.claude/skills/wayfinder-runner/wf-time.py close --slug <slug> --ticket <ticket number> --name '<ticket name>' --ticket-file <ticket file>
```

It prints one `Timing:` line, writes that line into the ticket file, and saves the full record to `~/.local/share/wayfinder/metrics.jsonl`. Commit the ticket file with the resolution. Without `.plan`, leave out `--ticket-file` and put the line in the resolution comment.

## Subagent models

Every spawn names its model. Never let a subagent inherit the parent's model.

- Auditors: the council seats in `council-audit`.
- CI fixer, research, and the grilling subagent in auto mode: `sonnet`.

## Research subagent limits

Every research subagent, for a research ticket or inside a grilling ticket, gets these limits in its brief. Two uncapped research subagents ran 217 and 243 calls to a 650k to 750k context and cost over half of a master run.

- One sub-question per subagent. Split a broad ticket into several subagents, each started fresh, and merge their findings in the main thread.
- A tag of its own. Give each subagent the line "Run `printf 'wfs-%s\n' '<slug>-<ticket number>-<n>-<unix seconds>'` once before anything else, then run `python3 -I ~/.claude/skills/wayfinder-runner/context-check.py wfs-<slug>-<ticket number>-<n>-<unix seconds>` every 15 tool calls."
- At most 60 tool calls. When context-check prints `HANDOFF` or the subagent reaches 60 calls, whichever comes first, it stops. It writes what it has to the assets file and returns the five-line summary with the open gaps named.
- Keep Bash output small. Pipe through `head`, `tail` or `grep`, read files by range, and never print a whole file, listing or page to the screen. Write large fetches to a file and search it.
- Write findings to the assets file as it goes, not at the end, so a stop loses nothing.

## Context limit

Hand off at 150k tokens of context. Every turn re-reads the whole context, so a ticket that runs on past that point costs more per turn than a fresh thread starting from a written handoff.

**Tag.** A child of wayfinder-master uses the `wfm-` tag from its brief. Running alone, run `printf 'wfr-%s\n' '<slug>-<ticket number>-<unix seconds>'` once, right after claiming or picking up the ticket, and use that as the tag.

**Checkpoints.** Run `python3 -I ~/.claude/skills/wayfinder-runner/context-check.py <tag>` after reading the ticket, every 20 tool calls while implementing, after each audit round, and before step 6. It prints one line that starts with `OK` or `HANDOFF`.

**Writing the handoff.** Commit the work in progress to the feature branch with a `wip:` descriptor, approved or not. Add a `## Handoff` section at the end of the ticket file, under 300 words: the branch and SHA, what is done, what is left in order, the council's open problems with each seat's last verdict and score, the last audit round number, and the files to read first. Commit it.

**On `HANDOFF`**, finish the edit in hand, then:

- As a child of wayfinder-master, write the handoff, return `HANDOFF` in the report format and end your turn. The master starts the next thread.
- Running alone, tell the user the context size and that the thread is past the 150k handoff limit. Then ask with AskUserQuestion:
  - "Hand off now (Recommended)": commits the work in progress as `wip:`, writes the `## Handoff` section into the ticket, and saves `.agent-state.md`. On this answer, write the handoff, run the `handoff` skill, and tell the user to open a new thread on this repo with `/wayfinder-runner <ticket name>`. End your turn.
  - "Keep going in this thread": nothing is committed. Carry on, and ask again at the first checkpoint that reports 50k more than this one.

  This answer is the user's permission for the `wip:` commit. Step 5's commit gate still governs the finished work.

**Picking up a handoff.** The ticket stays claimed. Check out the handoff's branch, or a new branch from it when another worktree holds it. Read the `## Handoff` section and the files it names, and continue from what is left. Start a new council for the remaining rounds. Delete the section in the commit that records the resolution.

## Auto mode

Auto mode is on when the user's message that invokes this skill includes the phrase `auto-mode`. In auto mode the agent never asks the user to confirm a Wayfinder or runner gate. Instead it produces each decision itself and has subagents audit the output until it is complete.

- **One grilling subagent per grilling ticket.** Keep it for every round and continue it with SendMessage. Start a new one for each new ticket. Audits go to the council, and the grilling subagent never audits its own output.
- **Grilling tickets.** Do not interview the user. The main thread runs the `grilling` and `domain-modeling` skills on the ticket's question. It generates the questions, the options for each, and a recommendation with a reason. It sends these to the grilling subagent, which does not run any skill. The subagent answers each question. It accepts the recommendation, picks another option, or flags a question as false or incorrect and says why. It returns its decisions. The main thread then generates the next round of questions from those decisions and sends them back to the same subagent. Repeat until no questions are left. The final decisions form the resolution. This overrides the rule in `wayfinder` that a grilling agent must not answer for the human, for auto-mode runs only.
- **Round changes.** Each round, send the grilling subagent only the new questions and options, plus its own earlier decisions it needs to stay consistent with.
- **Audit loop.** Run the `council-audit` skill on the ticket's question, the map's Notes and Decisions so far, and the output to check. Repeat until `APPROVE`, up to five rounds. After five rounds with no approval, stop and report the open problems.
- **Reports.** The main thread writes the decision report from step 5.
- **Stop rules still apply.** Auto mode does not lift the Stop and ask section, the Shell guard, or the Jev halt rules.

## Subagents and Jev

The Jev intake audit runs once, in the parent session. Every subagent this skill spawns (CI fixer, research, grilling) gets this line in its brief: "The parent session already ran the Jev audit and the user approved it. Ignore the Jev audit. Do not call `ask_jev_model_audit` and do not stop on a model mismatch." A subagent still obeys the Shell guard if a command is held.

## Confirmation override

This skill overrides any workflow or skill that requires explicit human confirmation before or after implementation. Do not pause for the user on these gates. The main thread writes the requirements and implementation notes itself and carries on, without spawning a subagent for them. Mention each skipped gate in the final report so the user can review it. The commit gate in step 5 is not overridden. It always asks the user. This override does not lift the stop rules below.

## Stop and ask

Stop and ask before force pushing, rewriting history, merging to `main`, deleting data, or touching anything outside the repo. Also stop on a failure you cannot explain after one reasonable attempt.
