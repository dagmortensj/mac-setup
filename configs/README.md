# Config files — where they live on macOS

Quick reference for grabbing each config off your current Mac and dropping it into this folder.

| Tool | Path on macOS | Goes into |
|---|---|---|
| **zsh / Oh My Zsh** | `~/.zshrc` | `configs/zsh/.zshrc` |
| **Powerlevel10k** | `~/.p10k.zsh` | `configs/zsh/.p10k.zsh` |
| **Neofetch** | `~/.config/neofetch/config.conf` | `configs/neofetch/config.conf` |
| **fastfetch** *(if used)* | `~/.config/fastfetch/config.jsonc` | `configs/fastfetch/config.jsonc` |
| **VS Code settings** | `~/Library/Application Support/Code/User/settings.json` | `configs/vscode/settings.json` |
| **VS Code keybindings** | `~/Library/Application Support/Code/User/keybindings.json` | `configs/vscode/keybindings.json` |
| **VS Code snippets** | `~/Library/Application Support/Code/User/snippets/` | `configs/vscode/snippets/` |
| **VS Code extensions list** | (run `code --list-extensions`) | `configs/vscode/extensions.txt` |
| **iTerm2 (archive)** ✅ | iTerm2 → Settings → General → Settings → *Export All Settings and Data* | `configs/iterm2/iterm2-settings.itermexport` |
| **iTerm2 (folder)** *(alt)* | iTerm2 → Settings → General → Settings → *Save current settings to folder* | `configs/iterm2/com.googlecode.iterm2.plist` |
| **Git** | `~/.gitconfig` | `configs/.gitconfig` |
| **Homebrew package list** | (run `brew bundle dump --file=Brewfile`) | `configs/Brewfile` |
| **SSH config** *(optional)* | `~/.ssh/config` | `configs/ssh/config` *(never commit private keys)* |

---

## Copy everything in one go

Run this from the root of the repo on your **current** Mac to populate `configs/`:

```bash
cd path/to/mac-setup

# Shell + prompt
cp ~/.zshrc                                                  configs/zsh/.zshrc
cp ~/.p10k.zsh                                               configs/zsh/.p10k.zsh

# Neofetch / fastfetch
mkdir -p configs/neofetch configs/fastfetch
[ -f ~/.config/neofetch/config.conf ]      && cp ~/.config/neofetch/config.conf      configs/neofetch/config.conf
[ -f ~/.config/fastfetch/config.jsonc ]    && cp ~/.config/fastfetch/config.jsonc    configs/fastfetch/config.jsonc

# VS Code
cp "$HOME/Library/Application Support/Code/User/settings.json"    configs/vscode/settings.json
cp "$HOME/Library/Application Support/Code/User/keybindings.json" configs/vscode/keybindings.json
cp -R "$HOME/Library/Application Support/Code/User/snippets"      configs/vscode/snippets 2>/dev/null
code --list-extensions > configs/vscode/extensions.txt

# Git
cp ~/.gitconfig configs/.gitconfig

# Homebrew snapshot
brew bundle dump --file=configs/Brewfile --force
```

For **iTerm2**: open Settings → General → Settings → check *Load preferences from a custom folder or URL*, point it at `configs/iterm2/`, and tick *Save changes to folder when iTerm2 quits*. iTerm will write `com.googlecode.iterm2.plist` into that folder.

---

## What NOT to commit

- `~/.ssh/id_*` — private keys, never. Only the `config` file is safe.
- API tokens or credentials inside `.zshrc` — move them to `~/.zshenv` (not committed) or use a secrets manager.
- `~/.aws/credentials`, `~/.npmrc` with auth tokens, `.env` files.

Add a `.gitignore` at the repo root with at least:

```
.DS_Store
configs/ssh/id_*
configs/**/*.private*
*.local.json
```
