#!/bin/bash
# Fallback only. VS Code Settings Sync is the normal way to restore VS Code,
# and install.sh installs tex-oppstart. Use this script if Settings Sync is
# not available: it restores the Default profile (LaTeX + Python), the Tavle
# profile (live coding in class), the writing profile (bare-bones LaTeX
# writing), keybindings, the Marketplace extensions (Høst Theme among them)
# and the home-made extensions from the snapshot in this folder. Safe to
# re-run; backs up settings and keybindings. The latexmk config is a symlink
# made by install.sh, so it is not handled here.
#
#   ./setup.sh            everything
#   ./setup.sh writing    only the named profile: default, tavle or writing
#
# An extension that fails to install is reported and the script carries on;
# it exits with status 1 at the end if anything failed.
set -e
U="$HOME/Library/Application Support/Code/User"
HER="$(cd "$(dirname "$0")" && pwd)"
STAMP="$(date +%Y%m%d-%H%M)"
FEIL=0
BARE="${1:-}"
case "$BARE" in ""|default|tavle|writing) ;; *) echo "ERROR: unknown profile '$BARE' (default, tavle or writing)"; exit 1 ;; esac

command -v code >/dev/null || { echo "ERROR: the code command is missing. In VS Code: Shell Command: Install 'code' command in PATH."; exit 1; }

# install EXTENSION [ARGS...]: installs quietly, reports a failure without stopping
install() {
  code --install-extension "$@" >/dev/null 2>&1 || { echo "ERROR: $1"; FEIL=1; }
}

# The Høst themes were called host-theme before version 3.5 and had the publisher
# dagmorten before 3.6.1. VS Code sees each as a different extension, so the old ones
# are removed (nothing happens if they are gone).
for e in dagmorten.host-theme dagmorten.hoest-theme; do
  code --uninstall-extension "$e" >/dev/null 2>&1 || true
done

# skal NAME: true when this profile is to be set up in this run
skal() { [ -z "$BARE" ] || [ "$BARE" = "$1" ]; }

# 1. Default profile
if skal default; then
  mkdir -p "$U"
  cp "$U/settings.json" "$U/settings.backup-$STAMP.json" 2>/dev/null || true
  cp "$U/keybindings.json" "$U/keybindings.backup-$STAMP.json" 2>/dev/null || true
  cp "$HER/default/settings.json" "$U/settings.json"
  cp "$HER/keybindings.json" "$U/keybindings.json"
  while read -r e; do
    [ -n "$e" ] && install "$e"
  done < "$HER/extensions.txt"
  install "$HER/tex-oppstart/tex-oppstart-1.0.0.vsix" --force
  install "$HER/arbeidsflate/arbeidsflate-1.0.0.vsix" --force
  echo "OK: Default profile"
fi

# finn_profil NAME: prints the folder id of a named profile, or nothing
finn_profil() {
  [ -f "$U/globalStorage/storage.json" ] || return 0
  python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(next((p['location'] for p in d.get('userDataProfiles',[]) if p['name']==sys.argv[2]),''))" "$U/globalStorage/storage.json" "$1"
}

# profil NAME FOLDER EXTENSION...: creates the profile if it is missing, copies
# settings and keybindings from FOLDER, and installs the extensions into it.
# An extension given as a path is a home-made .vsix in this folder.
profil() {
  local navn="$1" mappe="$2" id p e
  shift 2
  id="$(finn_profil "$navn")"
  if [ -z "$id" ]; then
    code --profile "$navn" --new-window >/dev/null 2>&1 || true
    for _ in $(seq 1 30); do id="$(finn_profil "$navn")"; [ -n "$id" ] && break; sleep 1; done
  fi
  if [ -z "$id" ]; then
    echo "ERROR: $navn profile not found. Create it in VS Code (Profiles > New Profile > $navn) and re-run."
    FEIL=1
    return 0
  fi
  p="$U/profiles/$id"; mkdir -p "$p"
  cp "$p/settings.json" "$p/settings.backup-$STAMP.json" 2>/dev/null || true
  cp "$HER/$mappe/settings.json" "$p/settings.json"
  cp "$HER/keybindings.json" "$p/keybindings.json"
  for e in dagmorten.host-theme dagmorten.hoest-theme; do
    code --uninstall-extension "$e" --profile "$navn" >/dev/null 2>&1 || true
  done
  for e in "$@"; do
    install "$e" --profile "$navn" --force
  done
  echo "OK: $navn profile"
}

# 2. Tavle profile
if skal tavle; then
  profil "Tavle" tavle ms-python.python ms-toolsai.jupyter dagmortensj.hoest-theme
  # No workspace button in Tavle: on the board only loose folders are opened,
  # and a stray click on the button would replace the folder in front of the class.
  code --uninstall-extension dagmorten.arbeidsflate --profile "Tavle" >/dev/null 2>&1 || true
fi

# 3. writing profile: LaTeX only, without Python and without Claude Code
if skal writing; then
  profil "writing" writing \
    james-yu.latex-workshop dagmortensj.hoest-theme \
    streetsidesoftware.code-spell-checker streetsidesoftware.code-spell-checker-norwegian-bokmal \
    "$HER/tex-oppstart/tex-oppstart-1.0.0.vsix" "$HER/tex-preambel/tex-preambel-1.0.0.vsix" \
    "$HER/arbeidsflate/arbeidsflate-1.0.0.vsix"
fi

exit "$FEIL"
