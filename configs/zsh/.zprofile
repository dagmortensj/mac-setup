# ~/.zprofile is read by login shells: every new iTerm2 window, and the VS Code
# terminal. It only sets PATH; everything else is in ~/.zshrc.

# Homebrew (Apple Silicon)
if [[ -x /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# The standard Python environment (configs/python/, built by install.sh) comes
# first, so `python3` and `python` in a terminal are that environment. It has
# to come after Homebrew, which puts /opt/homebrew/bin first.
if [[ -d "$HOME/.venvs/standard/bin" ]]; then
  path=("$HOME/.venvs/standard/bin" $path)
fi

# Remove duplicates; a VS Code terminal inherits a PATH that already has these.
typeset -U path
