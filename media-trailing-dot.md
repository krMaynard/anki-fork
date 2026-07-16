## Linked issue (required)

N/A (no existing tracking issue)

## Summary / motivation (required)

`add_hash_suffix_to_file_stem` unconditionally formatted `"{stem}-{hash}.{ext}"`. For an extensionless filename the extension is empty, producing a name that ends in `.` (e.g. `foo-<hash>.`), which is invalid on Windows — even though every other filename path in this module applies a `WINDOWS_TRAILING_CHAR` fix-up. The hashed name is written straight to disk on a media collision and used as the apkg import target, so the invalid name reaches the filesystem.

The fix omits the `.` separator when there is no extension.

## Steps to reproduce (required, use N/A if not applicable)

1. On Windows, import media containing an extensionless filename that collides with an existing file (triggering the hash-suffix path).
2. Observe a filename ending in `.` is produced, which is invalid on Windows.

## How to test (required)

### Checklist (minimum)

- [ ] I ran `./ninja check` or an equivalent relevant check locally.
- [x] I added or updated tests when the change is non-trivial or behavior changed.

### Details

Adds a unit test for the extensionless case. Developed and passed full CI (`check` on Linux/macOS/Windows, `format`, `minilints`) on a combined branch; per-branch CI runs on push. Draft until CI is green.

## Before / after behavior (optional)

Before: extensionless hashed media names end in `.` (invalid on Windows). After: no trailing dot.

## Risk / compatibility / migration (optional)

Low risk.

## UI evidence (required for visual changes; otherwise N/A)

N/A

## Scope

- [x] This PR is focused on one change (no unrelated edits).
