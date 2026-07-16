---
name: novel-style
description: Analyze user-supplied original novel chapters and approved human revisions to build and maintain an evidence-based project style pack covering narrative architecture, cinematic scenes, emotional rhythm, character voices, imagery and title systems. Use when source chapters have been ingested, when the user asks to extract or refine the work's storytelling characteristics, or when planning and writing lack the source work's energy, imagination or tension.
---

# Novel Style

Build project-local craft knowledge from supplied text. Do not attempt exact imitation of a living author or copy distinctive passages. Extract high-level, reusable characteristics of the work: narrative function, scene construction, pacing, emotional movement, viewpoint design, imagery and naming patterns.

Read [analysis-method.md](references/analysis-method.md) before analyzing a corpus. Read [style-pack-schema.md](references/style-pack-schema.md) before creating or updating files under `style/`.

## Separate observations from rules

Store chapter-level evidence in `style/observations/`. An observation may describe what a chapter does, but it is not yet a project rule.

Promote a pattern into the formal style pack only when:

- it appears across multiple relevant chapters, or is clearly tied to one repeatable scene type;
- its narrative function can be explained;
- its appropriate and inappropriate uses are stated;
- the user approves the proposed rule.

Never treat AI-generated continuation prose as evidence of source style. Human revisions may become preference evidence only after explicit approval.

## Analyze in passes

1. Inventory chapter titles, viewpoint, scene type and structural role across the corpus.
2. Select representative samples by scene type rather than only famous or dramatic chapters.
3. Record chapter observations for narrative structure, visual staging, sound, movement, emotional turns, dialogue subtext, imagery and title function.
4. Compare observations and propose rules with source chapter references, confidence, use cases and failure modes.
5. Present proposed changes to the user. Do not silently overwrite approved style rules.
6. After explicit structured approval, run `storyctl approve-style --proposal <path> --file <style-file>` with one `--file` per approved file. This records the decision and increments the manifest revision.

## Maintain the style pack

Keep these files focused:

- `profile.md`: concise entry point and strongest cross-cutting principles.
- `narrative-structure.md`: viewpoint, parallel lines, information asymmetry, convergence and reveal patterns.
- `cinematic-scenes.md`: space, light, sound, movement, visual focus, transitions and set pieces.
- `emotional-rhythm.md`: humor, warmth, dread, reversal, restraint and aftermath.
- `character-voices.md`: speech strategy, defenses, relationship-dependent voice and subtext.
- `imagery.md`: recurring motifs, established meaning, overuse risks and allowed development.
- `title-system.md`: book, arc and chapter naming patterns plus title selection workflow.
- `scene-patterns.md`: craft recipes by scene function, not prose templates.

Keep direct quotations short and necessary. Prefer chapter references and paraphrased evidence.

## Feed other skills

- Planning reads `profile`, `narrative-structure`, `emotional-rhythm`, `title-system` and relevant scene patterns.
- Writing reads `profile`, `cinematic-scenes`, `emotional-rhythm`, `character-voices`, `imagery` and relevant scene patterns.
- Wiki never imports subjective style claims.

When a required style file is missing or unapproved, report the gap. Do not invent a style rule inside a plan or draft and then treat it as established.
