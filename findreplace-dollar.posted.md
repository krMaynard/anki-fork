## Linked issue (required)

Fixes #5215

## Summary / motivation (required)

For a non-regex Find & Replace, the search term is escaped via `regex::escape` but the replacement was passed through unchanged. The regex engine interprets `$` in a replacement as a capture-group reference (e.g. `$1`, `$name`, `${n}`), so a literal replacement such as `$5` expanded to the (empty) capture group 5, silently dropping the text instead of inserting `$5`.

The fix escapes `$` to `$$` for non-regex replacements so it is inserted verbatim.

## Steps to reproduce (required, use N/A if not applicable)

1. Select notes and open Find & Replace with "Treat input as regular expression" **off**.
2. Replace some text with a literal replacement containing `$`, e.g. `$5`.
3. Observe the `$5` is dropped/mangled instead of inserted literally.

## How to test (required)

### Checklist (minimum)

- [x] I ran `./ninja check` or an equivalent relevant check locally.
- [x] I added or updated tests when the change is non-trivial or behavior changed.

### Details

Adds a regression test for literal `$` in non-regex replacements. Full CI (`check` on Linux/macOS/Windows, `format`, `minilints`) run against this exact commit on my fork: https://github.com/krMaynard/anki-fork/actions/runs/30287938613 — all green except the "Upload SARIF results for complexipy" step on the Linux job, which fails on every fork run with "Resource not accessible by integration" (a permissions limitation of running CodeQL uploads outside the upstream repo, unrelated to this change); the "Build, lint, and test" step passed on all three `check` jobs.

## Before / after behavior (optional)

Before: `$5` (non-regex) expands to an empty capture group. After: `$5` is inserted literally.

## Risk / compatibility / migration (optional)

Low risk; only affects non-regex replacement escaping.

## UI evidence (required for visual changes; otherwise N/A)

N/A

## Scope

- [x] This PR is focused on one change (no unrelated edits).
