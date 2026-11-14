# configs/

Where each file goes on the Mac, and how it gets there. "Link" means that `install.sh` makes the file in the home folder a symlink to the file here, so edits on the Mac are edits in the repository.

| File here | On the Mac | How |
|---|---|---|
| `zsh/.zshrc` | `~/.zshrc` | link (`terminal`) |
| `zsh/.zprofile` | `~/.zprofile` | link (`terminal`) |
| `zsh/.p10k.zsh` | `~/.p10k.zsh` | link (`terminal`) |
| `fastfetch/config.jsonc`, `fastfetch/eple.txt` | `~/.config/fastfetch/` | link (`terminal`) |
| `iterm2/com.googlecode.iterm2.plist` | iTerm2's settings | imported once with `defaults import` (`terminal`); updated with `scripts/iterm-export.sh` |
| `iterm2/farger/*.itermcolors` | iTerm2 colour presets | inside the settings above; double-click to import on their own |
| `git/.gitconfig` | `~/.gitconfig` | link (`dev`); personal settings go in `~/.gitconfig.local`, which is not in the repo |
| `latexmk/latexmkrc` | `~/.config/latexmk/latexmkrc` | link (`dev`) |
| `python/` | `~/.venvs/standard` | built with `uv sync --locked` (`dev`) |
| `uv/uv.toml` | `~/.config/uv/uv.toml` | link (`dev`) |
| `vscode/tex-oppstart/`, `vscode/classroom-mode/` | VS Code extensions | installed from the `.vsix` into the Default profile (`dev`) |
| `vscode/tex-preambel/` | VS Code extension | installed from the `.vsix` into the Writing profile (`dev`) |
| `vscode/workspace-switcher/` | VS Code extension | installed from the `.vsix` into both profiles (`dev`) |
| `vscode/default/settings.json`, `vscode/writing/settings.json`, `vscode/keybindings.json`, `vscode/extensions.txt` | VS Code | a copy: `vscode/setup.sh save` refreshes it from the Mac, `vscode/setup.sh restore` puts it back, and `vscode/setup.sh check` compares the two |
| `vscode/workspaces/*.code-workspace` | (stays here) | opened from the repo in VS Code, by hand or with the workspace-switcher button; folder paths are relative to the file |
| `cspell/ordliste.txt` | (stays here) | read straight from the repo by Code Spell Checker |
| `brew/*.Brewfile` | Homebrew packages | `brew bundle --no-upgrade` (`terminal`, `dev`, `apps`) |
| `repos.txt` | `~/Developer/<name>` | cloned (`repos`) |
| `claude/claude-code/CLAUDE.md` | `~/.claude/CLAUDE.md` | relative link (`repos`); read by Claude Code in every folder |
| `claude/developer/CLAUDE.md` | `~/Developer/CLAUDE.md` | relative link (`repos`) |
| `macos/defaults.sh` | macOS settings | run (`macos`) |

## What never goes in here

- Private keys (`~/.ssh/id_*`), tokens, passwords, `.env` files.
- `~/.gitconfig.local` (name, email, sign-in).
- API keys in shell files. Put them in `~/.zshenv`, which is not in the repo, or in the macOS keychain.

`.gitignore` blocks the usual names as a safety net.
