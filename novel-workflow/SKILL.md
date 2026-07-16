---
name: novel-workflow
description: Orchestrate every stateful long-form fiction continuation request across source ingestion, wiki and style-pack maintenance, arc or chapter planning, structured user approval, drafting, and wiki write-back. Use automatically when the user naturally asks to整理原作、提炼文风、维护小说 Wiki、设计新篇章、规划章节、续写下一章、修改续写、继续小说、检查剧情状态, or otherwise work on an ongoing novel project; determine and enforce the correct next stage before acting.
---

# Novel Workflow

Treat the project state as authoritative. Never bypass a failed `storyctl` gate.

## Locate the workspace

Find `.story/state.yaml` from the current directory or a user-specified project root. Locate the shared CLI at the sibling `storyctl/storyctl` path in this source checkout, or use an explicitly configured path.

Run:

```bash
<storyctl> --root <project> status
<storyctl> --root <project> validate
```

Do not edit `.story/state.yaml` directly.

## Route the next action

1. If `pending_wiki_update` is non-null, use `$novel-wiki` and finish that update before any planning or writing.
2. If the user asks to ingest source material or inspect story state, use `$novel-wiki`.
3. If the user asks to extract, revise or diagnose narrative style, scene craft, title patterns, imagination or tension, use `$novel-style`.
4. If no approved current plan exists, or the user requests a new arc/sequence/chapter outline, use `$novel-planning`.
5. Use `$novel-writing` only after `check-ready-to-write <plan-id>` succeeds.
6. After the user approves a draft, record approval immediately; the workflow must then route to `$novel-wiki` and optionally propose style learning only from explicit human revisions.

## Preserve authority boundaries

- Wiki content describes what has happened.
- Plans describe what may or will happen after user approval.
- Style files describe approved high-level craft patterns, never story facts.
- Drafts are not story truth.
- Only explicit structured user choices approve plans or drafts.
- Treat ambiguous reactions such as “looks fine,” “continue,” or silence as non-approval; ask for an explicit selection or approval.

When a gate blocks, report its exact reason and perform the required earlier stage. Do not improvise around the state machine.

## Run managed mode

Offer managed mode only after the user has explicitly approved both an arc plan and its chapter sequence. Present one authorization summary containing the exact chapter ids, batch limit, delegated permissions and hard stops. Enable it only after explicit user confirmation:

```bash
storyctl managed-enable --arc-id <arc> --sequence-id <sequence> \
  --chapter <id> [--chapter <id> ...] --max-chapters 3
```

While managed mode is active, repeatedly run `storyctl managed-next` and perform only the returned action:

- `plan-chapter`: use `$novel-planning` delegated mode.
- `write-chapter`: use `$novel-writing` delegated mode.
- `quality-check-and-approve`: generate the required quality report and request delegated approval.
- `commit-wiki`: use `$novel-wiki`; never skip this action.
- `pause` or `complete`: stop and report the checkpoint.

Pause immediately with `managed-pause` when a configured hard stop, canon conflict, parent-plan deviation, missing evidence or low-confidence decision appears. Do not reinterpret a hard stop as a minor detail. Resume only after a user decision or a batch-limit continuation request. The user may pause or disable managed mode at any time.
