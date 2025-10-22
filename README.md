# stop-azs

This repository now includes a utility that can deep-search the project tree to locate and
clean up duplicate content.

## Deduplication script

Use `tools/deduplicate.py` to identify duplicate files, remove redundant copies, and optionally
rewrite text files so each unique line appears only once.

### Usage

```bash
# Preview duplicate files and duplicate lines without modifying anything
python tools/deduplicate.py --path . --dedupe-lines --dry-run

# Delete duplicate files and rewrite supported text files with unique lines only
python tools/deduplicate.py --path . --remove-files --dedupe-lines --strip-whitespace --case-insensitive
```

The script ignores the `.git` directory, follows symbolic links only when `--follow-symlinks`
is provided, and supports common configuration and documentation file extensions when cleaning
duplicate lines.
