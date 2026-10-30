# Config files — where they live on macOS

Quick reference for grabbing each config off your current Mac and dropping it into this folder.

| Tool | Path on macOS | Goes into |
|---|---|---|
| **zsh / Oh My Zsh** | `~/.zshrc` | `configs/zsh/.zshrc` |
| **Powerlevel10k** | `~/.p10k.zsh` | `configs/zsh/.p10k.zsh` |
| **fastfetch** | `~/.config/fastfetch/config.jsonc`, `~/.config/fastfetch/eple.txt` | `configs/fastfetch/config.jsonc`, `configs/fastfetch/eple.txt` (the logo) |
| **VS Code settings** | `~/Library/Application Support/Code/User/settings.json` | `configs/vscode/default/settings.json` (Tavle profile: `configs/vscode/tavle/settings.json`) |
| **VS Code keybindings** | `~/Library/Application Support/Code/User/keybindings.json` | `configs/vscode/keybindings.json` |
| **VS Code extensions list** | (run `code --list-extensions`) | `configs/vscode/extensions.txt` |
| **latexmk** | `~/.config/latexmk/latexmkrc` | `configs/latexmk/latexmkrc` |
| **Spell-check, own words** | (read straight from the repo by Code Spell Checker) | `configs/cspell/ordliste.txt` |
| **iTerm2 (archive)** ✅ | iTerm2 → Settings → General → Settings → *Export All Settings and Data* | `configs/iterm2/iterm2-settings.itermexport` |
| **iTerm2 colour presets** | Copied from the [hoest-theme](https://github.com/dagmortensj/hoest-theme) repository, not from the Mac. Double-click to import, then pick under Profiles → Colors → Color Presets | `configs/iterm2/farger/Høstlys.itermcolors`, `Høstkveld.itermcolors` |
| **Git** | `~/.gitconfig` | `configs/.gitconfig` |
| **Homebrew package list** | Curated by hand, see the note at the top of the file | `configs/Brewfile` |
| **SSH config** *(optional)* | `~/.ssh/config` | `configs/ssh/config` *(never commit private keys)* |

---

## Copy everything in one go

Run this from the root of the repo on your **current** Mac to populate `configs/`:

```bash
cd path/to/mac-setup

# Shell + prompt
cp ~/.zshrc                                                  configs/zsh/.zshrc
cp ~/.p10k.zsh                                               configs/zsh/.p10k.zsh

# fastfetch
mkdir -p configs/fastfetch
[ -f ~/.config/fastfetch/config.jsonc ] && cp ~/.config/fastfetch/config.jsonc configs/fastfetch/config.jsonc
[ -f ~/.config/fastfetch/eple.txt ] && cp ~/.config/fastfetch/eple.txt configs/fastfetch/eple.txt

# VS Code
cp "$HOME/Library/Application Support/Code/User/settings.json"    configs/vscode/default/settings.json
cp "$HOME/Library/Application Support/Code/User/keybindings.json" configs/vscode/keybindings.json
code --list-extensions > configs/vscode/extensions.txt

# Git
cp ~/.gitconfig configs/.gitconfig
```

The `Brewfile` is not part of this. It is a curated list, and `brew bundle dump` would fill it with everything installed on the Mac, including Python packages that belong in venvs. Edit it by hand.

For **iTerm2**, export the archive as described in the table and replace `configs/iterm2/iterm2-settings.itermexport`.

---

## What NOT to commit

- `~/.ssh/id_*` — private keys, never. Only the `config` file is safe.
- API tokens or credentials inside `.zshrc` — move them to `~/.zshenv` (not committed) or use a secrets manager.
- `~/.aws/credentials`, `~/.npmrc` with auth tokens, `.env` files.

The repo's `.gitignore` covers at least:

```
.DS_Store
configs/ssh/id_*
configs/**/*.private*
*.local.json
```
