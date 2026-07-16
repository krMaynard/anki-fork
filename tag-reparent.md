## Linked issue (required)

N/A (no existing tracking issue)

## Summary / motivation (required)

The tag reparent helper used `new_parent.starts_with(existing_name)` to detect a drop onto the tag itself or a descendant. Comparing the raw `::`-joined strings rather than component boundaries meant a sibling whose name merely shares a string prefix (e.g. `foo::bar` onto `foo::barbaz`) was misclassified as a descendant and the move became a silent no-op — the same class of bug as the deck-reparent fix.

The fix compares on `::` component boundaries so only the tag itself or a genuine descendant is a no-op.

## Steps to reproduce (required, use N/A if not applicable)

1. Create tags `foo::bar` and `foo::barbaz`.
2. Drag/rename `foo::bar` under `foo::barbaz`.
3. Observe the move is a silent no-op.

## How to test (required)

### Checklist (minimum)

- [ ] I ran `./ninja check` or an equivalent relevant check locally.
- [x] I added or updated tests when the change is non-trivial or behavior changed.

### Details

Adds a regression test. Developed and passed full CI (`check` on Linux/macOS/Windows, `format`, `minilints`) on a combined branch; per-branch CI runs on push. Draft until CI is green.

## Before / after behavior (optional)

Before: reparenting a tag onto a string-prefix sibling is a silent no-op. After: it reparents correctly.

## Risk / compatibility / migration (optional)

Low risk.

## UI evidence (required for visual changes; otherwise N/A)

N/A

## Scope

- [x] This PR is focused on one change (no unrelated edits).
