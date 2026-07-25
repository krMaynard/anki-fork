## Linked issue (required)

Fixes #5207

## Summary / motivation (required)

The browser's **average-interval** column computed `intervals.iter().sum::<u32>() * 86400` in `u32`. Intervals are in days, so a single card with an interval beyond ~49,710 days (reachable via a large maximum-interval setting, "set due date", or add-ons) overflowed `u32` — panicking in debug builds and rendering a wildly wrong span in release.

The **average-ease** column had the same shape: `eases.iter().sum::<u16>()` overflows `u16` once ~27 cards are averaged in notes mode.

The fix extracts the two averages into small helpers that accumulate in a wider type (`u64` for intervals, `u32` for eases).

## Steps to reproduce (required, use N/A if not applicable)

1. Set a card's interval to a very large value (e.g. via "Set Due Date" with a large offset, or a high maximum interval).
2. Select it in the Browser with the Average Interval column shown.
3. In a debug build this panics; in release the displayed span is wildly wrong.
4. For ease: select ~30+ cards in notes mode with the Average Ease column shown.

## How to test (required)

### Checklist (minimum)

- [x] I ran `./ninja check` or an equivalent relevant check locally.
- [x] I added or updated tests when the change is non-trivial or behavior changed.

### Details

Adds unit tests covering the overflow-triggering inputs for both helpers. The full CI workflow ran against this exact commit: https://github.com/krMaynard/anki-fork/actions/runs/30141307409

`Build, lint, and test` passed on Linux, macOS, and Windows, and `format` and `minilints` passed. The workflow's only failure was the Linux SARIF upload step (`Resource not accessible by integration`), after the substantive Linux checks had passed.

## Before / after behavior (optional)

Before: overflow panic (debug) / garbage value (release) for large intervals or many-card ease averages. After: correct averages via wider accumulation.

## Risk / compatibility / migration (optional)

Low risk; display-only computation in the browser table.

## UI evidence (required for visual changes; otherwise N/A)

N/A (no visual layout change; corrects an incorrectly-computed cell value)

## Scope

- [x] This PR is focused on one change (no unrelated edits).
