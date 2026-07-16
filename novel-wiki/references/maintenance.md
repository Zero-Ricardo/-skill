# Wiki Maintenance

## Distill instead of append

Apply each chapter as a state transition. Replace stale “current” claims, preserve causal history in the timeline, and keep source references. Repeatedly appending chapter bullets produces contradictions and unusable context.

## Relevance test

Keep a fact in an active Wiki page only if at least one is true:

- it constrains a future action or possibility;
- it changes a character decision, relationship or knowledge boundary;
- it is required to understand an active thread, rule or foreshadowing item;
- contradicting it would create a continuity error.

Otherwise leave it in the source or a chapter observation outside the active context path.

## Quality checks

Before commit verify:

- hard facts have sources;
- inference is visibly labeled;
- no page contains two incompatible current states;
- character knowledge matches `knowledge.md`;
- relationship entries are not duplicated;
- completed conflicts have left `current.md`;
- major character pages contain a decision model and current arc position;
- supporting characters are not over-modeled;
- Wiki pages contain no unapproved future plan;
- new pages appear in `index.md`.
- all referenced obligation ids exist and pass `storyctl audit-obligations`;
- every active or dormant obligation has a next review or explicit wake condition;
- resolved obligations identify the chapter that fulfilled the reader promise.

## Repair order

When upgrading an existing Wiki, repair only the active planning closure first:

1. current dashboard;
2. active major characters;
3. active directional relationships;
4. knowledge ledger;
5. active world rules and foreshadowing;
6. index.

Do not rebuild every historical page before planning can continue.
