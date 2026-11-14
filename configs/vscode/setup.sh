#!/bin/bash
# Copies VS Code's settings between this Mac and the repository, and checks
# that the two agree. VS Code and Settings Sync own the settings: they are
# changed in VS Code, and Sync carries them to other computers. This folder
# holds a copy, for a new Mac where Sync is not available and as a record in
# git.
#
#   ./setup.sh check                   reports anything that is not as it
#                                      should be, and changes nothing
#   ./setup.sh save                    the Mac's settings, keybindings and
#                                      extension list are copied into this
#                                      folder; commit the result
#   ./setup.sh restore                 this folder's settings and keybindings
#                                      are copied onto the Mac; the Writing
#                                      profile is created if it is missing
#   ./setup.sh restore --extensions    the same, and the extensions are
#                                      installed (a Mac without Settings Sync)
#
# save and restore take the profiles to handle as further arguments, default
# or writing; without any, both are handled.
#
# The Default profile uses default/settings.json and the Writing profile
# writing/settings.json; both share keybindings.json. restore never deletes
# anything: a file it replaces is first moved to settings-backup/<time>/ in
# VS Code's User folder.
#
# save and restore also turn a settings file that is a symlink back into an
# ordinary file. For a short while the settings were links into this
# repository; an ordinary file is what VS Code and Settings Sync expect.
set -u
U="$HOME/Library/Application Support/Code/User"
EXT="$HOME/.vscode/extensions"
HER="$(cd "$(dirname "$0")" && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$U/settings-backup/$STAMP"
FEIL=0
UTVIDELSER=0
VALGT=""
KOMMANDO="${1:-}"
[ $# -gt 0 ] && shift

for a in "$@"; do
  case "$a" in
    --extensions) UTVIDELSER=1 ;;
    default|writing) VALGT="$VALGT $a" ;;
    *) echo "ERROR: unknown argument '$a' (see the top of this script)"; exit 1 ;;
  esac
done

# The home-made extensions each profile is to have, and the ones it is not.
EGNE_DEFAULT="tex-oppstart workspace-switcher classroom-mode"
EGNE_WRITING="tex-preambel workspace-switcher"
IKKE_DEFAULT="dagmorten.arbeidsflate dagmorten.tex-preambel dagmorten.host-theme dagmorten.hoest-theme"
IKKE_WRITING="dagmorten.arbeidsflate dagmorten.tex-oppstart dagmorten.classroom-mode dagmorten.host-theme dagmorten.hoest-theme anthropic.claude-code"

# skal NAME: true when this profile is to be handled in this run
skal() {
  [ -z "$VALGT" ] && return 0
  case " $VALGT " in *" $1 "*) return 0 ;; esac
  return 1
}

