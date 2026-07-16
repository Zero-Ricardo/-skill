---
name: novel-wiki
description: Build and maintain a compact, source-traceable, planning-oriented novel wiki from original chapters and approved continuation chapters. Use when ingesting story material, updating current character or relationship state, repairing stale or bloated wiki pages, tracking knowledge and foreshadowing, or assembling the minimum context required for arc, sequence, or chapter planning.
---

# Novel Wiki

Maintain the smallest body of knowledge that lets Planning make correct, character-driven decisions. Do not turn the Wiki into a prose encyclopedia or copy the source into summaries.

Read these references before acting:

- [wiki-schema.md](references/wiki-schema.md) for required page structures and content boundaries.
- [maintenance.md](references/maintenance.md) when ingesting or repairing pages.
- [context-contract.md](references/context-contract.md) when serving Planning or Writing.

Use the shared `storyctl` CLI for state transitions. Never edit `.story/state.yaml` directly.

## Separate knowledge classes

Label claims as:

- `canon`: explicitly stated or unambiguously demonstrated in supplied original text.
- `continuation`: established by user-approved continuation prose.
- `inference`: a supported interpretation, never a hard constraint.
- `proposal`: belongs in Plans, not the Wiki.

Attach source chapter references to hard facts. Put unresolved conflicts and identity-level ambiguity in `wiki/questions.md`. Do not resolve gaps for neatness.

## Ingest a chapter

1. Register the source with `storyctl ingest-canon <file>` when it is original material. For continuation, accept only the approved pending chapter.
2. Extract a compact change set before editing pages:
   - causal events that change future possibilities;
   - character state, goal, knowledge, misconception or emotional-debt changes;
   - relationship-state or information-asymmetry changes;
   - demonstrated world rules or exceptions;
   - foreshadowing state changes;
   - story-obligation state changes for supporting characters, promises, background threads and reader expectations;
   - new unresolved questions.
3. Update existing claims in place. Do not append a new bullet when an older “current” claim has become stale.
4. Keep historical detail in the timeline or source; keep only active writing constraints in character and current-state pages.
5. Update `wiki/index.md` when a page is added or its planning relevance changes.
6. Prepare a manifest with `updated_files`, run `propose-wiki-update`, then commit only after every declared file contains the change.
7. Run `storyctl validate` and report conflicts, inferences and missing evidence separately.

In managed mode, Wiki maintenance remains mandatory after every delegated chapter. Pause before commit if extraction discovers a hard stop or an unauthorized major change.

## Model characters for decisions

Use the major-character schema from `wiki-schema.md`. A useful character page must explain more than biography:

- what the character wants now and at depth;
- fear, shame or loss they defend against;
- central contradiction and self-misconception;
- normal decision pattern and crisis threshold;
- behavior that requires substantial setup;
- current action, knowledge, concealment and emotional debt;
- current arc position and the pressure needed to move it;
- relationship-specific wants and defenses;
- high-value scene conditions that expose the character.

Keep voice technique in the Style Pack. Keep character psychology, decisions and relationship-dependent behavior in the Wiki.

Use a compact schema for supporting characters. Promote one to the major schema only when they carry a continuing line, key relationship, active secret or consequential choice.

## Preserve supporting-character obligations

Do not keep important background, subplot or reader promises only inside a supporting-character page. Register every item that must later be touched, reinforced, resolved or deliberately retired in `wiki/obligations.json`.

Distinguish:

- background: available material with no promise to use it;
- active subplot: an ongoing pursuit or relationship change;
- story obligation: a planted promise, unresolved causal thread, emotional debt or repeatedly signaled background that must be reviewed.

Each obligation needs a stable id, carrier pages, status, last touch, next review, wake conditions, allowed handling, forbidden premature resolution and sources. Supporting-character pages link obligation ids rather than duplicating their full history.

After Wiki updates run `storyctl audit-obligations`. At arc or sequence planning, expose all `active`, `due` and relevant `dormant` obligations. At chapter planning, use `storyctl due-obligations` with the chapter id and scene tags; never load every supporting character merely to avoid forgetting them.

## Maintain current state

Treat `wiki/current.md` as a dashboard, not history. It should contain only:

- cutoff and active time/place;
- active characters, immediate goals and actions;
- active conflicts and countdowns;
- current public facts and critical private information;
- unresolved promises or emotional debts affecting the next planning unit;
- hard constraints for the immediate future.

Move completed history to `timeline.md`. Avoid repeating facts already discoverable through the index.

## Serve context, not the entire Wiki

Planning first reads only `current.md` and `index.md`, then submits a context request naming relevant Wiki and approved Style files. Build the pack with:

```bash
storyctl build-context --for <arc|sequence|chapter> --target <id> \
  --request <context-request.json>
```

The script rejects unapproved Style files, paths outside Wiki/Style, and oversized packs. If the pack is too large, narrow it; never truncate a fact page silently. Do not paste all characters, all history or all source chapters into a chapter pack.

After Wiki ingestion, report newly available chapters to `$novel-style`; do not mix style analysis into factual maintenance.
