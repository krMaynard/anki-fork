## Linked issue (required)

N/A (no existing tracking issue)

## Summary / motivation (required)

The `Preset` and `prop:cds` (custom-data string) parser arms stored their value verbatim, without unescaping `\"` the way the `Regex` node and the writer's `maybe_quote` already assume. So a value containing a double quote did not survive parse → write → parse: the writer re-escaped the already-present backslash-quote into `\\"`, which then failed to re-parse.

The fix unescapes `\"` when parsing these two nodes (matching the `Regex` arm), so the stored value is the literal text and the writer's escaping round-trips.

## Steps to reproduce (required, use N/A if not applicable)

1. Use a search containing a preset or `prop:cds` value with an escaped quote, e.g. `preset:a\"b` or `prop:cds:k=a\"b`.
2. Normalize/round-trip the search (parse → write → parse).
3. Observe the value no longer re-parses correctly (the escape compounds to `\\"`).

## How to test (required)

### Checklist (minimum)

- [ ] I ran `./ninja check` or an equivalent relevant check locally.
- [x] I added or updated tests when the change is non-trivial or behavior changed.

### Details

Adds a normalization round-trip regression test in `writer.rs`. Developed and passed full CI (`check` on Linux/macOS/Windows, `format`, `minilints`) on a combined branch; per-branch CI runs on push. Draft until CI is green.

## Before / after behavior (optional)

Before: a quote in a preset/custom-data search value does not survive round-tripping. After: it round-trips correctly.

## Risk / compatibility / migration (optional)

Low risk; matches existing `Regex`-arm behavior.

## UI evidence (required for visual changes; otherwise N/A)

N/A

## Scope

- [x] This PR is focused on one change (no unrelated edits).
