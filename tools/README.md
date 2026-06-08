# Toolkit Python Utilities

This folder contains helper scripts for extracting and merging Git command data from HTML source, backups, and VS Code session snapshots.

## Why keep these tools

- They are useful for regenerating the JSON data when the page content changes.
- They let you recover lost command entries from snapshots or legacy HTML backups.
- They are not required for the live site, but they are safe to keep in `tools/` as maintenance utilities.

## Available scripts

### `build_git_json.py`

- Extracts `git-termux.html` command cards and builds `assets/data/commands-git.json`.
- Rewrites `git-termux.html` to keep only the placeholder `<main id="mainContent">` block.
- Best used when the source page still contains hardcoded command cards you want to migrate.

### `extract_git_commands.py`

- Extracts command cards from `git-termux.html` into `assets/data/commands-git.json`.
- Produces a simpler `Quick Reference` JSON structure.
- Good as a lightweight extraction fallback.

### `merge_git_from_file.py`

- Merges additional command cards from `termux-ops-old.html` into `assets/data/commands-git.json`.
- Useful when you have extra commands in backup HTML that are not yet in the JSON.

### `merge_git_from_snapshots.py`

- Merges commands parsed from VS Code snapshot `content.txt` files into `assets/data/commands-git.json`.
- Great when the original page content is missing or partially lost.

### `recover_from_snapshots.py`

- Parses snapshot files and rebuilds/updates `assets/data/commands-git.json`.
- Creates a `.bak` backup of the existing JSON before writing.
- Recommended for recovery workflows.

## Recommended usage

Use the wrapper script below when you want a single entry point.

```bash
python tools/git_data_tools.py build
python tools/git_data_tools.py merge-file
python tools/git_data_tools.py merge-snapshots
python tools/git_data_tools.py recover-snapshots
```

## Notes

- These scripts are maintenance helpers, not part of the deployed web app.
- Keep them while you continue iterating on the data-driven toolkit.
- Remove them later only if you want a smaller repo and no longer need regeneration/recovery.
