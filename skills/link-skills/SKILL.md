---
name: link-skills
description: Link skills from one global folder (~/.agents/skills) into every installed AI tool, such as Claude Code, Codex, Cursor, Gemini CLI, Cline and Kiro. It also adds a short install rule to each tool's global instruction file. Call it when the user asks to link, sync or share skills across AI tools; says a skill is missing or not showing up in one tool; has just installed a new skill or a new AI tool; or asks where skills should be installed.
---

# Link skills

## What it does

One global folder, the hub, holds every skill. The hub is `~/.agents/skills` by default. This skill gives each installed AI tool one symlink per skill, from the tool's own skills folder to the hub entry. Skills that ship with a tool stay in that tool's own folder and are never touched.

It also makes sure each tool's global instruction file holds a short install rule note, so agents know where new skills go. The note only goes in if the file lacks it. It is never rewritten.

The script creates folders and symlinks, and appends a short note to instruction files. It never deletes or overwrites anything.

Instruction files it edits: `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` and `~/.gemini/GEMINI.md`. A missing file is created. A symlink or an unwritable file is left alone. Cursor, Cline and Kiro get a message with the note text to paste yourself.

## Install rule

Install new skills into `~/.agents/skills`, then run this skill so every AI tool can see them. Skills that ship with a tool stay in that tool's own folder.

## Steps

1. Find the script at `scripts/link-skills.sh` inside this skill's own folder. This skill is usually reached through a symlink, so resolve the real path first (for example `readlink -f` or `cd -P`).
2. Run it with `--dry-run` and any flags the user needs. It prints a plan and changes nothing.
3. Explain the plan in plain words. Say how many links it will create, which instruction files get the note, which tools get them, and anything it will leave alone.
4. Ask the user before running it for real.
5. Only after the user says yes, run the same command again with `--yes` instead of `--dry-run`.
6. Report the result. Run the same command with `--dry-run` once more if you want to confirm that everything shows as `ok`.

Rules:

- Never delete or overwrite anything, and never run `ln -sf`, `rm` or `mv` to fix a problem.
- A `conflict` is a link that is broken or points somewhere else. An `own copy` is a real folder or file that sits where a link would go. Report both to the user. Do not fix them silently.
- Tell the user to restart each tool so it picks up the new skills.

## Flags

| Flag | Meaning |
| --- | --- |
| `--hub DIR` | The hub folder. Default `~/.agents/skills`. |
| `--from DIR` | A folder of skill folders. Each one with a `SKILL.md` is linked into the hub first. |
| `--only a,b,c` | Only these skill names. |
| `--ai t1,t2` | Only these tools: claude, codex, cursor, gemini, cline, kiro. Default: every installed tool. `--ai none` links only into `--tool-dir` folders. |
| `--tool-dir DIR` | An extra skills folder, such as `./.claude/skills` in a project. Can be repeated. |
| `--no-note` | Skip the install rule note in the tools' instruction files. |
| `--dry-run` | Show the plan and change nothing. |
| `--yes` | Do not ask before making changes. |
| `--list-tools` | Print the installed tools and their skills folders, then exit. |

A tool counts as installed if its command is on PATH or `~/.<tool>` exists. Its skills folder is `~/.<tool>/skills`.
