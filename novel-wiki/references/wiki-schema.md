# Planning-oriented Wiki Schema

## Index

`wiki/index.md` is the routing layer. Give every page a one-line description plus tags for active characters, locations, threads, secrets and planning level. Do not repeat page contents.

## Current dashboard

Keep `wiki/current.md` short and overwrite stale state. Recommended sections:

```markdown
# Current Story State
## Cutoff and active time/place
## Active characters: immediate goal and action
## Active conflicts and countdowns
## Critical information asymmetry
## Unfinished promises and emotional debts
## Immediate hard constraints
```

## Major character

Use this schema for viewpoint characters and continuing decision-makers:

```markdown
# Character
## Core in one sentence
## Stable engine
- deep want
- fear/shame/loss
- value priority
- central contradiction
- self-misconception
## Decision model
- normal strategy
- relationship pressure
- crisis threshold
- aftermath pattern
## Behavior boundaries
## Current state
- location/body/emotion
- immediate goal/action
- known/unknown/mistaken/concealed
## Current arc position
- starting belief
- pressure already applied
- threshold not yet crossed
## Key relationships
- want from the other person
- outward strategy
- concealed need/information
- present tension and boundary
## Scene triggers
## Unfinished promises and emotional debts
## Evidence
```

Avoid generic adjective lists, full biographies, repeated event summaries, speculative future plots and prose-style instructions.

## Supporting character

Keep only: role, current allegiance/goal, relevant capability, knowledge boundary, active relationship or secret, current status, obligation ids, wake conditions and evidence. Omit childhood, personality essays and inactive history unless it changes a present decision.

## Story obligations

`wiki/obligations.json` is the machine-readable source of truth for unresolved supporting-character threads, reader promises, emotional debts and planted background that requires review. Use this shape:

```json
{
  "schema_version": 1,
  "obligations": [
    {
      "id": "O-001",
      "title": "Short description",
      "type": "subplot",
      "status": "active",
      "carrier_pages": ["characters/supporting-character.md"],
      "related_characters": ["main-character"],
      "reader_expectation": "What the text has led readers to expect",
      "open_questions": ["What remains unresolved"],
      "last_touched": "chapter-id",
      "next_review": "chapter-or-sequence-id",
      "wake_on": ["location-tag", "relationship-tag", "event-tag"],
      "allowed": ["reinforce without revealing identity"],
      "forbidden": ["resolve without major-decision approval"],
      "sources": ["source chapter"],
      "resolution_chapter": null
    }
  ]
}
```

Statuses are `dormant`, `active`, `due`, `resolved`, `retired` and `blocked`. Dormant means intentionally sleeping and still requires a wake condition and next review. Resolved requires a resolution chapter; retired requires an explicit user decision reference.

## Relationship

Model direction when it matters. A→B and B→A may have different wants, beliefs and concealments. Record current temperature, power asymmetry, shared history only as needed, active fracture, next pressure point and latest change source. Consolidate duplicates.

## Knowledge ledger

`wiki/knowledge.md` tracks only plot-critical information asymmetry:

```markdown
| Fact/secret | Knows | Suspects | Mistaken belief | Conceals from | Source |
```

Do not list ordinary shared facts.

## Timeline

Record only causal events that constrain later action. Include event id, time/order, participants, cause, consequence, knowledge distribution and source. Do not duplicate chapter summaries.

## World rules

Separate confirmed behavior, limit, cost, known exception, unresolved inference and source. A demonstrated exception does not automatically rewrite the general rule.

## Foreshadowing

Track id, evidence, current confirmed meaning, open interpretations, related characters, state and questions a valid resolution must answer. Never promote a proposed resolution into fact.
