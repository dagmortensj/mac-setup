#!/bin/bash
# install.sh: sets up a Mac from this repository. See README.md.
#
#   ./install.sh                  everything: terminal dev apps repos macos
#   ./install.sh terminal         only the terminal look (what other people want)
#   ./install.sh dev macos        several groups; they always run in the order above
#   ./install.sh --dry-run        show what would happen, change nothing
#   ./install.sh --skip-casks     install command-line tools but no apps (casks),
#                                 for a Mac where the apps were installed by hand
#
# Each step prints one line: OK, SKIP or FAIL. The full output goes to a log
# in ~/Library/Logs/mac-setup/. A failed step does not stop the others, and
# the script can be run again as often as needed: steps that are already done
# are left as they are (only the zsh plugins and Powerlevel10k get updated).
#
# Written for the bash 3.2 that ships with macOS.

set -o pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
BREW=/opt/homebrew/bin/brew
ALL_GROUPS="terminal dev apps repos macos"
STAMP="$(date +%Y-%m-%d-%H%M%S)"
LOG_DIR="$HOME/Library/Logs/mac-setup"
LOG="$LOG_DIR/install-$STAMP.log"
BACKUP="$HOME/.mac-setup-backup/$STAMP"
VENV="$HOME/.venvs/standard"

DRY=0
SKIP_CASKS=0
SELECTED=""
FULL=0
FAILED=""
DIFFERED=""
NOTE=""
GIT_NAME=""
GIT_EMAIL=""

usage() {
  sed -n '2,13p' "$REPO/install.sh" | sed 's/^# \{0,1\}//'
}

die() {
  echo "STOP: $*" >&2
  exit 1
}