# vis PATH: the path with the home folder shortened to ~ (a tilde for the
# reader; it is printed, never used as a path)
vis() {
  local tilde='~'
  case "$1" in
    "$HOME"/*) echo "$tilde/${1#"$HOME"/}" ;;
    *) echo "$1" ;;
  esac
}

# flytt FILE: moves a file on the Mac into the backup folder
flytt() {
  local rel="${1#"$U"/}"
  mkdir -p "$(dirname "$BACKUP/$rel")" && mv "$1" "$BACKUP/$rel"
}

# avlenk FILE REPOFILE: if FILE is a symlink, replaces it with an ordinary
# file holding what the link pointed to, or REPOFILE's content if the link
# was broken.
avlenk() {
  local fil="$1" repo="$2" tmp="$1.avlenk-$STAMP"
  [ -L "$fil" ] || return 0
  if [ -e "$fil" ]; then
    cp "$fil" "$tmp" || { echo "ERROR: could not copy $(vis "$fil")"; FEIL=1; return 1; }
  else
    cp "$repo" "$tmp" || { echo "ERROR: could not copy $(vis "$repo")"; FEIL=1; return 1; }
  fi
  if flytt "$fil" && mv "$tmp" "$fil"; then
    echo "unlinked: $(vis "$fil") is an ordinary file again"
  else
    echo "ERROR: could not replace the link $(vis "$fil")"; FEIL=1; return 1
  fi
}

# modus_paa FILE: true when classroom mode is on in this settings file. The
# mode hides the squiggles by making their colour transparent, and nothing
# else sets that value.
modus_paa() {
  grep -q '"editorError.foreground"[[:space:]]*:[[:space:]]*"#00000000"' "$1" 2>/dev/null
}

# lagre MACFILE REPOFILE: copies a file from the Mac into this folder
lagre() {
  local mac="$1" repo="$2"
  avlenk "$mac" "$repo" || return 0
  if [ ! -f "$mac" ]; then echo "MISSING:  $(vis "$mac")"; FEIL=1; return 0; fi
  if cmp -s "$mac" "$repo"; then
    echo "same:     $(vis "$repo")"
  elif mkdir -p "$(dirname "$repo")" && cp "$mac" "$repo"; then
    echo "saved:    $(vis "$repo")"
  else
    echo "ERROR: could not save $(vis "$repo")"; FEIL=1
  fi
}

# gjenopprett REPOFILE MACFILE: copies a file from this folder onto the Mac
gjenopprett() {
  local repo="$1" mac="$2"
  if [ ! -f "$repo" ]; then echo "ERROR: missing in the repository: $(vis "$repo")"; FEIL=1; return 0; fi
  avlenk "$mac" "$repo" || return 0
  if [ -f "$mac" ] && cmp -s "$mac" "$repo"; then echo "same:     $(vis "$mac")"; return 0; fi
  mkdir -p "$(dirname "$mac")" || { FEIL=1; return 0; }
  if [ -e "$mac" ]; then
    flytt "$mac" || { echo "ERROR: could not move $(vis "$mac")"; FEIL=1; return 0; }
  fi
  if cp "$repo" "$mac"; then
    echo "restored: $(vis "$mac")"
  else
    echo "ERROR: could not restore $(vis "$mac")"; FEIL=1
  fi
}

# sjekk MACFILE REPOFILE: reports whether a file on the Mac is an ordinary
# file with the same content as the repository's copy
sjekk() {
  local mac="$1" repo="$2"
  if [ -L "$mac" ]; then echo "PROBLEM:  $(vis "$mac") is a symlink (run: setup.sh save)"; FEIL=1
  elif [ ! -f "$mac" ]; then echo "PROBLEM:  $(vis "$mac") is missing"; FEIL=1
  elif cmp -s "$mac" "$repo"; then echo "ok:       $(vis "$mac") is the same as the repository's copy"
  else echo "differs:  $(vis "$mac") has changed since the last save (run: setup.sh save)"; FEIL=1
  fi
}

# har_code: true when the code command is available
har_code() {
  command -v code >/dev/null && return 0
  echo "ERROR: the code command is missing. In VS Code: Shell Command: Install 'code' command in PATH."
  FEIL=1
  return 1
}

# install EXTENSION [ARGS...]: installs quietly, reports a failure without stopping
install() {
  code --install-extension "$@" >/dev/null 2>&1 || { echo "ERROR: $1"; FEIL=1; }
}

# manifest FILE: prints a package.json without whitespace and without the
# "__metadata" block. VS Code reformats the file and adds that block when it
# installs an extension, so the installed copy never equals the source byte
# for byte.
manifest() {
  sed -e '/"__metadata"[[:space:]]*:/,/^[[:space:]]*}/d' "$1" | tr -d ' \t\n' | sed -e 's/,}/}/g'
}

# profiler: prints the names of the profiles other than Default, one per line
profiler() {
  [ -f "$U/globalStorage/storage.json" ] || return 0
  python3 -c "import json,sys
for p in json.load(open(sys.argv[1])).get('userDataProfiles',[]): print(p['name'])" "$U/globalStorage/storage.json"
}

# finn_profil NAME: prints the folder id of a named profile, or nothing
finn_profil() {
  [ -f "$U/globalStorage/storage.json" ] || return 0
  python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(next((p['location'] for p in d.get('userDataProfiles',[]) if p['name']==sys.argv[2]),''))" "$U/globalStorage/storage.json" "$1"
}

# vsix_ok NAME: true when the .vsix in this folder holds the same extension.js
# and package.json as the source files beside it
vsix_ok() {
  python3 -c "import sys,zipfile
d=sys.argv[1]; z=zipfile.ZipFile(d+'/'+sys.argv[2]+'-1.0.0.vsix')
for f in ('extension.js','package.json'):
    if z.read('extension/'+f)!=open(d+'/'+f,'rb').read(): sys.exit(1)" "$HER/$1" "$1" 2>/dev/null
}

# sjekk_utvidelser LABEL LISTED WANTED UNWANTED: compares the extensions a
# profile has with the home-made ones it should and should not have
sjekk_utvidelser() {
  local navn="$1" har="$2" e
  for e in $3; do
    if echo "$har" | grep -qx "dagmorten.$e"; then echo "ok:       $navn has $e"
    else echo "PROBLEM:  $navn lacks $e (run: setup.sh restore --extensions)"; FEIL=1
    fi
  done
  for e in $4; do
    if echo "$har" | grep -qx "$e"; then echo "PROBLEM:  $navn has $e, which does not belong there"; FEIL=1; fi
  done
}

case "$KOMMANDO" in
  check)
    # 1. the copies in this folder
    for e in tex-oppstart tex-preambel workspace-switcher classroom-mode; do
      if vsix_ok "$e"; then echo "ok:       $e.vsix matches its source"
      else echo "PROBLEM:  $e: the .vsix does not match extension.js and package.json beside it"; FEIL=1
      fi
    done
    # 2. profiles
    ANDRE="$(profiler)"
    if [ "$ANDRE" = "Writing" ]; then echo "ok:       the profiles are Default and Writing"
    else echo "PROBLEM:  the profiles besides Default should be Writing only, but are: $(echo "$ANDRE" | tr '\n' ' ')"; FEIL=1
    fi
    # 3. settings files
    if modus_paa "$U/settings.json"; then
      echo "note:     classroom mode is on, so the Default settings were not compared; turn it off before setup.sh save"
    else
      sjekk "$U/settings.json" "$HER/default/settings.json"
    fi
    sjekk "$U/keybindings.json" "$HER/keybindings.json"
    ID="$(finn_profil Writing)"
    if [ -n "$ID" ]; then
      sjekk "$U/profiles/$ID/settings.json" "$HER/writing/settings.json"
      [ -L "$U/profiles/$ID/keybindings.json" ] && { echo "PROBLEM:  $(vis "$U/profiles/$ID/keybindings.json") is a symlink (run: setup.sh save)"; FEIL=1; }
    fi
    # 4. extensions
    if command -v code >/dev/null; then
      sjekk_utvidelser Default "$(code --list-extensions 2>/dev/null)" "$EGNE_DEFAULT" "$IKKE_DEFAULT"
      if [ -n "$ID" ]; then
        sjekk_utvidelser Writing "$(code --list-extensions --profile Writing 2>/dev/null)" "$EGNE_WRITING" "$IKKE_WRITING"
      fi
      for e in tex-oppstart tex-preambel workspace-switcher classroom-mode; do
        if [ -f "$EXT/dagmorten.$e-1.0.0/extension.js" ]; then
          if cmp -s "$EXT/dagmorten.$e-1.0.0/extension.js" "$HER/$e/extension.js" && [ "$(manifest "$EXT/dagmorten.$e-1.0.0/package.json")" = "$(manifest "$HER/$e/package.json")" ]; then
            echo "ok:       the installed $e is the version in the repository"
          else
            echo "PROBLEM:  the installed $e is not the version in the repository (run: setup.sh restore --extensions)"; FEIL=1
          fi
        fi
      done
    else
      echo "note:     the code command is missing, so the extensions were not checked"
    fi
    # 5. leftovers
    for f in "$U"/settings.before-fix.json "$U"/*.backup-*.json "$U"/*.avlenk-* "$U"/profiles/*/*.backup-*.json; do
      [ -e "$f" ] && echo "note:     leftover file, safe to delete: $(vis "$f")"
    done
    [ -d "$U/settings-backup" ] && echo "note:     earlier settings are kept in $(vis "$U/settings-backup"); delete the folder when they are no longer needed"
    [ "$FEIL" = 0 ] && echo "Everything is as it should be."
    ;;
  save)
    if skal default; then
      if modus_paa "$U/settings.json"; then
        echo "ERROR: classroom mode is on. Turn it off in VS Code first, so its settings are not saved as the Default profile's."
        FEIL=1
      else
        lagre "$U/settings.json" "$HER/default/settings.json"
      fi
      lagre "$U/keybindings.json" "$HER/keybindings.json"
      if command -v code >/dev/null; then
        # The home-made extensions (publisher dagmorten) are not on the
        # Marketplace and are installed from this folder, so they are left out.
        if code --list-extensions 2>/dev/null | grep -v '^dagmorten\.' > "$HER/extensions.txt.ny" && [ -s "$HER/extensions.txt.ny" ]; then
          mv "$HER/extensions.txt.ny" "$HER/extensions.txt" && echo "saved:    $(vis "$HER/extensions.txt")"
        else
          echo "ERROR: could not list the extensions"; FEIL=1
        fi
      fi
    fi
    if skal writing; then
      ID="$(finn_profil Writing)"
      if [ -n "$ID" ]; then
        lagre "$U/profiles/$ID/settings.json" "$HER/writing/settings.json"
        # The Writing profile has the same keybindings as Default; only a link is undone here.
        avlenk "$U/profiles/$ID/keybindings.json" "$HER/keybindings.json" || true
      else
        echo "MISSING:  the Writing profile does not exist"; FEIL=1
      fi
    fi
    ;;
  restore)
    if [ "$UTVIDELSER" = 1 ]; then har_code || exit 1; fi
    if skal default; then
      gjenopprett "$HER/default/settings.json" "$U/settings.json"
      gjenopprett "$HER/keybindings.json" "$U/keybindings.json"
      if [ "$UTVIDELSER" = 1 ]; then
        # Extensions that do not belong here, or that have changed name, are
        # removed (nothing happens if they are gone): the Høst themes were
        # called host-theme before version 3.5 and had the publisher dagmorten
        # before 3.6.1, and workspace-switcher was first called arbeidsflate.
        for e in $IKKE_DEFAULT; do
          code --uninstall-extension "$e" >/dev/null 2>&1 || true
        done
        while read -r e; do
          case "$e" in ""|dagmorten.*) ;; *) install "$e" ;; esac
        done < "$HER/extensions.txt"
        for e in $EGNE_DEFAULT; do
          install "$HER/$e/$e-1.0.0.vsix" --force
        done
        echo "extensions installed: Default"
      fi
    fi
    # Writing profile: LaTeX only, without Python and without Claude Code.
    if skal writing; then
      ID="$(finn_profil Writing)"
      if [ -z "$ID" ] && har_code; then
        code --profile "Writing" --new-window >/dev/null 2>&1 || true
        for _ in $(seq 1 30); do ID="$(finn_profil Writing)"; [ -n "$ID" ] && break; sleep 1; done
      fi
      if [ -z "$ID" ]; then
        echo "ERROR: Writing profile not found. Create it in VS Code (Profiles > New Profile > Writing) and re-run."
        FEIL=1
      else
        gjenopprett "$HER/writing/settings.json" "$U/profiles/$ID/settings.json"
        gjenopprett "$HER/keybindings.json" "$U/profiles/$ID/keybindings.json"
        if [ "$UTVIDELSER" = 1 ]; then
          for e in $IKKE_WRITING; do
            code --uninstall-extension "$e" --profile "Writing" >/dev/null 2>&1 || true
          done
          for e in james-yu.latex-workshop dagmortensj.hoest-theme \
                   streetsidesoftware.code-spell-checker streetsidesoftware.code-spell-checker-norwegian-bokmal; do
            install "$e" --profile "Writing" --force
          done
          for e in $EGNE_WRITING; do
            install "$HER/$e/$e-1.0.0.vsix" --profile "Writing" --force
          done
          echo "extensions installed: Writing"
        fi
      fi
    fi
    ;;
  *)
    echo "Usage: setup.sh check | save | restore [--extensions]   (see the top of this script)"
    exit 1
    ;;
esac

exit "$FEIL"
