## Linked issue (required)

N/A (no existing tracking issue)

## Summary / motivation (required)

`reparented_name()` used `target.0.starts_with(&self.0)` to detect a drop onto the dragged deck or one of its descendants. Because this compared the raw `\x1f`-joined names rather than component boundaries, a sibling whose name merely shares a string prefix (e.g. dragging `foo::bar` onto `foo::barbaz`) was misclassified as a descendant and the drop became a silent no-op.

The fix compares on `\x1f` component boundaries so only the deck itself or a genuine descendant is treated as a no-op.

## Steps to reproduce (required, use N/A if not applicable)

1. Create decks `foo::bar` and `foo::barbaz`.
2. In the deck list, drag `foo::bar` onto `foo::barbaz`.
3. Observe nothing happens (silent no-op) instead of `bar` becoming `foo::barbaz::bar`.

## How to test (required)

### Checklist (minimum)

- [ ] I ran `./ninja check` or an equivalent relevant check locally.
- [x] I added or updated tests when the change is non-trivial or behavior changed.

### Details

Adds a regression assertion to the `drag_drop` test. Developed and passed full CI (`check` on Linux/macOS/Windows, `format`, `minilints`) on a combined branch; per-branch CI runs on push. Draft until CI is green.

## Before / after behavior (optional)

Before: reparenting onto a string-prefix sibling is a silent no-op. After: it reparents correctly.

## Risk / compatibility / migration (optional)

Low risk.

## UI evidence (required for visual changes; otherwise N/A)

N/A

## Scope

- [x] This PR is focused on one change (no unrelated edits).
