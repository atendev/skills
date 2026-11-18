---
name: wayfinder
description: Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on your issue tracker, and resolve them one at a time until the way to the destination is clear.
---

You have a loose idea that is too big for one agent session and wrapped in fog: you can't yet see the way from here to the **destination**. Wayfinding means finding that way, not charging at the destination. This skill draws the way as a **shared map** on the repo's issue tracker. Then it works through the map's **decision tickets** one at a time until the route is clear. A decision ticket is a question whose answer is a decision. It is not a slice of a build.

The destination differs for each effort, and naming it is the first step, because it shapes every ticket. It might be a spec to hand off and refine, a decision to lock before planning starts, or a change made in place, like a data-structure migration. The map works for any field: engineering, course content, anything that fits the shape.

## Plan, don't do

By default, Wayfinder is for **planning**. Each ticket settles a decision. The map is done when the way is clear and nothing is left to decide before someone does the work. If you feel pulled to just do the work, you have probably reached the edge of the map and it is time to hand off. An effort can change this in its **Notes** and carry the work itself into the map. Without that, produce decisions, not deliverables.

## Refer by name

Every map and ticket is an issue, so it has a **name**: its title. In everything the human reads (your updates, the map's Decisions so far), use that name. Never use a bare id, number, or slug. A string of `#42, #43, #44` is hard to read, and names are clear at a glance. The id and URL still exist. They sit inside the name's link and never replace it.

## The Map

The map is a single issue on this repo's issue tracker, labelled `wayfinder:map`. It is the main artifact. Its tickets are child issues of the map.

The map is an **index**, not a store. It lists the decisions made and points to the tickets that hold the detail. Each decision lives in one place, its ticket. The map never repeats it. It gives a short gist and a link.

**Where the map, its tickets, blocking, and frontier queries live depends on the tracker.** If the repo has a `.plan/README.md`, that file is the local tracker doc:

- Maps live at `.plan/maps/<slug>/map.md`, with tickets in `tickets/NN-slug.md`.
- Its "Rules" and "Resolving a ticket" sections stand in for "Wayfinding operations".
- Its rules on derived status, frontmatter, and claims replace the issue-based steps in this skill.
- Ticket numbers are per map. A new map starts at 001. A new ticket takes the current map's highest number plus one. Ignore numbers from other or archived maps in the same folder.

Otherwise you should have been given an issue tracker. If not, tell the user to run `/setup-matt-pocock-skills`. Read the tracker doc's "Wayfinding operations" section to see how _this_ repo does these things. If no tracker is provided, use the local-markdown tracker.

### The map body

The map body is the whole map at low detail. Load it once per session. Open tickets are **not** listed in it. They are open child issues, found by query.

```markdown
## Destination

<what reaching the end of this map looks like: the spec, decision, or change this effort is finding its way to. One or two lines; every session orients to it before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this effort>

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [<closed ticket title>](link): <one-line gist of the answer>

## Not yet specified

<!-- see "Fog of war": in-scope fog you can't ticket yet; graduates as the frontier advances -->

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a **child issue** of the map. The tracker's issue id identifies it. Its body is the question, sized to fit one agent session of 100K tokens:

```markdown
## Question

<the decision or investigation this ticket resolves>
```

Each ticket carries a `wayfinder:<type>` label, one of `research`, `prototype`, `grilling`, `task` (see [Ticket Types](#ticket-types)). These `wayfinder:` labels are the only labels a map and its tickets carry. Never add a triage label like `ready-for-agent`, because these tickets are decisions, not implementation work.

A session **claims** a ticket by assigning it to the dev driving the map. Do this **first**, before any work, so other sessions running at the same time skip it. That assignee _is_ the claim. An open ticket with no assignee is unclaimed.

Blocking uses the tracker's **native** dependency feature. This matters because the tracker's own UI then shows the frontier, so the human sees what can be picked up without opening the map. Only if the tracker has no native blocking should you write the blocking into the body. A ticket is **unblocked** when every ticket blocking it is closed. The **frontier** is the set of open, unblocked, unclaimed child tickets. It is the edge of what is known.

The answer is not part of the body. You record it when the ticket is resolved (see [Work through the map](#work-through-the-map)). Link any assets created while resolving a ticket from the issue. Do not paste them in.

## Ticket Types

Every ticket is either **HITL** (human in the loop, worked _with_ a human who speaks for themselves) or **AFK** (away from keyboard, driven by the agent alone). A HITL ticket resolves only through that live exchange. The agent never answers for the human. A grilling agent that answers its own questions has broken this rule.

- **Research** (AFK): Read documentation, third-party APIs, or local resources like knowledge bases to find a fact a decision waits on. A subagent on `sonnet` resolves it by calling the Skill tool with "research". Use it when you need knowledge from outside the current working directory.
- **Prototype** (HITL): Make a cheap, rough, concrete thing to react to (an outline, a rough take, a stub, or UI or logic code), so the discussion has something real to look at. Call the Skill tool with "prototype". Link the prototype as an asset. Use it when the key question is "how should it look" or "how should it behave".
- **Grilling** (HITL): A conversation. This is the default. Always call the Skill tool twice, for "grilling" and "domain-modeling".
- **Task** (HITL or AFK): Manual work that must happen before a _decision_ can be made. There is nothing to decide, prototype, or research, but the discussion is stuck until the work is done. Examples: signing up for a service so you can judge its API, setting up access, or moving data so you can see its shape. This is the one type that _does_ rather than decides. It earns its place by unblocking a decision, not by delivering the destination. The agent does it alone where it can (AFK). Otherwise it gives the human a precise checklist (HITL). It is resolved when the work is done. The answer records what was done and any facts later tickets depend on (where credentials are, new URLs, row counts).

## Fog of war

The map is _deliberately_ incomplete. Don't chart what you can't yet see. Beyond the live tickets lies the **fog of war**. This is your dim view of decisions and investigations that you know are coming but can't pin down yet, because they depend on questions still open. Each time you resolve a ticket, the fog ahead of it clears. Whatever you can now state precisely becomes a new ticket, one at a time, until the way to the destination is clear and no tickets remain.

The map's **Not yet specified** section is where you write down that dim view: the question you suspect is coming, and the area to come back to. It is the unexplored ground _toward_ the destination. Everything here is in scope, just not sharp enough to ticket yet. Write as little or as much as you can see. It also tells collaborators where the effort is headed.

**Fog or ticket?** The test is whether you can state the question precisely now, _not_ whether you can answer it now.

- **Make it a ticket** when the question is already sharp, even if it is blocked and you can't act on it yet.
- **Leave it in Not yet specified** when you can't phrase it that sharply yet. Don't cut the fog into ticket-sized pieces. It is coarser than a ticket. One patch may become several tickets, or none, once you reach it.

**Not yet specified** leaves out what is already decided (Decisions so far), what is already a live ticket, and what is out of scope (see the next section).

## Out of scope

Fog only gathers _toward_ the destination. The destination sets the scope, so work beyond it is **out of scope**. It isn't fog, and it doesn't belong in **Not yet specified**. It goes in its own **Out of scope** section on the map. This holds work you have chosen to rule out of _this_ effort. It lands here because of scope, not because it is vague.

Out-of-scope work never becomes a ticket, because the frontier stops at the destination. It comes back only if the destination moves, and then it is a new effort, not a restart.

Ruling something out of scope is a scoping decision, not a step on the route. Sometimes a ticket you already made turns out to sit past the destination. Maybe it was mis-scoped while charting, or an answer showed it. **Close it**, since a closed ticket is clearly off the frontier. Then add one line to the **Out of scope** section with the gist, why it is out of scope, and a link to the closed ticket. Keep it out of **Decisions so far**, which records the route you actually walked. A scope boundary is not a step on it.

## Invocation

There are two modes. In both, **never resolve more than one ticket per session**. Research tickets are the one exception.

### Chart the map

The user starts with a loose idea.

1. **Name the destination.** Call the Skill tool twice, for "grilling" and "domain-modeling", to pin down what this map is working toward: the spec, decision, or change. The destination sets the scope, so settle it first.
2. **Map the frontier.** Grill again, this time **breadth-first**. Spread across the whole space instead of going deep on one thread. Find the open decisions and the first steps you can take now. **If this turns up no fog** (the way to the destination is already clear and the whole job fits in one session), you don't need a map. Stop and ask the user how they want to proceed.
3. **Create the map** (label `wayfinder:map`). Fill in Destination and Notes. Leave Decisions so far empty. Sketch the fog in **Not yet specified**.
4. **Create the tickets you can specify now** as child issues of the map. Then add the blocking links in a **second pass**, because issues need ids before they can point at each other. Write cross-references in that pass too, using real ids. A placeholder `#<n>` auto-links to an unrelated issue. The links sort the tickets into the frontier and the blocked. Anything you can't yet specify stays in the fog, in the **Not yet specified** section.
5. **Start the research subagents.** For each `research` ticket you just created, start a subagent on `sonnet`. Set `model` explicitly and never inherit it. Give it a fresh context window and have it call the Skill tool with "research", so the tickets resolve in parallel. It writes its findings where the tracker doc keeps the map's assets. For `.plan`, that is a file in the map's `assets/` folder, committed on the shared planning branch, with a pointer from the ticket. It returns a summary of five lines or fewer, not the findings.
6. Stop. Charting is one session's work, and it resolves no tickets by hand.

### Work through the map

The user gives you a map (URL or number). A ticket is **optional**. Without one, you pick the next decision, not the user.

1. Load the **map**. Use the low-detail view, not every ticket body.
2. Choose the ticket. If the user named one, use it. Otherwise take the first frontier ticket in order. **Claim it** by assigning it to yourself before any work.
   - **Timing.** Right after claiming, run `printf 'wfr-%s\n' '<slug>-<ticket number>-<unix seconds>'` once. Then follow the "Timing" section of `~/.claude/skills/wayfinder-runner/SKILL.md`. Run one `printf 'wft %s\n' '<phase>'` mark as each phase starts (`grill`, `research`, `record`). Run its `wf-time.py close` command just before you record the resolution.
3. Resolve it as the type named by its `wayfinder:<type>` label (the `type:` frontmatter in `.plan`). See [Ticket Types](#ticket-types). Read the label, not just the body, because the body never states the type. **Zoom in as needed.** Fetch the full body of any related or closed ticket when you need it. Call the Skill tool for any skills the `## Notes` block names. If in doubt, call the Skill tool twice, for "grilling" and "domain-modeling".
4. Record the resolution. Post the answer as a **resolution comment**, **close** the issue, and **add a pointer** to the map's Decisions so far.
5. Add any new tickets you found (create them, then link them). Turn any fog the answer made specific into tickets, and clear each one from **Not yet specified** so it lives only as its new ticket. If the answer shows that a ticket (this one or another) sits beyond the destination, **rule it out of scope** instead of resolving it on the route. If the decision makes other parts of the map wrong, update or delete those tickets.

The user may run unblocked tickets in parallel, so expect other sessions to edit the tracker at the same time.
