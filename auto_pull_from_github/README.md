# PullFromGithub

## Purpose

PullFromGithub is a small pair of utilities to make pulling updates across multiple local Git repositories easier on Windows. The repository provides:

- `auto_git_pull.py` — scans a base folder for Git repositories, fetches remotes and pulls only those that are behind.
- `interactive_git_manager.py` — a terminal-based interactive manager to browse folders, inspect repo status, and pull or open repositories individually.

## Quick prerequisites

- Python 3.8 or newer
- Git available on the PATH (run `git --version` to verify)
- This project is written for Windows and uses File Explorer integration; it expects a base folder by default at `OneDrive\Desktop\Public`.

## Usage

Run the automated updater:

```powershell
python auto_git_pull.py
```

Run the interactive manager:

```powershell
python interactive_git_manager.py
```

## What each script does

- `auto_git_pull.py`
- Scans the configured base folder recursively for Git repositories (skips hidden folders).
- Runs `git fetch` for each repo, checks if the local branch is behind its upstream, and runs `git pull` only when needed.
- Prints a concise summary of updated, up-to-date, skipped, and failed repositories. Default timeouts: fetch/pull operations use short timeouts (30s).

- `interactive_git_manager.py`
- Lets you navigate directories from the configured base folder, shows which folders are Git repos, current branch, and whether there are uncommitted changes.
- For Git repos you can: pull from remote, open in File Explorer, or navigate into the folder.

## Configuration

Both scripts default to a base folder constructed from the current user home: `Path.home() / 'OneDrive' / 'Desktop' / 'Public'`.

To change the folder, open the top of the script and edit the `public_folder` / base path in `main()` (replace with any absolute path or environment-aware path you prefer). Example change:

```python
# Replace this in each script's main()
public_folder = Path(r"D:\Some\Other\Folder")
```

## Notes & troubleshooting

- If you see `Public folder not found`, create the `Public` folder at your Desktop or edit the script's base path as described above.
- If a fetch or pull times out, the script reports that repository as failed — try running `git -C <repo> fetch` or `git -C <repo> pull` manually to see more details.
- The interactive manager uses `explorer` to open folders; this is Windows-specific.

## Contributing & next steps

- Improvements to consider: add command-line options for base folder, recursion depth, or parallel fetch/pull; add logging to a file.
- If you'd like, I can: add a `--path` CLI option, create a `requirements.txt` (if we introduce dependencies), or add a simple unit test harness.

## Files of interest

- `auto_git_pull.py` — automated fetch-first bulk updater
- `interactive_git_manager.py` — terminal interactive manager

## License

Use and modify freely. If you want an explicit open-source license, let me know which one and I will add it.
