---
name: novel-planning
description: Design user-approved long-form fiction plans at arc, chapter-sequence, or individual-chapter level using the current story wiki, while presenting genuinely different options and recording structured user decisions before finalizing any outline. Use when opening a new arc, decomposing an arc into chapters, planning the next chapter, or revising an unapproved proposal.
---

# Novel Planning

Plan only from the latest Wiki and approved parent plan. Never treat a proposal as approved.

Read [multiline-and-tension.md](references/multiline-and-tension.md) before arc or sequence planning. Read the approved project style manifest and load only the style files required for the current planning level.

## Start with a gate and context

Run `storyctl check-ready-to-plan`. If blocked, stop and route to `$novel-wiki`.

Read only `wiki/current.md` and `wiki/index.md` first. Identify the characters who will decide or be directly affected, the active relationships, knowledge asymmetries, rules, threads and foreshadowing needed for this planning target. Write a context request following `$novel-wiki`'s context contract, then build the pack with `storyctl build-context --request <file>`. Verify its `wiki_revision` matches current state.

Do not read the full Wiki or all character pages by default. If a required major character lacks a decision model, current arc position or relationship-specific pressure, stop and request a targeted Wiki repair rather than inventing psychology inside the plan.

Query story obligations before planning:

```bash
storyctl due-obligations --chapter-id <id> [--tag <location-or-thread> ...]
```

Include returned `must_include` obligations in the context request. Consider `consider` items explicitly; either touch them or preserve their future review point. Do not force a cameo merely because an obligation exists.

Choose one level:

- `arc`: define purpose, conflict, character arcs, independent narrative lines, convergence points, major turns, ending state and foreshadowing strategy. Read `style/profile.md`, `narrative-structure.md` and `emotional-rhythm.md`.
- `sequence`: divide an approved arc into functional chapters, build a line-progression matrix, and control pacing, revelations, viewpoint distribution and line absence. Also read `style/title-system.md`.
- `chapter`: define concrete scenes, tension movement, visual and emotional design, viewpoint structure, information release, foreshadowing action and ending resonance. Read relevant `scene-patterns.md` entries and generate title candidates.

At every level, derive action from the Wiki character model:

- the character enters with a concrete want;
- resistance presses a fear, contradiction, relationship or misconception;
- the choice follows or meaningfully breaks an established decision pattern;
- any break requires visible pressure and changes the arc position;
- consequences update knowledge, relationships or emotional debt.

Do not use personality adjectives as sufficient motivation.

## Explore before filtering

Do not begin by shrinking the solution space to the safest plot. First produce a private divergent pass of possibilities that remain thematically relevant:

- a contemporary space transformed by an established world rule;
- a visual set piece that also pressures a relationship or belief;
- two apparently separate lines that could collide;
- a reversal that changes the meaning of prior evidence;
- an outcome achieved by character choice rather than a convenient new power.

Then filter candidates against the Wiki, approved parent plan and major-decision gates. Label each surviving option as directly usable, requiring setup, requiring separate user approval, or conflicting with canon. Reject spectacle that has no character or thematic function.

## Present structured options

Create exactly 2 or 3 genuinely different options. For each include:

- core direction;
- character impact;
- foreshadowing impact;
- downstream opportunity and risk;
- narrative-line and tension consequences;
- one defining visual or dramatic possibility.

Give a reasoned recommendation without selecting for the user. Register the proposal with:

```bash
storyctl propose-plan <id> --level <level> --option A --option B
```

Fill the generated proposal fields before presenting them. Ask the user to choose an option, combine options, request redesign, or explicitly approve a named option.

## Require explicit confirmation

Do not infer approval from praise, continued discussion, silence, rejection of another option, or “try it.” When the user modifies a selected option, create a revised option and ask again.

After an explicit structured choice, run:

```bash
storyctl record-decision <id> --selected <option-id>
```

If the Wiki changed while awaiting an answer, discard the stale confirmation and regenerate options.

### Delegated chapter planning

Use this path only when `storyctl managed-next` returns `plan-chapter` and the active delegation covers the chapter. Still generate 2–3 real options and preserve them in the proposal. Score each option against the approved arc outcome, chapter-sequence function, character arcs, tension, style pack, continuity risk and hard stops.

Automatically select the strongest compliant option, record the reasons in the outline, and finalize with:

```bash
storyctl delegated-finalize-plan <chapter-id> \
  --delegation <delegation-id> --selected <option-id> --outline <file>
```

Do not use delegation for arc or sequence plans. Pause managed mode instead of auto-selecting any option that triggers a hard stop, changes the approved parent outcome, needs a new world rule, or has unresolved low confidence.

## Cover obligations in sequences

Alongside every sequence plan, create a JSON coverage file that maps active or due obligation ids to one or more scheduled chapter touches and an action: `mention`, `reinforce`, `activate`, `resolve`, `retire` or `defer`.

Run:

```bash
storyctl check-sequence-coverage --coverage <file>
```

The sequence cannot be finalized while a due obligation is absent, an active obligation lacks a touch or explicit defer action, or a proposed resolution contradicts its forbidden handling. A dormant obligation may remain offstage when its wake condition has not occurred, but must retain a future review point.

## Finalize the outline

Write the selected outline to a temporary Markdown file. Ensure it implements the confirmed option and contains no silent major additions. Finalize with:

```bash
storyctl finalize-plan <id> --outline <file>
```

For major death, betrayal, identity revelation, world-rule change, central mystery solution, major foreshadowing resolution, or deviation from an approved ending, create a separate structured decision before incorporating it.

For sequence and chapter plans, include 2–4 title candidates derived from `style/title-system.md`, explain each title's function, and mark one recommendation. A title is approved with the plan unless the user explicitly defers it. Recheck the title after the prose exists; changing it does not change plot approval.
