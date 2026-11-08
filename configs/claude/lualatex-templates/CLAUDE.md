# Kontekst for Dag-Morten — `lualatex-templates`

Les `~/Developer/CLAUDE.md` først; dette er tillegget som gjelder bare dette repoet. **Denne fila skal aldri inn i repoet** — den står i `.git/info/exclude` og er lokal. Repoet er offentlig på `github.com/dagmortensj/lualatex-templates`. README, kommentarer i stilfilene og commit-meldinger er på engelsk; i `no/` er kommentarer og plassholdertekst på norsk.

## Hva repoet er

Seks maler, hver i `en/` og `no/`, tolv mapper i alt:

| `en/` | `no/` | Stilfil |
|---|---|---|
| `book` | `bok` | `bookstyle.sty` / `bokstil.sty` |
| `ffv` | `ffv` | `ffvstyle.sty` / `ffvstil.sty` |
| `notes` | `notat` | `notesstyle.sty` / `notatstil.sty` |
| `handout` | `handout` | `handoutstyle.sty` (samme navn i begge) |
| `exam` | `prove` | `examstyle.sty` / `provestil.sty` |
| `formulasheet` | `formelark` | `formulasheetstyle.sty` / `formelarkstil.sty` |

Hver mappe har `main.tex`, stilfila (all formatering ligger der), `README.md`, `.latexmkrc` og en bundlet `main.pdf` som viser resultatet. `book`, `ffv` og `notes` har `.bib`; `book`, `notes` og `handout` har `figures/` (`figurer/`). `main.pdf` er **ikke** gitignorert — den er en del av repoet og skal være fersk ved commit.

Søsterrepoet `pdflatex-templates` har samme malsett for pdflatex. En endring i layout eller funksjonalitet skal normalt inn i begge, i hver sin pakkedialekt; en endring som bare gjelder `unicode-math`/OpenType, hører bare hjemme her.

## Regler som følger av `unicode-math`

- **Fet matte er `\symbf` / `\symbfit` / `\symbfup`**, aldri `\bm`, aldri `\boldmath`.
- **Ikke last `amssymb`** — bryter bygget. **Ikke last `mathtools`** — gir unicode-math-varsler; `physics2` (`ab.legacy`), `tensor` og unicode-math sin egen `\coloneq` dekker behovet.
- **Ikke last `esvect`** — stilfilene definerer `\vv` selv, og setter `\mathitalicsmode=1`.
- Fonter per mal står i README (Garamond Libre, STIX Two, NewCM). Bytt ikke font uten at det er poenget med prompten.
- En pdflatex-pakke kan eller kan ikke fungere her. Hver mals README har en tabell over hva som er sjekket — oppdater den når du prøver noe nytt.

## Paritet mellom `en/` og `no/`

De to utgavene skal avvike **bare i språkstrenger, filnavn og kommentarer**. Alt annet er drift.

- Endrer du en stilfil eller `main.tex` i én utgave, gjør **samme endring i den andre** i samme tur. Norske kommandonavn følger den eksisterende ordboka (`\del`/`\exampart`, `\nivå`/`\level`, `halvdel`/`half`, `tett`/`tight` osv. — hele listen står i `tools/parity-diff.sh`).
- Kjør alltid `tools/parity-diff.sh` fra repo-rota etterpå. Skriptets header lister de få legitime restavvikene (siunitx-lokalisering, `\providecommand`-vakter, synlige strenger i `exam` og `formulasheet`). Alt annet skal bort før du er ferdig.
- Innfører du et nytt norsk identifikatornavn, legg mappingen inn i `map()` i `tools/parity-diff.sh` — lengre navn først, så ikke et kortere spiser midten av et lengre.

## Bygg og verifisering

- Alltid `latexmk -lualatex -interaction=nonstopmode main` (eller bare `latexmk main`, `.latexmkrc` velger motoren). Aldri ren `lualatex`: `notes` og `book` trenger biber, `exam` trenger et pass til for «Side 2 av 5».
- **Alle tolv skal bygge uten warnings.** Det er standarden repoet lover i README; sjekk `main.log` for `Warning` etter en endring, ikke bare om PDF-en kom ut.
- `exam` har pakkevalgene `coverpage`, `booklet`, `statuscheck` (`forside`, `hefte`, `statussjekk`); `formulasheet` har `tight` (`tett`). En endring i disse stilfilene må prøves med hvert valg, ikke bare standard.
- Bygg skjer på Macen (Dag-Morten) eller i sandboxen (verifisering), aldri i `device_bash`-VM-en — se hovedfila.

## Terminal for Dag-Morten

Når han ber om terminal etter en endring: bygg de berørte malene, paritet, `git status`, så commit og push — i den rekkefølgen, i repoet. Bytt `handout` med malene som er endret:

```bash
cd ~/Developer/lualatex-templates
for d in no/handout en/handout; do
  (cd "$d" && latexmk -lualatex -interaction=nonstopmode main >/dev/null 2>&1 && echo "OK: $d")
done
tools/parity-diff.sh
git status      # bare de ventede filene — ellers stopp
git add -A && git commit -m "..." && git push
```

Er `pdflatex-templates` også endret, samme blokk der med `latexmk -pdf`.

## Dokumentasjon følger koden

En endring i hva en mal gjør, skal også inn i malens `README.md` (begge språk) og, om den er synlig fra repo-rota, i hoved-`README.md`. Oppdater `.gitignore`-kommentarene om du innfører nye byggeartefakter.