# pretty PATH: the path with ~ for the home folder, for messages.
# shellcheck disable=SC2088  # a literal ~ is the point here
pretty() {
  case "$1" in
    "$HOME"/*) echo "~/${1#"$HOME"/}" ;;
    *) echo "$1" ;;
  esac
}

for arg in "$@"; do
  case "$arg" in
    --dry-run)    DRY=1 ;;
    --skip-casks) SKIP_CASKS=1 ;;
    -h|--help)    usage; exit 0 ;;
    terminal|dev|apps|repos|macos) SELECTED="$SELECTED $arg" ;;
    *) echo "Unknown option or group: $arg"; echo; usage; exit 2 ;;
  esac
done
if [ -z "$SELECTED" ]; then
  SELECTED=" $ALL_GROUPS"
  FULL=1
fi

want() {
  case "$SELECTED " in
    *" $1 "*) return 0 ;;
  esac
  return 1
}

# ---------------------------------------------------------------- helpers

# In a dry run, steps describe what they would do. The description goes to
# the terminal (fd 3) and to the log.
exec 3>&1
would() {
  echo "        would $*" >&3
  echo "would $*"
}

# step LABEL FUNCTION [ARGS...]: runs one step with its output in the log and
# prints one status line. A function returns 0 for OK, 3 for SKIP and
# anything else for FAIL, and can put a short remark in NOTE.
step() {
  local label="$1" rc status
  shift
  NOTE=""
  echo "=== $label" >>"$LOG"
  [ "$DRY" = 1 ] && echo "      $label"
  "$@" </dev/null >>"$LOG" 2>&1
  rc=$?
  case "$rc" in
    0) status="OK" ;;
    3) status="SKIP" ;;
    *) status="FAIL"; FAILED="$FAILED
        $label" ;;
  esac
  echo "$status: $NOTE (exit $rc)" >>"$LOG"
  if [ "$DRY" = 1 ]; then
    [ "$status" = "OK" ] || printf '%-4s  %s%s\n' "$status" "$label" "$NOTE"
  else
    printf '%-4s  %s%s\n' "$status" "$label" "$NOTE"
  fi
}

# Steps that take long say so before they start.
slow() {
  [ "$DRY" = 1 ] || echo "      $1 ..."
}

# link SOURCE DESTINATION [relative]: makes DESTINATION a symlink to SOURCE
# (a path in the repo). With "relative", the link holds a relative path, so it
# also works where the folders are mounted somewhere else. Whatever is at
# DESTINATION already is moved to the backup folder first. A regular file that
# differs from the repo's version is remembered, so the summary can point it out.
link() {
  local src="$REPO/$1" dest="$2" rel target
  if [ ! -e "$src" ]; then
    echo "missing in the repo: $1"
    return 1
  fi
  target="$src"
  if [ "$3" = "relative" ]; then
    target="$(/usr/bin/python3 -c 'import os, sys; print(os.path.relpath(sys.argv[1], os.path.dirname(sys.argv[2])))' "$src" "$dest")" || return 1
  fi
  if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$target" ]; then
    echo "already linked: $dest"
    return 0
  fi
  if [ "$DRY" = 1 ]; then
    if [ -e "$dest" ] || [ -L "$dest" ]; then
      would "move $(pretty "$dest") to the backup folder and link it to $1"
    else
      would "link $(pretty "$dest") to $1"
    fi
    return 0
  fi
  mkdir -p "$(dirname "$dest")" || return 1
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if [ -f "$dest" ] && [ ! -L "$dest" ] && ! cmp -s "$dest" "$src"; then
      DIFFERED="$DIFFERED
        $(pretty "$dest")"
    fi
    rel="${dest#"$HOME"/}"
    mkdir -p "$(dirname "$BACKUP/$rel")" || return 1
    mv "$dest" "$BACKUP/$rel" || return 1
    echo "moved $dest to $BACKUP/$rel"
  fi
  ln -s "$target" "$dest" && echo "linked $dest -> $target"
}

# brew_bundle NAME: installs what is missing from configs/brew/NAME.Brewfile.
# Nothing that is already installed is upgraded.
brew_bundle() {
  local file="$REPO/configs/brew/$1.Brewfile" casks=""
  [ -f "$file" ] || { echo "missing: $file"; return 1; }
  if [ "$SKIP_CASKS" = 1 ]; then
    casks="$(HOMEBREW_NO_AUTO_UPDATE=1 brew bundle list --cask --file="$file")" || return 1
    casks="$(printf '%s\n' "$casks" | tr '\n' ' ' | sed 's/ *$//')"   # one line
    [ -n "$casks" ] && NOTE=" (apps skipped: $casks)"
  fi
  if [ "$DRY" = 1 ]; then
    if brew bundle check --no-upgrade --file="$file" >/dev/null 2>&1; then
      would "install nothing: everything in $1.Brewfile is installed"
    else
      would "install what is missing from $1.Brewfile:"
      brew bundle check --no-upgrade --verbose --file="$file" 2>&1 | grep -v '^brew bundle can' | sed 's/^/            /' >&3
      [ -n "$casks" ] && would "skip these casks: $casks"
    fi
    return 0
  fi
  HOMEBREW_BUNDLE_CASK_SKIP="$casks" brew bundle --no-upgrade --file="$file"
}

# ---------------------------------------------------------------- preflight

[ "$(uname -s)" = "Darwin" ] || die "this script is for macOS."
[ "$(uname -m)" = "arm64" ] || die "this script expects an Apple Silicon Mac (Homebrew in /opt/homebrew)."
[ "$(id -u)" != "0" ] || die "run it as your normal user, not with sudo."
xcode-select -p >/dev/null 2>&1 || die "the Command Line Tools are missing. Install Homebrew first (see the README); it installs them."
if want terminal || want dev || want apps; then
  [ -x "$BREW" ] || die "Homebrew is not installed. Install it first (see the Quick start in the README), then run this again."
fi
if [ -x "$BREW" ]; then
  eval "$("$BREW" shellenv)"
  export HOMEBREW_NO_ENV_HINTS=1
  # A dry run changes nothing, not even Homebrew itself.
  [ "$DRY" = 1 ] && export HOMEBREW_NO_AUTO_UPDATE=1
fi

mkdir -p "$LOG_DIR" || die "cannot create $LOG_DIR"
{
  echo "mac-setup install.sh, $STAMP"
  echo "repo: $REPO   groups:$SELECTED   dry-run: $DRY   skip-casks: $SKIP_CASKS"
} >"$LOG"

echo
[ "$DRY" = 1 ] && echo "Dry run: nothing will be changed."
echo "Groups:$SELECTED"
echo "Log:    $(pretty "$LOG")"
if [ "$REPO" != "$HOME/Developer/mac-setup" ]; then
  echo
  echo "Note: the repo is at $REPO, not ~/Developer/mac-setup. The links will point"
  echo "here, but the VS Code settings expect ~/Developer/mac-setup (spell-check word list)."
fi
echo

# Everything that needs an answer is asked now, so the rest can run unattended.

# Git identity, only if ~/.gitconfig.local does not have one yet. An existing
# ~/.gitconfig (from before this setup) is read first.
if want dev && ! git config --file "$HOME/.gitconfig.local" user.name >/dev/null 2>&1; then
  GIT_NAME="$(git config --file "$HOME/.gitconfig" user.name 2>/dev/null)"
  GIT_EMAIL="$(git config --file "$HOME/.gitconfig" user.email 2>/dev/null)"
  if [ -z "$GIT_NAME" ] || [ -z "$GIT_EMAIL" ]; then
    if [ "$DRY" = 1 ]; then
      echo "(A real run would ask for your name and email for git here.)"
    else
      echo "Name and email for your git commits (stored in ~/.gitconfig.local):"
      read -r -p "  Name:  " GIT_NAME || die "no answer"
      read -r -p "  Email: " GIT_EMAIL || die "no answer"
      [ -n "$GIT_NAME" ] && [ -n "$GIT_EMAIL" ] || die "both name and email are needed."
      echo
    fi
  else
    echo "Git identity taken from the existing ~/.gitconfig: $GIT_NAME <$GIT_EMAIL>"
    echo
  fi
fi

# The admin password for the macos group (pmset, removing apps), asked now
# and kept active by a background loop. Homebrew does not use it: since
# version 7 it deliberately asks for the password itself whenever a cask's
# installer needs it (MacTeX, Teams, Logi Options+).
if [ "$DRY" = 0 ] && want macos; then
  echo "Your Mac password, for the macOS settings at the end:"
  sudo -v || die "no admin password given."
  ( while kill -0 $$ 2>/dev/null; do sudo -n true 2>/dev/null; sleep 50; done ) &
  KEEPALIVE=$!
  trap 'kill "$KEEPALIVE" 2>/dev/null' EXIT
  echo
fi

# Keep the Mac awake while this runs.
[ "$DRY" = 0 ] && caffeinate -dims -w $$ >/dev/null 2>&1 &

# ---------------------------------------------------------------- terminal

oh_my_zsh() {
  local tmp rc
  if [ -d "$HOME/.oh-my-zsh" ]; then
    echo "already installed"
    return 0
  fi
  if [ "$DRY" = 1 ]; then
    would "install Oh My Zsh (unattended, keeping ~/.zshrc)"
    return 0
  fi
  tmp="$(mktemp "${TMPDIR:-/tmp}/omz-install.XXXXXX")" || return 1
  if ! curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -o "$tmp"; then
    rm -f "$tmp"
    return 1
  fi
  RUNZSH=no CHSH=no KEEP_ZSHRC=yes sh "$tmp" --unattended --keep-zshrc
  rc=$?
  rm -f "$tmp"
  return "$rc"
}

# clone_or_update URL DIRECTORY
clone_or_update() {
  if [ -d "$2/.git" ]; then
    if [ "$DRY" = 1 ]; then would "update $(pretty "$2")"; return 0; fi
    git -C "$2" pull --ff-only --quiet
  else
    if [ "$DRY" = 1 ]; then would "clone $1"; return 0; fi
    git clone --depth 1 --quiet "$1" "$2"
  fi
}

zsh_plugins() {
  local custom="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}" ok=0
  if [ ! -d "$HOME/.oh-my-zsh" ] && [ "$DRY" = 0 ]; then
    NOTE=" (Oh My Zsh is missing)"
    return 3
  fi
  clone_or_update https://github.com/zsh-users/zsh-autosuggestions "$custom/plugins/zsh-autosuggestions" || ok=1
  clone_or_update https://github.com/zsh-users/zsh-syntax-highlighting "$custom/plugins/zsh-syntax-highlighting" || ok=1
  clone_or_update https://github.com/romkatv/powerlevel10k "$custom/themes/powerlevel10k" || ok=1
  return "$ok"
}

shell_links() {
  local ok=0
  link configs/zsh/.zshrc "$HOME/.zshrc" || ok=1
  link configs/zsh/.zprofile "$HOME/.zprofile" || ok=1
  link configs/zsh/.p10k.zsh "$HOME/.p10k.zsh" || ok=1
  link configs/fastfetch/config.jsonc "$HOME/.config/fastfetch/config.jsonc" || ok=1
  link configs/fastfetch/eple.txt "$HOME/.config/fastfetch/eple.txt" || ok=1
  if [ ! -e "$HOME/.hushlogin" ]; then
    if [ "$DRY" = 1 ]; then would "create ~/.hushlogin"; else touch "$HOME/.hushlogin" || ok=1; fi
  fi
  return "$ok"
}

# iTerm2's settings are imported only when iTerm2 has none yet (a new Mac),
# so settings changed on this Mac since the last export are never overwritten.
iterm_settings() {
  local plist="$REPO/configs/iterm2/com.googlecode.iterm2.plist"
  [ -f "$plist" ] || { echo "missing: $plist"; return 1; }
  if defaults read com.googlecode.iterm2 >/dev/null 2>&1; then
    NOTE=" (iTerm2 already has settings; to replace them, quit iTerm2 and run: defaults import com.googlecode.iterm2 configs/iterm2/com.googlecode.iterm2.plist)"
    return 3
  fi
  if pgrep -xq iTerm2; then
    NOTE=" (iTerm2 is running: quit it and run ./install.sh terminal from Terminal.app)"
    return 3
  fi
  if [ "$DRY" = 1 ]; then would "import iTerm2 settings from configs/iterm2/"; return 0; fi
  defaults import com.googlecode.iterm2 "$plist"
}

group_terminal() {
  slow "Homebrew: terminal.Brewfile, this can take a while"
  step "Homebrew: terminal.Brewfile" brew_bundle terminal
  step "Shell and fastfetch config (links)" shell_links
  step "Oh My Zsh" oh_my_zsh
  step "zsh plugins and Powerlevel10k" zsh_plugins
  step "iTerm2 settings" iterm_settings
}

# ---------------------------------------------------------------- dev

# ~/.gitconfig.local: name, email and the GitHub sign-in through gh. The empty
# helper line clears the macOS keychain helper that Homebrew's git sets, so
# git always asks gh for the current token.
git_config() {
  local f="$HOME/.gitconfig.local" ok=0 host
  link configs/git/.gitconfig "$HOME/.gitconfig" || ok=1
  if ! git config --file "$f" user.name >/dev/null 2>&1; then
    if [ "$DRY" = 1 ]; then
      would "write your git name and email to ~/.gitconfig.local"
    else
      git config --file "$f" user.name "$GIT_NAME" || ok=1
      git config --file "$f" user.email "$GIT_EMAIL" || ok=1
    fi
  fi
  if ! git config --file "$f" --get-all credential.https://github.com.helper >/dev/null 2>&1; then
    if [ "$DRY" = 1 ]; then
      would "let git sign in to GitHub through gh (in ~/.gitconfig.local)"
    else
      for host in https://github.com https://gist.github.com; do
        git config --file "$f" --add "credential.$host.helper" "" || ok=1
        git config --file "$f" --add "credential.$host.helper" "!/opt/homebrew/bin/gh auth git-credential" || ok=1
      done
    fi
  fi
  return "$ok"
}

tool_links() {
  local ok=0
  link configs/latexmk/latexmkrc "$HOME/.config/latexmk/latexmkrc" || ok=1
  link configs/uv/uv.toml "$HOME/.config/uv/uv.toml" || ok=1
  return "$ok"
}

# The standard Python environment, from configs/python/ (uv.lock pins every
# version). uv downloads Python 3.13 itself the first time.
python_env() {
  command -v uv >/dev/null 2>&1 || { NOTE=" (uv is not installed)"; return 1; }
  if [ "$DRY" = 1 ]; then
    would "build $(pretty "$VENV") from configs/python/ (uv sync --locked)"
    return 0
  fi
  UV_PROJECT_ENVIRONMENT="$VENV" uv sync --locked --project "$REPO/configs/python" || return 1
  "$VENV/bin/python" -c "import numpy, matplotlib, tkinter; print('numpy', numpy.__version__, 'matplotlib', matplotlib.__version__, 'tk', tkinter.TkVersion)"
}

# VS Code's Python settings, written into this Mac's settings: the default
# profile and every other profile that exists. Run `./install.sh dev` again
# after Settings Sync has brought in the other profiles.
#   python.defaultInterpreterPath           the standard environment
#   python-envs.terminal.autoActivationType off
#   python.terminal.activateEnvironment     false
# The environment is already first on PATH, so the terminal needs no
# activation; the activation command VS Code types into a new terminal
# otherwise collides with the command that Cmd+R types. The first two are
# machine settings, which Settings Sync leaves out.
vscode_python() {
  local user="$HOME/Library/Application Support/Code/User" f
  local files=("$user/settings.json")
  for f in "$user"/profiles/*/settings.json; do
    [ -f "$f" ] && files+=("$f")
  done
  if [ "$DRY" = 1 ]; then
    would "point VS Code's Python at $(pretty "$VENV") and turn off terminal activation (${#files[@]} settings file(s))"
    return 0
  fi
  if [ ! -x "$VENV/bin/python" ]; then
    NOTE=" (the standard environment is missing)"
    return 3
  fi
  "$VENV/bin/python" - "$VENV/bin/python" "${files[@]}" <<'PY'
import json, os, re, sys

settings = {
    "python.defaultInterpreterPath": sys.argv[1],
    "python-envs.terminal.autoActivationType": "off",
    "python.terminal.activateEnvironment": False,
}
scalar = r'(?:"(?:[^"\\]|\\.)*"|true|false|null|-?\d+(?:\.\d+)?)'

def set_key(text, key, value):
    entry = f'"{key}": {json.dumps(value)}'
    pattern = re.compile(r'"' + re.escape(key) + r'"\s*:\s*' + scalar)
    if pattern.search(text):
        return pattern.sub(lambda m: entry, text, count=1)
    start = text.find("{")
    if start < 0:
        raise ValueError("no { found")
    rest = text[start + 1:]
    # Comments do not count as content when deciding on the comma.
    bare = re.sub(r"//[^\n]*|/\*.*?\*/", "", rest, flags=re.S).strip()
    if bare in ("", "}"):
        return text[:start + 1] + "\n    " + entry + "\n" + rest.lstrip()
    return text[:start + 1] + "\n    " + entry + "," + rest

for path in sys.argv[2:]:
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        text = "{}\n"
    else:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    new = text
    try:
        for key, value in settings.items():
            new = set_key(new, key, value)
    except ValueError:
        sys.exit(f"not a settings file: {path}")
    if new != text or not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        print("updated", path)
    else:
        print("already set", path)
PY
}

