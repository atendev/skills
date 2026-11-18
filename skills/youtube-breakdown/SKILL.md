---
name: youtube-breakdown
description: Fetch a YouTube video's transcript and turn it into a tight, unslopped breakdown (TL;DR, key points, timestamps). Use whenever the user shares a youtube.com or youtu.be link, or asks to summarize, break down, take notes on, or pull the main points from a YouTube video, talk, podcast episode, or lecture, even if they never say "transcript".
---

# YouTube breakdown

## 1. Fetch

Run exactly one command. It prints a short transcript with the title, the word count, and a `[m:ss]` time marker every 2 minutes:

```bash
~/.claude/skills/youtube-breakdown/scripts/yt.py "<url-or-id>"
```

Flags:

- `--lang es,en` sets the language order. It falls back to auto-translation.
- `--every 300` puts the time markers further apart.
- `--out path.txt` also saves the raw text. Add it only if the user asks for the transcript itself.

Don't search the web, open the page, or fetch again. The transcript is the only source. If the script fails (captions off, private video, IP block), report the error in one line and stop.

## 2. Break down

Write it from the transcript alone. Use this shape unless the user asked for something else:

```
**<Title>** — <channel>
**TL;DR:** 1–2 sentences: the core claim or answer.
**Key points**
- [m:ss] point (one line each, 4–8 points, ordered as in the video)
**Worth noting:** claims needing a source, caveats, or concrete numbers/tools/names mentioned (omit if none)
```

Match the length to the video. A 3-minute clip gets a TL;DR and 2–3 bullets. Paraphrase, and quote a line only when the exact words matter. Keep it short. Cut sponsor reads, intros, and "like and subscribe".

## 3. Unslop

Run the `unslop` skill on the breakdown before you show it. If it is already loaded this session, don't load it again.
