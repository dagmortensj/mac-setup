# Kontekst for Dag-Morten — Høst

Høst er et lyst (**Høstlys**) og et mørkt (**Høstkveld**) fargetema for VS Code og iTerm. Repoet ligger i `~/Developer/hoest-theme`, GitHub-brukeren er **dagmortensj** (`github.com/dagmortensj/hoest-theme`). Utvidelsen er publisert på VS Code Marketplace siden 1. november 2026 som **Høst Theme**, ID `dagmortensj.hoest-theme` (første versjon der: 3.10.0). Les denne fila før du rører noe i repoet.

Stil: konsis og direkte. Snakk norsk med Dag-Morten. Dokumentasjon, commit-meldinger og CHANGELOG i repoet er på engelsk, slik det allerede står.

## ⚠️ Dag-Mortens egne endringer skal aldri overskrives

Dag-Morten redigerer filene selv mellom promptene. Disse endringene er hans, og de skal overleve neste ting du gjør.

- **Les fila på nytt før du skriver.** Jobb direkte i mappa (`device_bash`), og hent alltid gjeldende innhold fra disk før du endrer. Det du husker fra forrige tur, kan være utdatert.
- **Rediger på stedet, aldri ved å skrive fila om igjen fra et tidligere tool-resultat** (som kan være avkortet). Bruk `sed -i`, `python3` read-modify-write eller tilsvarende.
- **Aldri `force: true` i `device_commit_files`.** Send `expectedMtimeMs` fra siste staging. Blir skrivingen avvist, hent fila på nytt, flett, skriv igjen.
- **Endre bare det prompten faktisk handler om.** Alt annet han har rørt, står urørt, også når din egen versjon var «penere».
- **Ikke rydd opp uoppfordret.** Formatering, kommentarer, navn og småjusteringer han har lagt inn, er bevisste valg til det motsatte er sagt.
- Er du i tvil om en forskjell kommer fra ham eller fra deg: spør. Ikke gjett.

## Git: Dag-Morten committer og pusher selv

**Kjør aldri `git add`, `git commit` eller `git push` for ham**, og ikke spør av deg selv om han vil committe. Når han ber om terminal, gir du **bare terminalkode** i en `bash`-blokk (fargekodet), ikke prosa rundt. Han limer den inn i iTerm på Macen.

Mal:

```bash
cd ~/Developer/hoest-theme
git status      # skal bare vise de ventede filene — ellers stopp
git add -A && git commit -m "Short subject in English" && git push
```

- Commit-meldinger på engelsk, i samme stil som loggen (`git log --oneline`): kort emnelinje, versjonsnummer først når en versjon slippes («3.6.0: colours follow written rules in every language»).
- Én commit per sammenhengende endring. Blir det flere ting (f.eks. ny versjon og nye skjermbilder), gi to commit-linjer.
- Ikke bruk `git` i `device_bash` til annet enn å lese (`git status`, `git diff`, `git log`). VM-en kan ikke slette filer, så `commit`, `checkout` og `stash` der etterlater låsefiler i `.git`.

## Slik henger repoet sammen

