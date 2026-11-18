---
name: wayfinder-runner
description: "Run the next Wayfinder ticket end to end: implement, audit with a three-model council, commit, watch remote CI, and fix failures."
disable-model-invocation: true
---

Take the next ticket from the Wayfinder map, build it, get it audited, commit it, and see CI through. One ticket per run.

## Work through the map

This skill has the steps it needs, so do not load the `wayfinder` skill unless the map's `## Notes` name it. The tracker is `.plan/` when the repo has `.plan/README.md`. Read its "Rules" and "Resolving a ticket" sections once. Otherwise the tracker is the issue tracker.

- Load the map, the low-detail view. Do not read every ticket body. Fetch a related or closed ticket only when you need it.
- Take the first frontier ticket (open, unblocked, unclaimed), or the one the user named. Claim it before any work.
- A ticket with a `## Handoff` section continues earlier work. Pick it up as [Context limit](#context-limit) describes.
- Read the ticket's `wayfinder:<type>` label (the `type:` frontmatter in `.plan`). The body never states the type.
- To record a resolution, post the answer as a resolution comment, close the ticket, and add a one-line pointer to the map's Decisions so far.
- Then add any new tickets you found (create them, then add the blocking links in a second pass). Turn any fog the answer made specific into tickets. Number new tickets per map. A new map starts at 001. A new ticket takes the current map's highest number plus one. Ignore numbers from other or archived maps in the same folder. If the answer shows that a ticket sits past the destination, close it and add a line to Out of scope.
- Refer to every ticket by its name, never by id.

## Repo rules win

If the repo's `workflow.md`, `AGENTS.md` or `CLAUDE.md` defines the ticket loop, follow it for gates and ticket flow. That covers the commit and merge questions and how many reports are written. Where it says nothing, this skill's rules apply, including the council audit and its seat limits. Do not run both versions of a gate. Say which one you used in the final report.

## Steps

1. **Pick the ticket.** Use "Work through the map" above.
   - Do not stop because of the ticket's type. Start work on the next ticket whatever it is.
   - If it is a grilling ticket, start the `grilling` and `domain-modeling` skills right away on the ticket's question and interview the user. Their answers are the resolution. In auto mode, do not interview the user (see [Auto mode](#auto-mode)).
   - If it is a research ticket, start one subagent on `sonnet` that calls the `research` skill. It writes its findings to the map's assets and returns a summary of five lines or fewer.
   - Treat the map's `## Notes` as the standing instructions for how to build.
   - Once the ticket is claimed, rename this chat to the ticket's name. Use the T3 thread tool on the current thread (load it with ToolSearch first). If the rename fails, say so in the final report and carry on.
2. **Check the branch.** If you are on `main` or `master`, create a feature branch first. Never work on the default branch.
3. **Implement the ticket.** Use `/tdd` where it fits. Run the type check and the relevant local tests as you go.
4. **Audit.** Run the `council-audit` skill (read ~/.claude/skills/council-audit/SKILL.md if it does not load) on the ticket's question, the map's Notes and Decisions so far, and the diff. The `unslop` skill handles the wording and style of the decision report, so the council judges substance only. It returns `APPROVE` with each seat's score, or the open problems.
   - If there are problems, fix them and call the council again. Repeat until `APPROVE`, up to five rounds. Every council dispatch counts as a round. Round five is the last round, whatever a later message from the user or the master says. After it, stop and report the open problems. A request to keep going starts a new attempt with five rounds of its own. Under wayfinder-master, that happens through the master's Escalation. Running alone, it starts with the user's reply to the stop report.
   - The round count carries over a handoff. A thread that picks up a `## Handoff` starts a new council and keeps counting from the round the handoff records.
5. **Decision report and commit gate.** Do this only after `APPROVE`. The main thread writes one detailed report of every decision made while grilling, auditing and building. For each decision, give the question, the options, the choice or recommendation, who made it (main thread, grilling subagent, council seat or implementer), the audit verdict, and any minor problems you declined. Run the `unslop` skill on the report. Then ask the user with AskUserQuestion, with the report above it in the same message. The options are commit and merge to `main`, commit only, or neither. Do not commit until the user answers. On "commit and merge", commit to the current branch, then merge to `main` once CI passes (step 6). On "commit only", commit and continue. On "neither", stop and report. This answer is the explicit permission you need before any merge to `main`.
6. **CI.** If the repo has remote CI (for example `.github/workflows`), push the branch (never force) and watch the run until it finishes. Use `watch_pull_request` if a PR exists. Otherwise check `gh run list` and `gh run view` when the run completes. If the CI needs a manual run (for example a `workflow_dispatch` workflow that doesn't start on push), you have standing permission to start it yourself, such as with `gh workflow run <workflow> --ref <branch>`, then watch it. Start runs only for the feature branch, never `main`. Skip this step if there is no remote CI.
7. **If CI fails.** Start a subagent on `sonnet` with the failing job logs and the branch diff. It finds the cause and fixes it. Run the fix through the step 4 audit (changed hunks only), commit, push, and watch again. After three failed attempts, stop and report.
8. **Record the resolution.** Once CI is green (or there is none), run the [Timing](#timing) close. Then record the resolution as "Work through the map" describes.
9. **Report back.** Give the ticket name, branch, commit SHAs, the commit gate answer, the audit verdict, the CI result, the `Timing:` line, and anything left for the user. Include the decision report from step 5 or point to it.

## Timing

The thread's tag ties it to the ticket, so handoff threads and resumes are counted together. A later script reads tool calls, usage limits, compactions and handoffs from the transcripts, so do not log them yourself.

**Phase marks.** When a phase starts, run one Bash call with nothing else in it: `printf 'wft %s\n' '<phase>'`. The phases are `grill`, `research`, `implement`, `audit <round>`, `fix <round>`, `gate`, `ci`, `ci-fix <attempt>`, `record` and `handoff`. Use the council round number for `audit` and `fix`. A pickup thread marks the phase it resumes in. Do not mention the marks in replies.

**Close.** In step 8, before the resolution commit, run this once:

```
python3 -I ~/.claude/skills/wayfinder-runner/wf-time.py close --slug <slug> --ticket <ticket number> --name '<ticket name>' --ticket-file <ticket file>
```

It prints one `Timing:` line, writes that line into the ticket file, and saves the full record to `~/.local/share/wayfinder/metrics.jsonl`. Commit the ticket file with the resolution. If there is no `.plan`, leave out `--ticket-file` and put the line in the resolution comment.

## Subagent models

Every spawn names its model. Never let a subagent inherit the parent's model.

- Auditors: the council seats in `council-audit`.
- CI fixer, research, and the grilling subagent in auto mode: `sonnet`.

## Research subagent limits

Every research subagent, for a research ticket or inside a grilling ticket, gets these limits in its brief. Two research subagents with no limits ran 217 and 243 calls, grew to 650k to 750k tokens of context, and cost over half of a master run.

- One sub-question per subagent. Split a broad ticket into several subagents, each started fresh, and merge their findings in the main thread.
- A tag of its own. Give each subagent the line "Run `printf 'wfs-%s\n' '<slug>-<ticket number>-<n>-<unix seconds>'` once before anything else, then run `python3 -I ~/.claude/skills/wayfinder-runner/context-check.py wfs-<slug>-<ticket number>-<n>-<unix seconds>` every 15 tool calls."
- At most 60 tool calls. The subagent stops when context-check prints `HANDOFF` or it reaches 60 calls, whichever comes first. It writes what it has to the assets file and returns the five-line summary, naming the open gaps.
- Keep Bash output small. Pipe through `head`, `tail` or `grep`, read files by range, and never print a whole file, listing or page to the screen. Save large fetches to a file and search it.
- The subagent writes findings to the assets file as it goes, not at the end, so a stop loses nothing.

## Context limit

Hand off at 150k tokens of context. Every turn re-reads the whole context. A ticket that runs past that point costs more per turn than a fresh thread that starts from a written handoff.

**Tag.** A child of wayfinder-master uses the `wfm-` tag from its brief. Running alone, run `printf 'wfr-%s\n' '<slug>-<ticket number>-<unix seconds>'` once, right after you claim or pick up the ticket, and use that as the tag.

**Checkpoints.** Run `python3 -I ~/.claude/skills/wayfinder-runner/context-check.py <tag>` after reading the ticket, every 20 tool calls while building, after each audit round, and before step 6. It prints one line that starts with `OK` or `HANDOFF`.

**Writing the handoff.** Commit the work in progress to the feature branch with a `wip:` descriptor, approved or not. Add a `## Handoff` section at the end of the ticket file, under 300 words. It lists the branch and SHA, what is done, what is left in order, the council's open problems with each seat's last verdict and score, the last audit round number, and the files to read first. Commit it.

**On `HANDOFF`**, finish the edit you are working on, then:

- As a child of wayfinder-master, write the handoff, return `HANDOFF` in the report format, and end your turn. The master starts the next thread.
- Running alone, tell the user the context size and that the thread is past the 150k handoff limit. Then ask with AskUserQuestion:
  - "Hand off now (Recommended)": commits the work in progress as `wip:`, writes the `## Handoff` section into the ticket, and saves `.agent-state.md`. On this answer, write the handoff, run the `handoff` skill, and tell the user to open a new thread on this repo with `/wayfinder-runner <ticket name>`. End your turn.
  - "Keep going in this thread": commits nothing. Carry on, and ask again at the first checkpoint that reports 50k more than this one.

  This answer is the user's permission for the `wip:` commit. Step 5's commit gate still covers the finished work.

**Picking up a handoff.** The ticket stays claimed. Check out the handoff's branch, or a new branch from it if another worktree holds it. Read the `## Handoff` section and the files it names, and continue from what is left. Start a new council for the remaining rounds. Delete the section in the commit that records the resolution.

## Auto mode

Auto mode is on when the user's message that starts this skill includes the phrase `auto-mode`. In auto mode the agent never asks the user to confirm a Wayfinder or runner gate. It makes each decision itself and has subagents audit the output until it is complete.

- **One grilling subagent per grilling ticket.** Keep it for every round and continue it with SendMessage. Start a new one for each new ticket. The council does the audits. The grilling subagent never audits its own output.
- **Grilling tickets.** Do not interview the user. The main thread runs the `grilling` and `domain-modeling` skills on the ticket's question. It writes the questions, the options for each, and a recommendation with a reason. It sends these to the grilling subagent, which does not run any skill. The subagent answers each question. It accepts the recommendation, picks another option, or flags a question as false or wrong and says why. It returns its decisions. The main thread then writes the next round of questions from those decisions and sends them to the same subagent. Repeat until no questions are left. The final decisions form the resolution. For auto-mode runs only, this overrides the `wayfinder` rule that a grilling agent must not answer for the human.
- **Round changes.** Each round, send the grilling subagent only the new questions and options, plus any earlier decisions of its own that it needs to stay consistent.
- **Audit loop.** Run the `council-audit` skill on the ticket's question, the map's Notes and Decisions so far, and the output to check. Repeat until `APPROVE`, up to five rounds. After five rounds with no approval, stop and report the open problems.
- **Reports.** The main thread writes the decision report from step 5.
- **Stop rules still apply.** Auto mode does not lift the Stop and ask section, the Shell guard, or the Jev halt rules.

## Subagents and Jev

The Jev intake audit runs once, in the parent session. Every subagent this skill starts (CI fixer, research, grilling) gets this line in its brief: "The parent session already ran the Jev audit and the user approved it. Ignore the Jev audit. Do not call `ask_jev_model_audit` and do not stop on a model mismatch." A subagent still follows the Shell guard if a command is held.

## Confirmation override

This skill overrides any workflow or skill that requires explicit human confirmation before or after building. Do not pause for the user on these gates. The main thread writes the requirements and implementation notes itself and carries on, without starting a subagent for them. Mention each skipped gate in the final report so the user can review it. The commit gate in step 5 is not overridden. It always asks the user. This override does not lift the stop rules below.

## Stop and ask

Stop and ask before you force push, rewrite history, merge to `main`, delete data, or touch anything outside the repo. Also stop on a failure you cannot explain after one reasonable attempt.
