---
name: novel-wiki
description: Build and maintain a source-traceable novel wiki from original chapters and user-approved continuation chapters, update current character and story state, track timelines, rules, relationships and foreshadowing, and generate minimal context packs for planning. Use when ingesting chapters, committing approved prose, repairing stale story state, or preparing planning context.
---

# Novel Wiki

Maintain facts without inventing missing answers. Read the project files directly; use the shared `storyctl` CLI for every state transition.

## Classify every claim

Keep these origins distinct:

- `canon`: stated or unambiguously shown in supplied original text.
- `continuation`: established by user-approved continuation prose.
- `inference`: plausible interpretation that is not story truth.

Attach a source chapter and location to hard facts. Put unresolved ambiguity in `wiki/questions.md`. Never promote an inference or proposed plan into the Wiki.

## Ingest original material

1. Register one source with `storyctl ingest-canon <file>`.
2. Read it and prepare a Wiki change manifest containing `updated_files`.
3. Update only affected pages: `current.md`, characters, timeline, world, relationships, foreshadowing, and questions.
4. Run `storyctl propose-wiki-update <canon-id> --patch <manifest>` and show a concise update report.
5. Run `storyctl commit-wiki <canon-id>` only after all declared Wiki files contain the extracted changes.
6. Run `storyctl validate`.

For bulk ingestion, repeat per chapter so sources and changes remain traceable. Stop for genuine version conflicts or identity-changing ambiguity.

After Wiki ingestion succeeds, report which source chapters are newly available to `$novel-style`. Do not extract style rules inside the Wiki workflow and do not block Wiki freshness on optional style analysis.

## Commit approved continuation

Accept only the chapter shown in `pending_wiki_update`. Read the approved draft and update state changes rather than writing a literary summary:

- events and causal consequences;
- character location, physical/emotional state, goals, knowledge and misconceptions;
- relationship changes and information asymmetry;
- world-rule additions or demonstrated exceptions;
- foreshadowing seeded, reinforced, activated or resolved;
- `current.md` and the canon cutoff.

Prepare the manifest, run `propose-wiki-update`, then `commit-wiki`. A successful commit copies the approved prose into `sources/continuation` and writes a receipt. Never copy drafts there manually.

In managed mode, Wiki maintenance remains mandatory and automatic after each delegated chapter approval. Preserve the delegation id in the pending update and receipt. If extraction finds a canon conflict, identity ambiguity, rule change or major foreshadowing resolution not authorized by the parent plan, pause managed mode before committing rather than normalizing the conflict.

## Build planning context

Run `storyctl build-context --for <arc|sequence|chapter> --target <id>`, then enrich the generated file with only relevant Wiki evidence:

- current conflict and prior ending state;
- involved characters, motivations and knowledge boundaries;
- applicable world rules;
- active foreshadowing and unresolved questions;
- facts the plan must not violate;
- links to Wiki pages or sources.

Do not paste the entire Wiki into a chapter context pack.
