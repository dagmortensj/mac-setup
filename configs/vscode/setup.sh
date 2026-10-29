#!/bin/bash
# Restores the VS Code setup: Default profile (LaTeX + Python), Tavle profile
# (live coding in class), keybindings, the two home-made extensions and the
# global latexmk config. Safe to re-run; backs up settings and keybindings.
set -e
U="$HOME/Library/Application Support/Code/User"
HER="$(cd "$(dirname "$0")" && pwd)"
STAMP="$(date +%Y%m%d-%H%M)"

# 1. Default profile
cp "$U/settings.json" "$U/settings.backup-$STAMP.json" 2>/dev/null || true
cp "$U/keybindings.json" "$U/keybindings.backup-$STAMP.json" 2>/dev/null || true
cp "$HER/default/settings.json" "$U/settings.json"
cp "$HER/keybindings.json" "$U/keybindings.json"
while read -r e; do [ -n "$e" ] && code --install-extension "$e" >/dev/null 2>&1; done < "$HER/extensions.txt"
code --install-extension "$HER/tex-oppstart/tex-oppstart-1.0.0.vsix" --force >/dev/null 2>&1
code --install-extension "$HER/host/host-theme.vsix" --force >/dev/null 2>&1
echo "OK: Default profile"

# 2. Tavle profile (created if missing)
find_tavle() {
  python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(next((p['location'] for p in d.get('userDataProfiles',[]) if p['name']=='Tavle'),''))" "$U/globalStorage/storage.json"
}
ID="$(find_tavle)"
if [ -z "$ID" ]; then
  code --profile "Tavle" --new-window >/dev/null 2>&1
  for i in $(seq 1 30); do ID="$(find_tavle)"; [ -n "$ID" ] && break; sleep 1; done
fi
[ -z "$ID" ] && { echo "ERROR: Tavle profile not found. Create it in VS Code (Profiles > New Profile > Tavle) and re-run."; exit 1; }
P="$U/profiles/$ID"; mkdir -p "$P"
cp "$HER/tavle/settings.json" "$P/settings.json"
cp "$HER/keybindings.json" "$P/keybindings.json"
for e in ms-python.python ms-toolsai.jupyter "$HER/host/host-theme.vsix"; do
  code --install-extension "$e" --profile "Tavle" --force >/dev/null 2>&1 || echo "ERROR: $e"
done
echo "OK: Tavle profile"

# 3. Global latexmk config (engine fallback for projects without .latexmkrc)
mkdir -p "$HOME/.config/latexmk"
cp "$HER/../latexmk/latexmkrc" "$HOME/.config/latexmk/latexmkrc"
echo "OK: latexmkrc"
