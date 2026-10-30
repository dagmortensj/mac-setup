#!/bin/bash
# Restores the VS Code setup: Default profile (LaTeX + Python), Tavle profile
# (live coding in class), keybindings, the two home-made extensions and the
# global latexmk config. Safe to re-run; backs up settings and keybindings.
#
# An extension that fails to install is reported and the script carries on;
# it exits with status 1 at the end if anything failed.
set -e
U="$HOME/Library/Application Support/Code/User"
HER="$(cd "$(dirname "$0")" && pwd)"
STAMP="$(date +%Y%m%d-%H%M)"
FEIL=0

command -v code >/dev/null || { echo "ERROR: the code command is missing. In VS Code: Shell Command: Install 'code' command in PATH."; exit 1; }

# install EXTENSION [ARGS...]: installs quietly, reports a failure without stopping
install() {
  code --install-extension "$@" >/dev/null 2>&1 || { echo "ERROR: $1"; FEIL=1; }
}

# The Høst themes were called host-theme before version 3.5. VS Code sees the new
# name as a different extension, so the old one is removed (nothing happens if it is gone).
code --uninstall-extension dagmorten.host-theme >/dev/null 2>&1 || true

# 1. Default profile
mkdir -p "$U"
cp "$U/settings.json" "$U/settings.backup-$STAMP.json" 2>/dev/null || true
cp "$U/keybindings.json" "$U/keybindings.backup-$STAMP.json" 2>/dev/null || true
cp "$HER/default/settings.json" "$U/settings.json"
cp "$HER/keybindings.json" "$U/keybindings.json"
while read -r e; do
  [ -n "$e" ] && install "$e"
done < "$HER/extensions.txt"
install "$HER/tex-oppstart/tex-oppstart-1.0.0.vsix" --force
install "$HER/hoest-theme.vsix" --force
echo "OK: Default profile"

# 2. Tavle profile (created if missing)
find_tavle() {
  [ -f "$U/globalStorage/storage.json" ] || return 0
  python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(next((p['location'] for p in d.get('userDataProfiles',[]) if p['name']=='Tavle'),''))" "$U/globalStorage/storage.json"
}
ID="$(find_tavle)"
if [ -z "$ID" ]; then
  code --profile "Tavle" --new-window >/dev/null 2>&1 || true
  for i in $(seq 1 30); do ID="$(find_tavle)"; [ -n "$ID" ] && break; sleep 1; done
fi
[ -z "$ID" ] && { echo "ERROR: Tavle profile not found. Create it in VS Code (Profiles > New Profile > Tavle) and re-run."; exit 1; }
P="$U/profiles/$ID"; mkdir -p "$P"
cp "$HER/tavle/settings.json" "$P/settings.json"
cp "$HER/keybindings.json" "$P/keybindings.json"
code --uninstall-extension dagmorten.host-theme --profile "Tavle" >/dev/null 2>&1 || true
for e in ms-python.python ms-toolsai.jupyter "$HER/hoest-theme.vsix"; do
  install "$e" --profile "Tavle" --force
done
echo "OK: Tavle profile"

# 3. Global latexmk config (engine fallback for projects without .latexmkrc)
mkdir -p "$HOME/.config/latexmk"
cp "$HER/../latexmk/latexmkrc" "$HOME/.config/latexmk/latexmkrc"
echo "OK: latexmkrc"

exit "$FEIL"
