## Linked issue (required)

Fixes #5186

## Summary / motivation (required)

`parse_image_cloze` parsed properties with a nom `escaped`/`separated_pair` loop that broke on the first parse failure, silently discarding the failing property **and every property after it**. Two reachable inputs triggered this:

- an empty value (e.g. an empty text label, `text=`), and
- a value containing a backslash not followed by `:` (e.g. LaTeX like `\frac`).

In both cases the remaining occlusion properties (scale, font size, position, …) were lost.

The fix parses by splitting the shape off the first colon, then splitting the rest on unescaped colons and each property on its first `=`, so every property is read independently and empty/backslash values are preserved.

## Steps to reproduce (required, use N/A if not applicable)

1. Create an image-occlusion note whose occlusion data contains a property with an empty value (e.g. an empty text label) or a backslash value (e.g. LaTeX).
2. Round-trip / re-parse the occlusion.
3. Observe properties after the offending one (scale, font size, position) are dropped.

## How to test (required)

### Checklist (minimum)

- [x] I ran `./ninja check` or an equivalent relevant check locally.
- [x] I added or updated tests when the change is non-trivial or behavior changed.

### Details

Adds a unit test covering empty-value and backslash-value inputs preserving subsequent properties. The full CI workflow (`check` on Linux/macOS/Windows, `format`, `minilints`) was run against this exact commit on my fork: https://github.com/krMaynard/anki-fork/actions/runs/29983177217

## Before / after behavior (optional)

Before: an empty or backslash property value drops that property and all following ones. After: all properties are preserved.

## Risk / compatibility / migration (optional)

Low–moderate: rewrites the occlusion property parser. Covered by unit tests; parsing output is unchanged for well-formed inputs.

## UI evidence (required for visual changes; otherwise N/A)

N/A

## Scope

- [x] This PR is focused on one change (no unrelated edits).
