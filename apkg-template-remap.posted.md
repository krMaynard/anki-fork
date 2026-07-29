## Linked issue (required)

Fixes #5209

## Summary / motivation (required)

`import_cards` remapped a card's template index (`ord`) inside `add_card`, which runs **after** `map_to_imported_note` has already overwritten `card.note_id` with the target note id. But `notetype_map` — and therefore `remapped_templates` — is keyed by the **source** note id, so the lookup missed and the template index was left unchanged whenever a note's id changed on import (id-collision uniquify, or a guid match to a differently-id'd note).

Consequences: cards could point at the wrong template after import, and `card_ordinal_already_exists` deduplicated on the un-remapped ordinal.

The fix computes the remapped index in `import_cards` using the **source** note id, before `map_to_imported_note` runs, via a small pure helper.

## Steps to reproduce (required, use N/A if not applicable)

1. Have a collection whose notetype template ordinals were reordered relative to a source deck.
2. Export a deck to `.apkg` where an imported note's id collides with an existing note (forcing uniquify) or matches by guid to a differently-id'd note.
3. Import the `.apkg` into the target collection.
4. Observe that affected cards render with the wrong template (their ordinal was not remapped).

## How to test (required)

### Checklist (minimum)

- [x] I ran `./ninja check` or an equivalent relevant check locally (via the fork CI run linked below).
- [x] I added or updated tests when the change is non-trivial or behavior changed.

### Details

Adds a unit test for the remap lookup exercising the source-note-id keying. Full CI (`check` on Linux/macOS/Windows, `format`, `minilints`) was run against this exact commit on the fork: https://github.com/krMaynard/anki-fork/actions/runs/30167008557 — build, lint, and test pass on all three OSes. (The run shows red only for the `Upload SARIF results for complexipy` step, which always fails on forks due to a token-permission limitation, not a code failure.)

## Before / after behavior (optional)

Before: template ordinals silently left un-remapped when a note's id changed on import. After: ordinals remapped using the source note id.

## Risk / compatibility / migration (optional)

Low risk; import-path-only change, no schema or scheduling impact.

## UI evidence (required for visual changes; otherwise N/A)

N/A

## Scope

- [x] This PR is focused on one change (no unrelated edits).
