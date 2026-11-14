# CLAUDE.md

Instructions for Claude when working in this repository.

## What this is

Dag-Morten's Mac setup. `install.sh` builds a freshly erased Mac from it, and the files in `configs/` remain the source of truth afterwards: most dotfiles in the home folder are symlinks into this repository. `README.md` explains everything for humans; `configs/README.md` maps each file to its place on the Mac. Read both before changing anything.

The repository lives in `~/Developer/mac-setup`. Some synced VS Code settings depend on that path.

## Layout

- `install.sh`: groups `terminal`, `dev`, `apps`, `repos`, `macos`; options `--dry-run` and `--skip-casks`. Bash 3.2 compatible (macOS's bash): no associative arrays, no `mapfile`, no `${var,,}`, no `&>>`.
- `configs/brew/*.Brewfile`: one Brewfile per group.
- `configs/python/`: the standard Python environment (uv project, built in `~/.venvs/standard`).
- `configs/iterm2/com.googlecode.iterm2.plist`: iTerm2 settings snapshot, written by `scripts/iterm-export.sh`.
- `configs/macos/defaults.sh`: macOS settings.
- `configs/vscode/`: the home-made extensions (tex-oppstart, tex-preambel, workspace-switcher, classroom-mode), plus a copy of the settings of the two profiles (Default in `default/`, Writing in `writing/`) and the shared keybindings. VS Code and Settings Sync own the settings; `setup.sh save` copies them here, `setup.sh restore` puts them back, and `setup.sh check` reports any disagreement. Editing the copy here changes nothing on the Mac: to change a setting, have him run `setup.sh save` first, edit the copy, and give him `setup.sh restore default` or `setup.sh restore writing`. After changing an extension, rebuild its `.vsix` (same version number, 1.0.0) and have him run `setup.sh restore --extensions`; `setup.sh check` shows whether the installed copy is current. A setting name that VS Code does not know cannot be written through the extension API, so check names against VS Code before adding them to classroom-mode.
- `configs/claude/`: the originals of `~/.claude/CLAUDE.md` for Claude Code (`claude-code/`) and `~/Developer/CLAUDE.md` (`developer/`). The files in place are relative links to these. Other repositories commit their own `CLAUDE.md`.

## Rules

- **Git:** Dag-Morten commits and pushes himself. Do not commit or push; give him the commands. Remotes are HTTPS (`https://github.com/dagmortensj/...`), never SSH.
- **Brewfiles are curated by hand.** Never run `brew bundle dump`. Add or remove single lines.
- **No permanent installs without asking.** If a task needs a tool once (converting a figure, say), ask before installing it, and remove it again afterwards unless he wants to keep it. Only tools he wants to keep go into a Brewfile.
- **Running Python:** `pyrun file.py` uses the nearest project `.venv`, otherwise the standard environment; ⌘R in VS Code calls it. Projects build their `.venv` with `uv sync` and run things with `uv run`.
- **Python packages** go into the standard environment with `pyadd` / `pyremove` (or `uv add/remove --project configs/python` with `UV_PROJECT_ENVIRONMENT=~/.venvs/standard`). Never `pip install`.
- **iTerm2 changes** are saved with `scripts/iterm-export.sh`, never by editing the plist by hand.
- **`.zshrc` and `.zprofile` cannot be read** through Claude's device shell (Permission denied), not even in `configs/zsh/`. Read the committed version with `git show HEAD:configs/zsh/.zshrc`, and give Dag-Morten terminal commands for changes.
- **Symlinked files:** `~/.gitconfig` is a link to `configs/git/.gitconfig`, so `git config --global` writes into the repo. Personal git settings go in `~/.gitconfig.local`.
- **Scripts:** quiet terminal output, one status line per step; details go to a log. Keep `install.sh` idempotent and never let it overwrite or delete anything except through its backup mechanism. Deletions use fixed literal paths only. Run `shellcheck` on any script you change.
- **Documentation** is in English, in plain, well-written prose: no slogans, no punchy one-liners, no "not X but Y" constructions. When behaviour changes, update `README.md` and `configs/README.md` in the same change.

## Checking a change

- `bash -n` and `shellcheck` on `install.sh`, `scripts/*.sh`, `configs/macos/defaults.sh` and `configs/vscode/setup.sh`. Claude's device shell has no shellcheck: stage the scripts to the cloud sandbox and run it there (`pip install shellcheck-py`).
- `configs/vscode/setup.sh` can be exercised without VS Code by running it with `HOME` set to an empty folder and a stub `code` command first on `PATH`.
- `./install.sh --dry-run` (or with a group) shows what would happen without changing anything.
- On this Mac, where the apps were installed by hand, use `--skip-casks`.
