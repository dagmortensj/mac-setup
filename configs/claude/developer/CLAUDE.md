# Kontekst for Dag-Morten — `~/Developer`

Dette er hovedinstruksene for alt arbeid i `~/Developer`. Hvert repo kan ha sin egen `CLAUDE.md` med det som gjelder bare der — les den også før du rører repoet. GitHub-brukeren er **dagmortensj**.

Stil: konsis og direkte. Snakk norsk med Dag-Morten. Dokumentasjon, commit-meldinger og README i repoene er på engelsk der de allerede er det.

## Arbeidsflyt: rett i repoene

Jobb **direkte i `~/Developer/<repo>`** med `device_bash`. Det finnes ingen arbeidskopier som skal synkes, og ingen rsync-flyt. Den gamle mellomstasjonen `claude-cowork/` er avviklet og arkivert i `Dropbox/arkiv/claude-cowork/`; ikke gjenopprett den.

Det som ikke er repoer, ligger i Dropbox: undervisningen i `Dropbox/jobb-vgs/<fag>/` (hver fagmappe har sin egen `CLAUDE.md`), skriveprosjektene i `Dropbox/prosjekter/fysikk/` og `Dropbox/prosjekter/matematikk/`, og Behiel-notatene i `Dropbox/artikler/fysikk/behiel/`.

Repoer i dag:

| Repo | Hva |
|---|---|
| `lualatex-templates` | LaTeX-maler for LuaLaTeX (OpenType-fonter, `unicode-math`); egen `CLAUDE.md` |
| `pdflatex-templates` | Samme malsett for pdflatex |
| `hoest-theme` | Fargetema for VS Code og iTerm; egen `CLAUDE.md` |
| `mac-setup` | Oppsettet for Macen: `install.sh`, Brewfiles, dotfiles (lenket inn i hjemmemappa), Python-standardmiljøet, iTerm-innstillinger, alle `CLAUDE.md`-filene, og `scripts/unwrap-tex.py`; egen `CLAUDE.md` |
| `physics/schroedinger` | Simulering av den tidsavhengige Schrödinger-ligningen (1D og 2D), remote `olympia-academy/schroedinger`; eget uv-prosjekt |

## ⚠️ Dag-Mortens egne endringer skal aldri overskrives

Dag-Morten redigerer filene selv mellom promptene. Disse endringene er hans, og de skal overleve neste ting du gjør.

- **Les fila på nytt før du skriver.** Hent alltid gjeldende innhold fra disk før du endrer. Det du husker fra forrige tur, kan være utdatert.
- **Rediger på stedet, aldri ved å skrive fila om igjen fra et tidligere tool-resultat** (som kan være avkortet). Bruk `sed -i`, `python3` read-modify-write eller tilsvarende.
- **Aldri `force: true` i `device_commit_files`.** Send `expectedMtimeMs` fra siste staging. Blir skrivingen avvist, hent fila på nytt, flett, skriv igjen.
- **Endre bare det prompten faktisk handler om.** Alt annet han har rørt, står urørt, også når din egen versjon var «penere».
- **Ikke rydd opp uoppfordret.** Formatering, kommentarer, navn og småjusteringer han har lagt inn, er bevisste valg til det motsatte er sagt.
- Er du i tvil om en forskjell kommer fra ham eller fra deg: spør. Ikke gjett.

## Git: Dag-Morten committer og pusher selv

**`CLAUDE.md` committes ikke i prosjektrepoene.** Originalene ligger i mac-setup: `configs/claude/developer/CLAUDE.md` (denne fila) og `configs/claude/<repo>/CLAUDE.md`. `~/Developer/CLAUDE.md` og hvert repos `CLAUDE.md` er lenker dit, og `CLAUDE.md` står i repoets `.git/info/exclude`. Rediger gjennom lenken som vanlig; endringen havner i mac-setup, og Dag-Morten committer den der. En ny `CLAUDE.md` for et repo lages i `mac-setup/configs/claude/<repo>/`, og `./install.sh repos` lenker den på plass.

**Kjør aldri `git add`, `git commit` eller `git push` for ham**, og ikke spør av deg selv om han vil committe. `git status`, `git diff` og `git log` kan du bruke fritt for å orientere deg. Når han ber om terminal, gir du **bare terminalkode** i en `bash`-blokk, ikke prosa rundt. Han limer den inn i iTerm på Macen.

Rekkefølgen for malrepoene er alltid **bygg → paritet → status → commit → push**, alt i `~/Developer/<repo>`. Detaljer i repoets egen `CLAUDE.md`.

