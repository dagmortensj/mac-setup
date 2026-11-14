#!/bin/bash
# Makes TeX Live's biber an ARM-only program.
#
#   scripts/biber-arm64.sh            replace the universal biber with its arm64 part
#   scripts/biber-arm64.sh --dry-run  show what would happen, change nothing
#
# MacTeX ships biber as a universal binary (x86_64 and arm64). On its first
# run, and whenever its unpacked copy in the temporary folder has been cleared,
# biber calls lipo to cut out the part for this Mac's processor. That call
# can fail, and then biber stops before it has read anything ("extracting
# arm64 binary with lipo failed"), so every document with biblatex loses its
# bibliography. This script cuts out the arm64 part once, with the lipo from
# the Command Line Tools, checks that it runs, and puts it in place of the
# universal file. biber then has nothing left to unpack, and the version stays
# the one TeX Live ships, which is the one its biblatex expects.
#
# Run it again after `tlmgr update` has updated biber and after a new TeX Live
# year: both bring the universal file back. When biber is already ARM-only it
# says so and changes nothing. install.sh runs it in the dev group.
#
# The universal original is kept in ~/.mac-setup-backup/<date>/. Replacing the
# file needs the admin password (TeX Live belongs to root). Run from a
# terminal, the script asks for it; run without one, it stops and says so.
#
# Exit codes: 0 replaced (or nothing to do in a dry run), 10 already ARM-only,
# 3 skipped (no MacTeX, not Apple Silicon, no admin rights), 1 failed.
#
# Written for the bash 3.2 that ships with macOS.

set -u
set -o pipefail

DRY=0
case "${1:-}" in
  --dry-run) DRY=1 ;;
  "") ;;
  -h|--help) sed -n '2,5p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  *) echo "Unknown option: $1"; exit 2 ;;
esac

LIPO=/usr/bin/lipo
TEXBIN_BIBER=/Library/TeX/texbin/biber
STAMP="$(date +%Y-%m-%d-%H%M%S)"
BACKUP="$HOME/.mac-setup-backup/$STAMP"
LOG_DIR="$HOME/Library/Logs/mac-setup"
LOG="$LOG_DIR/biber-arm64-$STAMP.log"

mkdir -p "$LOG_DIR" || { echo "FAIL  cannot create $LOG_DIR"; exit 1; }
echo "biber-arm64.sh, $STAMP, dry-run: $DRY" >"$LOG"

# say STATUS TEXT: one line on the terminal, the same line in the log.
say() {
  printf '%-4s  %s\n' "$1" "$2"
  printf '%s: %s\n' "$1" "$2" >>"$LOG"
}

# version FILE: biber's version number, or nothing if the file does not run.
version() {
  "$1" --version 2>>"$LOG" | sed -n 's/^biber version: *//p' | head -n 1
}

if [ "$(uname -m)" != "arm64" ]; then
  say SKIP "not an Apple Silicon Mac; the universal biber is the right one here"
  exit 3
fi
if [ ! -e "$TEXBIN_BIBER" ]; then
  say SKIP "no TeX Live biber at $TEXBIN_BIBER (is MacTeX installed?)"
  exit 3
fi
if [ ! -x "$LIPO" ] || ! xcode-select -p >/dev/null 2>&1; then
  say FAIL "lipo is missing: install the Command Line Tools (xcode-select --install)"
  exit 1
fi

# The real file behind /Library/TeX/texbin, for example
# /usr/local/texlive/2026/bin/universal-darwin/biber.
BIBER="$(readlink -f "$TEXBIN_BIBER" 2>>"$LOG")"
if [ -z "$BIBER" ] || [ ! -f "$BIBER" ]; then
  say FAIL "cannot resolve $TEXBIN_BIBER to a file"
  exit 1
fi
echo "biber: $BIBER" >>"$LOG"

ARCHS="$("$LIPO" -archs "$BIBER" 2>>"$LOG")"
echo "architectures: $ARCHS" >>"$LOG"
case " $ARCHS " in
  " arm64 ")
    say OK "biber $(version "$BIBER") is already ARM-only"
    exit 10
    ;;
  *" arm64 "*) ;;
  *)
    say FAIL "$BIBER has no arm64 part (architectures: ${ARCHS:-unknown})"
    exit 1
    ;;
esac

if [ "$DRY" = 1 ]; then
  say OK "would replace $BIBER ($ARCHS) with its arm64 part, keeping the original in ~/.mac-setup-backup/"
  exit 0
fi

# Admin rights: reuse a valid sudo session; otherwise ask, but only when there
# is a terminal to ask in.
if ! sudo -n true 2>/dev/null; then
  if [ -t 0 ]; then
    echo "Your Mac password, to replace biber in TeX Live:"
    sudo -v || { say FAIL "no admin password given"; exit 1; }
  else
    say SKIP "needs the admin password: run scripts/biber-arm64.sh in a terminal"
    exit 3
  fi
fi

mkdir -p "$BACKUP" || { say FAIL "cannot create $BACKUP"; exit 1; }
cp -p "$BIBER" "$BACKUP/biber.universal" 2>>"$LOG" \
  || { say FAIL "cannot copy $BIBER to the backup folder"; exit 1; }

# Cut out the arm64 part next to the backup and check it before it goes in.
THIN="$BACKUP/biber.arm64"
"$LIPO" -thin arm64 "$BIBER" -output "$THIN" >>"$LOG" 2>&1 \
  || { say FAIL "lipo could not cut out the arm64 part (see $LOG)"; exit 1; }
if [ "$("$LIPO" -archs "$THIN" 2>>"$LOG")" != "arm64" ]; then
  say FAIL "the cut-out file is not arm64-only; nothing was replaced"
  exit 1
fi
NEW="$(version "$THIN")"
if [ -z "$NEW" ]; then
  say FAIL "the arm64 biber does not run; nothing was replaced (see $LOG)"
  exit 1
fi

# The redirect is meant to run as the user: the log is the user's file.
# shellcheck disable=SC2024
sudo install -m 755 "$THIN" "$BIBER" >>"$LOG" 2>&1 \
  || { say FAIL "could not replace $BIBER; the original is unchanged"; exit 1; }

if [ "$("$LIPO" -archs "$BIBER" 2>>"$LOG")" != "arm64" ] || [ "$(version "$BIBER")" != "$NEW" ]; then
  say FAIL "biber was replaced but does not answer as expected; the original is in $BACKUP"
  exit 1
fi

say OK "biber $NEW is now ARM-only; the universal original is in ~/.mac-setup-backup/$STAMP/"
exit 0
