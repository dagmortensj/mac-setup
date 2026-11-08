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
- `configs/vscode/`: tex-oppstart, plus a settings snapshot for the fallback `setup.sh`. Settings Sync is the real source for VS Code.

## Rules

- **Git:** Dag-Morten commits and pushes himself. Do not commit or push; give him the commands. Remotes are HTTPS (`https://github.com/dagmortensj/...`), never SSH.
- **Brewfiles are curated by hand.** Never run `brew bundle dump`. Add or remove single lines.
- **No permanent installs without asking.** If a task needs a tool once (converting a figure, say), ask before installing it, and remove it again afterwards unless he wants to keep it. Only tools he wants to keep go into a Brewfile.
- **Python packages** go into the standard environment with `pyadd` / `pyremove` (or `uv add/remove --project configs/python` with `UV_PROJECT_ENVIRONMENT=~/.venvs/standard`). Never `pip install`.
- **iTerm2 changes** are saved with `scripts/iterm-export.sh`, never by editing the plist by hand.
- **Symlinked files:** `~/.gitconfig` is a link to `configs/git/.gitconfig`, so `git config --global` writes into the repo. Personal git settings go in `~/.gitconfig.local`.
- **Scripts:** quiet terminal output, one status line per step; details go to a log. Keep `install.sh` idempotent and never let it overwrite or delete anything except through its backup mechanism. Deletions use fixed literal paths only. Run `shellcheck` on any script you change.
- **Documentation** is in English, in plain, well-written prose: no slogans, no punchy one-liners, no "not X but Y" constructions. When behaviour changes, update `README.md` and `configs/README.md` in the same change.

## Checking a change

- `bash -n install.sh` and `shellcheck install.sh scripts/*.sh configs/macos/defaults.sh`.
- `./install.sh --dry-run` (or with a group) shows what would happen without changing anything.
- On this Mac, where the apps were installed by hand, use `--skip-casks`.