tex_oppstart() {
  local code vsix="$REPO/configs/vscode/tex-oppstart/tex-oppstart-1.0.0.vsix"
  code="$(command -v code)" || code="/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
  if [ ! -x "$code" ]; then
    NOTE=" (VS Code is not installed)"
    [ "$DRY" = 1 ] && { would "install tex-oppstart once VS Code is installed"; return 0; }
    return 3
  fi
  if "$code" --list-extensions 2>/dev/null | grep -qx 'dagmorten.tex-oppstart'; then
    echo "already installed"
    return 0
  fi
  if [ "$DRY" = 1 ]; then would "install the VS Code extension tex-oppstart"; return 0; fi
  "$code" --install-extension "$vsix" --force
}

group_dev() {
  slow "Homebrew: dev.Brewfile. MacTeX is about 6 GB, and Homebrew asks for your password when it installs it"
  step "Homebrew: dev.Brewfile" brew_bundle dev
  step "Git config (link and ~/.gitconfig.local)" git_config
  step "latexmk and uv config (links)" tool_links
  step "Python standard environment" python_env
  step "VS Code: Python interpreter" vscode_python
  step "VS Code: tex-oppstart" tex_oppstart
}

# ---------------------------------------------------------------- apps

group_apps() {
  slow "Homebrew: apps.Brewfile. Homebrew asks for your password for Teams and Logi Options+"
  step "Homebrew: apps.Brewfile" brew_bundle apps
}

