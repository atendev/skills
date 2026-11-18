---
name: youtube-breakdown
description: Fetch a YouTube video's transcript and turn it into a tight, unslopped breakdown (TL;DR, key points, timestamps). Use whenever the user shares a youtube.com or youtu.be link, or asks to summarize, break down, take notes on, or pull the main points from a YouTube video, talk, podcast episode, or lecture, even if they never say "transcript".
---

# YouTube breakdown

## 1. Fetch

Run exactly one command; it prints a compact transcript (title, word count, a `[m:ss]` marker every 2 minutes):

```bash
~/.claude/skills/youtube-breakdown/scripts/yt.py "<url-or-id>"
```

Flags: `--lang es,en` sets language priority (it falls back to auto-translation). `--every 300` makes markers sparser. `--out path.txt` also saves the raw text, but only add it if the user asks for the transcript itself.

Don't search the web, open the page, or re-fetch. The transcript is the source. If the script errors (captions disabled, private video, IP block), report the error in one line and stop.

## 2. Break down

Write it straight from the transcript. Default shape (adjust if the user asked for something specific):

```
**<Title>** — <channel>
**TL;DR:** 1–2 sentences: the core claim or answer.
**Key points**
- [m:ss] point (one line each, 4–8 points, ordered as in the video)
**Worth noting:** claims needing a source, caveats, or concrete numbers/tools/names mentioned (omit if none)
```

Scale it to the video: a 3-minute clip gets a TL;DR and 2–3 bullets. Paraphrase; quote a line only when the exact wording matters. Keep it short. Cut sponsor reads, intros, and "like and subscribe".

## 3. Unslop

Apply the `unslop` skill to the breakdown before you show it. If it's already loaded this session, don't reload it.
