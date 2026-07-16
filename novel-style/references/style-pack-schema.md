# Style Pack Schema

Each formal rule should use this compact structure:

```markdown
## Rule ID — Name

- Status: approved | proposed | retired
- Confidence: high | medium | exploratory
- Applies to: scene or planning contexts
- Principle: the reusable high-level rule
- Function: the reader or story effect it creates
- Evidence: source chapter references
- Avoid: misuse and overuse
```

`style/manifest.json` contains:

```json
{
  "schema_version": 1,
  "revision": 1,
  "source_scope": [],
  "approved_files": [],
  "pending_proposals": [],
  "updated_at": null
}
```

Keep observations under `style/observations/` and pending cross-corpus proposals under `style/proposals/`. Planning and Writing may use only approved formal files listed in the manifest.