| Sti | Innhold |
|---|---|
| `src/palette.py` | **Eneste sted hex-koder finnes.** Høstkveld avledes fra Høstlys med én regel i OKLCH. Tekstfargen og gråtonene er ikke hex, men avledes av bakgrunnen og oransje (`_neutrals`, siden 3.9.0): tekst har bakgrunnens tone, gråtonene tonen midt mellom oransje og bakgrunnen. Ingen Gruvbox-verdier igjen; ikke nevn Gruvbox i dokumentasjonen. Flatene i begge temaene er en stige fra bakgrunnen (`BACKGROUND`, `SURFACES`, `WHITES`, siden 3.10.0). |
| `src/build.py` | Lager `vscode/themes/*.json`, `iterm/*.itermcolors`, `docs/palette.svg`, `docs/roles.svg` og `docs/roles.png` fra paletten. Fargene i koden navngis etter rolle (`"red"`, `"selection"`), aldri hex. |
| `src/colorspace.py` | OKLCH, sRGB-gamut, WCAG-kontrast |
| `src/icon.py` | Tegner ikonet fra paletten (trenger Pillow). Tre blad: oransje, rust, grønn. Står fast. |
| `src/banner.py` | Tegner `docs/loevfall.png` (seks blad, malen) og `docs/banner.png` (Løvfall i Høstkveld til venstre, speilet i Høstlys til høyre med rust og oransje byttet) fra paletten og `icon.py` sine bladformer |
| `vscode/` | Utvidelsen: temaer, injection-grammatikker for LaTeX og for sammensatte tilordninger (`+=`) i flere språk, statuslinjeknappen (`extension.js`), ikon, CHANGELOG og pakka `hoest-theme.vsix` |
| `iterm/` | iTerm-presetene |
| `docs/rules.md` | **Spesifikasjonen**: hvilken rolle hver farge har, fet og kursiv, og unntakene der grammatikken setter grenser |
| `docs/palette.md` | Alle farger med kontrast, regelen for Høstkveld, terminalfargene |
| `examples/` | Realistiske filer til skjermbildene |
| `test/` | Én fil per språk, rundt 60 linjer (vanlige konstruksjoner først, så en blokk «Vanskelige tilfeller»), til å sjekke reglene etter en endring |

**Generert, aldri rediger for hånd:** `vscode/themes/`, `iterm/`, `docs/palette.svg`, `docs/roles.svg`, `docs/roles.png`, `vscode/icon.png`, `docs/loevfall.png`, `docs/banner.png`. Endre paletten eller `build.py` i stedet.

`hoest-theme.vsix` er med i repoet med vilje (README lenker til den for VSCodium/Cursor), så ny pakke skal committes.

## Fargereglene er lov

`docs/rules.md` er spesifikasjonen, og `build.py` følger den. Når et nytt språk eller en ny grammatikk legges til, får hvert token farge ved å spørre **hvilken rolle det har**, aldri etter hva som ser bra ut i én fil. Kort:

- **Strukturfarge, fet**: landemerker — definisjoner og kontrollflyt, `\begin`/`\end`, `\section`
- **Strukturfarge**: resten av grammatikken — `const`, `import`, `public`, HTML-tagger, preamble
- **Verdifarge**: verdier og input — tall, `True`/`None`, parametere (kursiv)
- Strukturfargen er den sterkeste av de to varme mot bakgrunnen: **rust i Høstlys, oransje i Høstkveld**; verdifargen er den andre. I koden heter rollene `structure` og `value` (satt per tema i `_roles` i `palette.py`); bruk aldri `rust`/`orange` i tokenregler. Terminalplassene følger ikke: gul er alltid oransje, cyan alltid rust.
- **Grønn**: verktøy — funksjoner, innebygde typer, CSS-egenskaper, miljønavn, `\draw`
- **Blå**: tekst og matematikk — strenger, alt i `$...$`
- **Plomme**: det du selv navnga, og symboler — egne klasser, `self` (kursiv), dekoratorer, nøkler, `\n`, `\gamma`
- **Rød**: signaler og referanser — `\ref`, `\cite`, lenker, feil (aldri `\section`)
- **Tekstfarge**: variabler, operatorer, `\frac`, `\label`
- Fet bare for landemerker. Kursiv bare for plassholdere (og kommentarer).

Foreslår du en endring som bryter reglene, si det eksplisitt og la ham avgjøre. Får en grammatikk ikke skilt to roller, følg grammatikken og **før unntaket inn i lista i `rules.md`** i stedet for å skjule det.

## Arbeidsflyt ved endring

Rekkefølgen er **bygg → versjon → pakke → test → commit**. Bygg og pakking kan du kjøre selv i `device_bash` (python3, node og npx finnes der); installasjon i VS Code og commit gjør Dag-Morten på Macen.