# ---------------------------------------------------------------- repos

# clone_repo URL: clones into ~/Developer. An existing folder is never touched.
clone_repo() {
  local dest
  dest="$HOME/Developer/$(basename "$1" .git)"
  if [ -e "$dest" ]; then
    NOTE=" (already there)"
    return 0
  fi
  if [ "$DRY" = 1 ]; then would "clone $1 into $(pretty "$dest")"; return 0; fi
  mkdir -p "$HOME/Developer" && git clone --quiet "$1" "$dest"
}

# The two CLAUDE.md files that belong to the working environment rather than
# to a repository: configs/claude/claude-code/ for ~/.claude/CLAUDE.md (read
# by Claude Code in every folder) and configs/claude/developer/ for
# ~/Developer/CLAUDE.md. Both are relative links. Each repository keeps its
# own CLAUDE.md, committed in that repository.
claude_links() {
  local ok=0
  link configs/claude/claude-code/CLAUDE.md "$HOME/.claude/CLAUDE.md" relative || ok=1
  link configs/claude/developer/CLAUDE.md "$HOME/Developer/CLAUDE.md" relative || ok=1
  return "$ok"
}

group_repos() {
  local url
  [ -f "$REPO/configs/repos.txt" ] || { step "Repositories" false; return; }
  while read -r url; do
    case "$url" in ''|\#*) continue ;; esac
    step "Clone $(basename "$url" .git)" clone_repo "$url"
  done <"$REPO/configs/repos.txt"
  step "CLAUDE.md files (links)" claude_links
}

