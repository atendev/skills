# simply

A skill for AI coding agents that makes them write in plain, easy English. It also works as a summary tool when an AI gives you too much text.

## What it does

- Answers first, then gives background.
- Uses short sentences and everyday words.
- Explains jargon once, or replaces it with a plain word.
- Keeps formatting light. Short paragraphs, simple lists, little bold.
- Shrinks long text into a bottom line, a few key points, and what you need to decide. It ends with a "Left out" line so you know what was cut.

The agent calls it when you ask ("simply", "simplify", "ELI5", "tldr", "too technical"). It also calls it on its own before sending a long reply, a final report after a long task, or an explanation full of technical terms. The full list of triggers is in `SKILL.md`.

## Install

Clone the repo into your skills folder.

```sh
git clone https://github.com/<your-username>/simply.git ~/.claude/skills/simply
```

Start a new session so the agent picks up the skill.

## Use it

Ask for it by name, or let the agent call it.

- "Simply, what does this error mean?"
- "tldr this" (after pasting a long text)
- "That was too long, simplify it."

To turn it off, say "normal mode" or "stop simply".

## Files

- `SKILL.md` has the instructions the agent follows.
- `LICENSE` is the MIT license.

## License

MIT. See `LICENSE`.