1. Endre `src/palette.py` eller `src/build.py` (eller en grammatikk i `vscode/syntaxes/`).
2. `python3 src/build.py --check` fra repo-rota. Stopper bygget på en farge utenfor sRGB, sier det hva som skal inn i `OUT_OF_GAMUT`. Ikke legg det inn uten å si fra.
3. Endret en hex-kode seg: oppdater tabellene i `docs/palette.md` (hex og kontrast fra `--check`).
4. Endret en regel seg: oppdater `docs/rules.md`, og README-tabellen om rollen er beskrevet der.
5. Hev `version` i `vscode/package.json` (semver: patch for fiks, minor for nye regler/språk) og legg til en seksjon øverst i `vscode/CHANGELOG.md` med dagens dato, i samme stil som de forrige.
6. Pakk: `cd vscode && npx @vscode/vsce package -o hoest-theme.vsix`.
7. Terminalkode til Dag-Morten for install og commit:

```bash
cd ~/Developer/hoest-theme
code --install-extension vscode/hoest-theme.vsix --force
# Reload Window i VS Code, sjekk test/<språk> i Høstkveld og noen i Høstlys
git status
git add -A && git commit -m "3.6.1: ..." && git push
```

8. Publisering, etter push: Dag-Morten laster opp den nye `vscode/hoest-theme.vsix` selv i nettleseren på `marketplace.visualstudio.com/manage/publishers/dagmortensj` (ingen token, ikke `vsce publish`). Marketplace tar ikke samme versjonsnummer to ganger, og teksten der (beskrivelse, README, CHANGELOG) kommer fra pakka, så den endres bare med en ny versjon. Han hever ikke versjonen for småting; mellom to versjoner kan derfor `hoest-theme.vsix` i repoet ligge bak `package.json`/README, og det er greit.
9. Etter publisering: VS Code-profilene i mac-setup (Default og Tavle) installerer temaet fra Marketplace, så der ligger ingen vsix-kopi. Endret iTerm-presetene seg, kopier dem: `cp iterm/*.itermcolors ../mac-setup/configs/iterm2/farger/`. Tavle oppdateres med `code --install-extension dagmortensj.hoest-theme --profile Tavle --force`.

Testing: han åpner filene i `test/` (se `test/README.md`). Ser noe galt ut, ber du om **Developer: Inspect Editor Tokens and Scopes** på ordet, og du finner riktig scope ut fra det. Ikke gjett scopes.

## Små ting

- Første avsnitt i `README.md` og `vscode/README.md` er skrevet av Dag-Morten selv. Rør det ikke.
- Ikke lag `__pycache__`: alle tre skriptene setter `dont_write_bytecode`, så en `src/__pycache__` kommer fra en løs `import palette` i `device_bash` (VM-ens Python 3.10). Bruk `python3 -B` eller kjør sjekkskript på en kopi utenfor repoet. Mappa er ignorert i git, men VM-en kan ikke slette den; gi terminal. `.DS_Store` er ignorert.
- Utvidelsen het `host-theme` før 3.5; navnet `hoest-theme` og publisher `dagmortensj` (samme som GitHub-brukeren) er endelige. Før 3.6.1 var publisher `dagmorten`.
- Skjermbildene i `docs/screenshots/` tar han selv.
- Offentlig tekst (README, Marketplace, docs) skal ikke nevne Gruvbox, Solarized eller andre temaer som opphav eller sammenligning for fargene, og ikke LaTeX-malene hans. Motivasjonen er høstfarger og jordtoner, punktum. Sammenligningen av *reglene* med Dracula og Monokai nederst i `rules.md` står.
- Publisher-kontoen er uverifisert (verifisering krever eget domene og seks måneder på Marketplace, tidligst mai 2027). Profilen skal være nøytral og om ham, ikke om Høst.