## Python

Små skript og notatbøker kjøres i standardmiljøet `~/.venvs/standard` (uv, Python 3.13, definert i `mac-setup/configs/python/`). Det ligger først i PATH, så `python3` er det miljøet. Nye pakker legges til med `pyadd <pakke>` (fjernes med `pyremove`), som oppdaterer pakkelista og `uv.lock` i mac-setup; aldri `pip install`. Prosjekter med egne avhengigheter, som `schroedinger`, har sitt eget uv-prosjekt (`uv sync`).

## Begrensninger i `device_bash`

- Filer som heter `.zshrc` eller `.zprofile` kan ikke leses, heller ikke i repoet (`Permission denied`). Bruk `git -C ~/Developer/mac-setup show HEAD:configs/zsh/.zshrc` for å lese den committede versjonen, og be Dag-Morten om terminalkode hvis fila må endres.
- Sletting (`rm`, `mv` ut av en mappe) krever at han godkjenner det først.

## LaTeX-dokumenter skrevet med malene

Følg malens konvensjoner (repoets `README.md` og hver mals egen `README.md`).

**Overføring av gammelt dokument til ny mal:** kopier alltid over en **ren kopi av den nye malen** (main + sty + alt), og flytt det gamle *innholdet* inn i den. Aldri motsatt vei. Ikke alle malens miljøer trengs — vurder ut fra det gamle dokumentet, og **fjern ubrukt boilerplate** fra malens `main`.

**Linjeskift i .tex-filer:** **ett avsnitt per linje**, uten harde linjeskift inne i avsnittet. Dag-Morten har myk linjebryting i VS Code. Matematikkmiljøer, lister (`\item` på egen linje) og kode skrives som før. Gamle filer rettes med `~/Developer/mac-setup/scripts/unwrap-tex.py`.

**Vektorer med pil:** begge malsettene definerer `\vv` i stilfila, så last ikke `esvect`. Skriv `\vv{F}` med indeksen utenfor pila (`\vv{F}_1`, aldri `\vv{F_1}`), og `\overrightarrow{AB}` over flere symboler. Ikke `\vec`.

**Display-matte:** aldri `\tfrac` i align eller frittstående ligninger — alltid `\frac` der.

**Fasit og løsningsforslag i fysikk:** finn symbolsk formel først, sett inn tall helt til slutt. Ingen mellomregninger med tallverdier.

**Norsk fysikkprosa:** aldri «regnestykke» — bruk «utledning», «beregning» eller «regning». «Hastighet» er vektoren, «fart» er størrelsen.

## Kompilering

Engine følger repoet: **pdflatex** i `pdflatex-templates`, **lualatex** i `lualatex-templates` — der alltid via `latexmk -lualatex`, aldri ren `lualatex` (notat og bok trenger biber). Hver malmappe har en `.latexmkrc` som velger motor, så `latexmk main` fungerer også.

Tre maskiner, ulik evne til å bygge:

- **MacTeX på Macen er fasit** (installert med Homebrew som `mactex-no-gui`, årets TeX Live) for endelige PDF-er. Dag-Morten bygger der selv. **Terminalkommandoer for bygg skal være stille:** det eneste han vil se i terminalen, er én `OK: <mappe>`-linje per dokument når bygget er ferdig. Aldri latexmk-loggen, aldri innholdet i det som bygges. Send derfor både stdout og stderr til `/dev/null` — `>/dev/null 2>&1`, ikke bare `>/dev/null` — og la feil vises som manglende `OK`-linje, ikke som logg. Mal:

  ```bash
  (cd "$d" && latexmk -pdf -interaction=nonstopmode main >/dev/null 2>&1 && echo "OK: $d")
  ```
- **Den lokale Linux-VM-en bak `device_bash` kan ikke bygge malene** — den mangler `luaotfload`, norsk babel og fontene (verifisert). Ikke prøv.
- **Sandboxen (cloud) kan bygge** når filene stages dit. Du er root og har nett; TeX Live 2023 er minimalt, så installer per økt:

```
apt-get install -y texlive-lang-european texlive-fonts-extra lmodern
apt-get install -y texlive-luatex texlive-latex-extra texlive-bibtex-extra biber
```

Installasjonen er flyktig og må gjentas i hver ny økt. Bruk sandbox-bygg til å **verifisere** at endringer kompilerer (render til PNG og se på resultatet), ikke til å produsere `main.pdf` som skal inn i repoet — det gjør Macen.
