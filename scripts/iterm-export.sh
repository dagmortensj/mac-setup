#!/bin/bash
# Saves iTerm2's current settings to configs/iterm2/com.googlecode.iterm2.plist,
# the file install.sh imports on a new Mac. Run it after changing something in
# iTerm2 that you want to keep, then commit the result.
#
# Keys that change on their own (window positions, update checks, run counters,
# everything iTerm2 marks NoSync) are left out, so the file only changes when a
# setting does. The file is written as sorted XML so that git diff is readable.
#
# iTerm2 hands every change to macOS straight away, so this can run while
# iTerm2 is open.
set -eu

REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$REPO/configs/iterm2/com.googlecode.iterm2.plist"
TMP="$(mktemp "${TMPDIR:-/tmp}/iterm-export.XXXXXX")"
trap 'rm -f "$TMP"' EXIT

if ! defaults export com.googlecode.iterm2 "$TMP" 2>/dev/null; then
  echo "FAIL: no iTerm2 settings found (has iTerm2 been opened on this Mac?)"
  exit 1
fi

/usr/bin/python3 - "$TMP" "$OUT" <<'PY'
import plistlib, sys

src, out = sys.argv[1], sys.argv[2]
with open(src, "rb") as f:
    prefs = plistlib.load(f)

# Prefixes and keys that iTerm2 or macOS rewrite by themselves.
VOLATILE_PREFIXES = (
    "NoSync",                    # iTerm2's own "never sync" bookkeeping
    "NSWindow Frame",            # window positions
    "NSSplitView",
    "NSNavPanel",                # open/save panel sizes
    "NSToolbar Configuration",
    "kCPK",                      # colour picker state
)
VOLATILE_KEYS = {
    "NSOSPLastRootDirectory",
    "SULastCheckTime",           # Sparkle update checks
    "SUUpdateRelaunchingMarker",
    "SUUpdateGroupIdentifier",
    "SUFeedURL",
    "iTerm Version",
    "LoadPrefsFromCustomFolder", # settings are imported, not read from a folder
    "PrefsCustomFolder",
}

kept = {k: v for k, v in prefs.items()
        if k not in VOLATILE_KEYS and not k.startswith(VOLATILE_PREFIXES)}

with open(out, "wb") as f:
    plistlib.dump(kept, f, fmt=plistlib.FMT_XML, sort_keys=True)
print(f"OK: {len(kept)} settings saved, {len(prefs) - len(kept)} volatile keys left out")
PY
