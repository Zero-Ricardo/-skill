---
name: novel-writing
description: Draft a long-form fiction chapter from an approved chapter outline and current Wiki-derived writing context while preserving character motivation, knowledge boundaries, continuity, world rules and unresolved foreshadowing. Use when a specific chapter plan has been explicitly approved and the user asks to write or revise its prose.
---

# Novel Writing

Render an approved plan into scenes. Do not perform hidden replanning.

Read [cinematic-and-multiline.md](references/cinematic-and-multiline.md) before drafting. The continuity constraints are the floor, not the artistic target.

## Verify permission to write

Run `storyctl check-ready-to-write <plan-id>`. Stop on failure. Read only:

- the approved chapter outline;
- its Wiki-derived context pack;
- directly relevant character, rule and foreshadowing pages;
- the prior chapter ending when needed;
- the approved style manifest plus relevant cinematic, emotional, voice, imagery and scene-pattern files.

Do not target exact imitation of a living author. Use approved high-level qualities such as genre, narrative distance, pacing, emotional register and humor.

## Draft the chapter

- Convert outline beats into causal scenes rather than expanding bullets mechanically.
- Express character through choices, action, dialogue and selective interiority; do not recite character cards.
- Preserve who knows what, current injuries, locations, possessions and relationship temperature.
- Do not reveal or resolve foreshadowing beyond the approved outline.
- Do not add a major rule, identity, death, betrayal or plot turn. Return to `$novel-planning` if one becomes necessary.
- Preserve approved key outcomes while freely inventing scene paths, minor obstacles, physical business, misunderstandings, humor, visual motifs and dialogue subtext that do not change those outcomes.
- Give every scene a visible spatial logic, a changing sensory focus and a character pressure. Spectacle must alter a choice, relationship or understanding.
- Follow the approved emotional movement; use contrast between ordinary life, humor, wonder, dread and aftermath rather than sustaining one ornate register.
- When the plan uses multiple lines, make each transition change information, tension or meaning. Preserve viewpoint knowledge boundaries and use visual, sonic, thematic or causal bridges instead of mechanical labels.
- Use the project title system to verify that the approved title gains meaning from the finished chapter. Propose a title revision separately when it does not.

## Perform a light self-check

Before presenting the draft, check:

- every required outline event is present;
- no major unapproved event or setting fact was added;
- characters use only information they possess;
- ending state matches what the prose actually establishes;
- scenes can be spatially visualized and their focal image changes with the emotion;
- humor, imagery and lyrical emphasis arise from character and scene function rather than decorative imitation;
- every viewpoint or narrative-line switch has a specific effect;
- the chapter contains pressure, change and aftermath rather than only correct events.

List significant new-fact candidates separately; they are not Wiki updates.

Save the draft and run:

```bash
storyctl register-draft <chapter-id> --plan-id <plan-id> --file <draft>
```

Ask for explicit user approval or revisions. After explicit approval run `storyctl approve-draft <chapter-id>`. Stop writing: the state is now `wiki-update-required`, and `$novel-wiki` must commit the chapter before further planning.

## Use delegated drafting

Use this path only when the active managed delegation covers the chapter. Draft and run the same checks as interactive mode. If a check fails, revise automatically at most twice. Write a machine-readable quality report with:

```json
{
  "continuity": "pass",
  "character": "pass",
  "information_boundary": "pass",
  "world_rules": "pass",
  "foreshadowing": "pass",
  "outline_coverage": "pass",
  "style": "pass",
  "major_change_detected": false,
  "revision_count": 1
}
```

Approve through the delegation only when every hard field passes:

```bash
storyctl delegated-approve-draft <chapter-id> \
  --delegation <delegation-id> --quality-report <file>
```

Pause managed mode if two revisions do not pass, a major change is detected, or literary quality cannot be honestly marked pass. After delegated approval, stop drafting and allow the mandatory Wiki update to run.
