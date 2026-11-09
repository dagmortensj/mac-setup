# Instruksjoner for Claude Code i VS Code

Jeg er Dag-Morten, lektor i matematikk og fysikk. Snakk norsk med meg, vær kortfattet, og si fra rett ut hvis noe er feil.

## Når du endrer i mine filer

- Endre bare det jeg ber om. Ikke formater om, gi nytt navn til eller rydd i resten av fila.
- Bruk makroene og miljøene som finnes i prosjektet (preamble og stilfiler). Les dem før du skriver ny kode, og ikke legg til pakker uten å spørre.

## LaTeX

- Ett avsnitt per linje, uten harde linjeskift inne i avsnitt.
- Displaymatte (equation, align og lignende): alltid `\frac`, aldri `\tfrac`.
- Vektorer: indeksen utenfor pila, `\vv{F}_1`, aldri `\vv{F_1}`. Bruk `\vv`, ikke `\vec`.
- Figurer: innholdsfargene er oransje og grønn. Rødt (darkred) er bare for lenker, bokser rundt viktige resultater og skillelinjer.
- Kompilerer du for å sjekke noe, hold terminalen stille: `latexmk -interaction=nonstopmode main >/dev/null 2>&1`, og les `.log` ved feil.

## Fysikk og fagspråk

- Fasit og løsningsforslag: utled et symbolsk uttrykk først og sett inn tall helt til slutt, uten mellomregninger med tall.
- Aldri «regnestykke». Bruk «utledning», «beregning» eller «regning».
- «Hastighet» er vektoren, «fart» er størrelsen.

## Skrivestil

- Vanlig, godt formulert prosa uten typiske AI-vendinger: slagord, «ikke X, men Y» og korte punchlines.
