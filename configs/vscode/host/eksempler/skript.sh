#!/bin/bash
# Bygger alle dokumentene stille
set -euo pipefail
MAPPE="${1:-$HOME/Developer}"
for d in "$MAPPE"/*/; do
    if [[ -f "$d/main.tex" ]]; then
        (cd "$d" && latexmk -lualatex -interaction=nonstopmode main >/dev/null && echo "OK: $d")
    fi
done
antall=$(ls | wc -l)
echo "Ferdig med $antall filer" | tee -a logg.txt
export PATH="/opt/homebrew/bin:$PATH"
