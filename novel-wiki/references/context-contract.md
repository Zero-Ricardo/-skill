# Context Contract

Planning must not read the full Wiki by default.

## Request shape

```json
{
  "wiki_files": [
    "characters/character-a.md",
    "relationships.md",
    "knowledge.md",
    "foreshadowing.md",
    "obligations.json"
  ],
  "style_files": [
    "profile.md",
    "narrative-structure.md"
  ],
  "reason": "Plan the next chapter around character A's concealed departure"
}
```

`current.md` and `index.md` are always included. Requested paths are relative to `wiki/` or `style/`. Style files must be approved in `style/manifest.json`.

## Default budgets

- Arc planning: 18,000 characters.
- Sequence planning: 14,000 characters.
- Chapter planning: 10,000 characters.

These are guardrails, not targets. If selected complete pages exceed the limit, the request must be narrowed or a compact derived page must be maintained. Never truncate a page because the missing tail may contain a critical constraint.

## Content selection

Include only characters who act, decide, are directly affected, carry relevant secrets or define a needed relationship. Include only rules and foreshadowing touched by the planning target. Use source files only for evidence verification after the Wiki identifies a specific claim.
