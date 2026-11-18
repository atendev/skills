# skills

My collection of skills for AI coding agents such as Claude Code. Each skill is a folder under `skills/` with a `SKILL.md` that tells the agent when to use it and what to do.

## Skills

- **simply.** Makes the agent write in plain, easy English. It also shrinks long text into a short summary. The agent calls it when you ask ("simply", "tldr", "too technical") and on its own before long or jargon-heavy replies.
- **wayfinder.** Plans a large piece of work as a map of decision tickets, then resolves them one at a time. This is my edited copy of Matt Pocock's skill. It uses a local `.plan/` folder as the tracker and pins research subagents to a cheaper model. See `NOTICE`.
- **wayfinder-master.** Hands ready wayfinder tickets to `wayfinder-runner` threads in batches. It picks the cheapest model that can do each ticket and merges each finished batch.
- **wayfinder-runner.** Runs the next wayfinder ticket from start to finish. It implements the ticket, has a three-model council audit it, commits, watches CI, and fixes failures.
- **council-audit.** Has three auditors from three providers (Claude, Gemini and GPT) judge finished work in parallel. Each returns APPROVE or DISAPPROVE, a score from 1 to 10 and a list of problems. `wayfinder-runner` uses it as its audit gate.
- **youtube-breakdown.** Fetches a YouTube transcript and turns it into a short breakdown with a TL;DR, key points and timestamps.
- **apple.** Applies Apple's Human Interface Guidelines, with exact numbers for tap targets, type sizes, spacing, safe areas and contrast.
- **link-skills.** Keeps one global skills folder and links it into every AI tool you have installed. The agent calls it when a skill is missing from a tool or after you add a skill.

## Install

Clone the repo and run the wizard.

```sh
git clone https://github.com/atendev/skills.git ~/Documents/Github/skills
bash ~/Documents/Github/skills/install.sh
```

The wizard lists each skill and asks `Install <skill> [y/n]`. Then it finds the AI tools on your machine and asks which ones to link. It shows the plan and waits for your OK before it changes anything. You can also pipe it from the web, which clones the repo to `~/.local/share/atendev-skills` first.

```sh
curl -fsSL https://raw.githubusercontent.com/atendev/skills/main/install.sh | bash
```

Start a new session in each tool so it finds the skills.

## How the linking works

All skills live in one global folder, `~/.agents/skills`. Each installed AI tool gets one symlink per skill, from its own `skills/` folder to the global folder. Skills that ship with a tool stay in that tool's folder and are never touched. The script only creates folders and symlinks and appends a note. It never deletes or overwrites anything. It leaves real folders and wrong links alone and tells you about them. It also adds a short install rule note to each tool's global instruction file where it can (Claude Code, Codex and Gemini CLI), and prints the text to paste for the others. Use `--no-note` to skip that.

Install new skills into `~/.agents/skills`, then run `skills/link-skills/scripts/link-skills.sh` (or ask your agent to run the `link-skills` skill). Use `--dry-run` first to see the plan.

Link each skill under the folder name it already has. Some skills call scripts at `~/.claude/skills/<name>/`, so a different folder name breaks them.

## Skills that depend on others

- `wayfinder-runner` calls `council-audit`, so install the two together.
- `council-audit` relies on T3 Code's `delegate_task` tool, the Jev toolbox's `ask_jev_model_audit` tool, and the `claude` and `gemini` command line tools.
- The wayfinder skills expect a `.plan/` folder in your project to track maps and tickets.
- `youtube-breakdown` runs `scripts/yt.py` and needs Python 3.

## Adding a skill

Make a folder under `skills/` with a `SKILL.md` that starts with a `name` and a `description`. The description is what lets the agent decide when to use it.

## License

MIT. See `LICENSE`. The `wayfinder` skill is derived from Matt Pocock's work, which is also MIT. See `NOTICE`.