# ---------------------------------------------------------------- macos

macos_defaults() {
  local file="$REPO/configs/macos/defaults.sh"
  if [ "$DRY" = 1 ]; then
    would "apply $(grep -c '^defaults' "$file") settings from configs/macos/defaults.sh and restart Dock and Finder"
    return 0
  fi
  bash "$file" || return 1
  killall Dock Finder >/dev/null 2>&1
  return 0
}

# Studio Display: no maintenance wakes while asleep (see the README).
power_settings() {
  if [ "$DRY" = 1 ]; then would "set powernap 0 and tcpkeepalive 0 (on charger) with pmset"; return 0; fi
  sudo pmset -a powernap 0 && sudo pmset -c tcpkeepalive 0
}

# GarageBand and iMovie, if present. Only these fixed paths are ever deleted.
remove_apps() {
  local p removed=0 failed=0
  for p in "/Applications/GarageBand.app" "/Applications/iMovie.app" "/Library/Application Support/GarageBand"; do
    [ -e "$p" ] || continue
    if [ "$DRY" = 1 ]; then
      would "delete $p"
    else
      if sudo rm -rf "$p"; then
        echo "deleted $p"
      else
        failed=1
        NOTE=" (macOS refused to delete $(basename "$p"): drag it to the Bin in Finder)"
      fi
    fi
    removed=$((removed + 1))
  done
  [ "$removed" = 0 ] && NOTE=" (nothing to remove)"
  return "$failed"
}

