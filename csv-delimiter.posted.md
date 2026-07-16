## Linked issue (required)

Refs #3853 — that report had two halves: the mangled `#separator:Comma,,` header line (fixed at the time by trimming trailing delimiters from comment lines), and the underlying auto-detection favouring `:` over `,` whenever both appear (per @dae's analysis there). This PR fixes the second half, which is still reachable today whenever a file has no valid `#separator:` header. Happy to open a dedicated issue instead if preferred.

## Summary / motivation (required)

`delimiter_from_reader` returned the **first** delimiter byte found anywhere in the 8KB sample, in a fixed enum order that tries `:` before `,`. So a normal comma CSV containing a colon in any field (a time like `9:00`, a URL, a `parent::child` tag, `"Note:"`) was detected as colon-delimited and split into the wrong columns, corrupting the import. This is the content-driven half of the misdetection discussed in #3853; the header-line half was already fixed by trimming trailing delimiters from `#`-comment lines.

The fix keeps detection dependency-free: examine the first several non-empty lines and pick the delimiter that splits them most **consistently** (the same positive field count on the most lines), ignoring a delimiter that only appears inside field content. Ties break with a priority order that keeps genuine delimiters ahead of content-prone ones (colon, space), so an ambiguous file is read the way it was most likely written — e.g. a semicolon file with decimal commas (`1,5;2,7`) stays semicolon.

## Steps to reproduce (required, use N/A if not applicable)

1. Save as `test.csv` (no `#separator:` header):
   ```
   time,note
   9:00,wake up
   10:30,run
   ```
2. Import via File → Import.
3. The preview splits rows on `:` instead of `,`.

## How to test (required)

### Checklist (minimum)

- [x] I ran `./ninja check` or an equivalent relevant check locally.
- [x] I added or updated tests when the change is non-trivial or behavior changed.

### Details

- New unit tests in `metadata.rs` cover: comma file with colons in fields (multi-line and single-line), semicolon file with decimal commas, a genuinely colon-delimited file, and the existing detection cases (explicit `#separator:` values, tab pickup from first line, fallback to Space) still pass.
- The full CI workflow (`check` on Linux/macOS/Windows, `format`, `minilints`) was run against this exact commit on my fork: https://github.com/krMaynard/anki-fork/actions/runs/29471099145

## Before / after behavior (optional)

Before: first-occurrence detection mis-splits comma CSVs containing colons (or any delimiter byte appearing earlier in the enum order than the real one). After: consistency-based detection reads them correctly; explicitly-specified delimiters are unaffected.

## Risk / compatibility / migration (optional)

Only the auto-detection fallback changes; `#separator:` headers and delimiters passed explicitly through the import dialog are untouched. Detection remains a heuristic and can still guess wrong on genuinely ambiguous files — the tie-break deliberately prefers comma/semicolon over colon/space, so e.g. a colon-delimited file whose every line also contains exactly one comma now resolves to comma where the old code resolved to colon. That trade-off favors the far more common case (comma/semicolon files with colons in content) at the expense of a rare one, and any file with a consistent delimiter and no equally-consistent impostor is detected correctly.

## UI evidence (required for visual changes; otherwise N/A)

N/A

## Scope

- [x] This PR is focused on one change (no unrelated edits).
