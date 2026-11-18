# skills

My collection of skills for AI coding agents such as Claude Code. Each skill is a folder under `skills/` with a `SKILL.md` that tells the agent when to use it and what to do.

## Skills

- **simply.** Makes the agent write in plain, easy English. It also shrinks long text into a short summary. The agent calls it when you ask ("simply", "tldr", "too technical") and on its own before long or jargon-heavy replies.
- **wayfinder.** Plans a large piece of work as a map of decision tickets, then resolves them one at a time. This is my edited copy of Matt Pocock's skill. It uses a local `.plan/` folder as the tracker and pins research subagents to a cheaper model. See `NOTICE`.
- **wayfinder-master.** Hands ready wayfinder tickets to `wayfinder-runner` threads in batches. It picks the cheapest model that can do each ticket and merges each finished batch.
- **wayfinder-runner.** Runs the next wayfinder ticket from start to finish. It implements the ticket, has a three-model council audit it, commits, watches CI, and fixes failures.
- **youtube-breakdown.** Fetches a YouTube transcript and turns it into a short breakdown with a TL;DR, key points and timestamps.
- **apple.** Applies Apple's Human Interface Guidelines, with exact numbers for tap targets, type sizes, spacing, safe areas and contrast.

## Install

Clone the repo, then link the skills you want into your skills folder.

```sh
git clone https://github.com/atendev/skills.git ~/Documents/Github/skills
ln -s ~/Documents/Github/skills/skills/simply ~/.claude/skills/simply
```

Link every skill under the folder name it already has. Some skills call scripts at `~/.claude/skills/<name>/`, so a different folder name breaks them. Start a new session so the agent finds the skills.

## Skills that depend on others

- `wayfinder-runner` calls a `council-audit` skill that isn't in this repo yet.
- The wayfinder skills expect a `.plan/` folder in your project to track maps and tickets.
- `youtube-breakdown` runs `scripts/yt.py` and needs Python 3.

## Adding a skill

Make a folder under `skills/` with a `SKILL.md` that starts with a `name` and a `description`. The description is what lets the agent decide when to use it.

## License

MIT. See `LICENSE`. The `wayfinder` skill is derived from Matt Pocock's work, which is also MIT. See `NOTICE`.