group_macos() {
  step "macOS settings" macos_defaults
  step "Power settings (pmset)" power_settings
  step "Remove GarageBand and iMovie" remove_apps
}

# ---------------------------------------------------------------- run

for g in $ALL_GROUPS; do
  want "$g" || continue
  echo "[$g]"
  "group_$g"
  echo
done

if [ -n "$DIFFERED" ]; then
  echo "These files differed from the repo's version and were moved to"
  echo "$(pretty "$BACKUP") before being replaced by links. Compare them with the"
  echo "repo before deleting the backup:$DIFFERED"
  echo
fi

if [ -n "$FAILED" ]; then
  echo "Finished, but these steps failed:$FAILED"
  echo
  echo "The log has the details: $(pretty "$LOG")"
  echo "Fix the cause and run ./install.sh again (or just the group concerned)."
  exit 1
fi

if [ "$DRY" = 1 ]; then
  echo "Dry run finished. Nothing was changed."
  exit 0
fi

echo "Finished without errors."
if [ "$FULL" = 1 ]; then
  cat <<'EOF'

Left to do by hand (details in the README, section "After install.sh"):
  1. Log out and in again, so every macOS setting takes effect.
  2. Sign in: Dropbox, Teams, Outlook, Claude (reconnect its folders), and
     `gh auth login` (answer No to "Authenticate Git with your GitHub credentials?").
  3. VS Code: turn on Settings Sync with GitHub and choose Merge. Then run
     ./install.sh dev once more, so the synced profiles also get the Python setting.
  4. App Store, under your account: Word, Excel, PowerPoint, Outlook, OneNote,
     Pages, Numbers, Keynote, GeoGebra Classic 6, AdGuard for Safari.
  5. Download yourself: SAFEQ Client (from school) and PASCO Capstone.
  6. Safari web apps: Gmail and YouTube (File > Add to Dock).
  7. Set by hand: Night Shift, display scaling, Control Center and menu bar,
     Spotlight categories, lock screen clock, Dock apps.
  8. Check in System Settings that the settings from configs/macos/defaults.sh took.
EOF
fi
