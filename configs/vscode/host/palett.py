# Høst-paletten: den eneste kilden til fargene i Høstlys og Høstkveld.
# bygg.py lager VS Code-temaene og iTerm-fargefilene fra denne fila.
# Endre en farge her, kjør `python3 bygg.py`, og alt annet følger med.
#
# Seks farger med faste roller (se palett.md):
#   rød      landemerker og henvisninger: \section, \ref, \cite, lenker, feil
#   rust     struktur: \begin, \end, \item, preamblen, nøkkelord
#   oransje  tall og konstanter
#   grønn    funksjoner og miljønavn
#   blå      strenger og matematikk
#   plum     klasser, typer, greske bokstaver og symboler
#
# Høstlys bygger på lualatex-malene. Høstkveld regnes ut fra Høstlys (se nederst),
# så en endring i en av de seks fargene i Høstlys følger med til Høstkveld.

from fargerom import fra_oklch, juster, juster_lyshet, til_oklch

FARGER = ["rod", "rust", "oransje", "gronn", "bla", "plum"]

HOSTLYS = {
    "type": "light",
    # De seks fargene. Rød, oransje, grønn, blå og plum er de samme som i lualatex-malene.
    "rod": "#781414",             # darkred
    "rust": "#99380e",            # midtpunktet mellom rød og oransje i lyshet, metning og kulør
    "oransje": "#b85c00",         # darkorange
    "gronn": "#4a6b12",           # darkolive
    "bla": "#1e608c",             # darkblue
    "plum": "#6e3278",            # darkplum
    # Tekst og nøytrale toner
    "tekst": "#282828",
    "dempet": "#7c6f64",          # klammer, beskrivelser, inaktive faner
    "kommentar": "#928374",
    "inaktiv": "#a89984",         # inaktive ikoner og titler, ignorerte filer
    "fane_inaktiv": "#7c6f64",
    "linjenr": "#c9a77a",
    "plassholder": "#a89984",
    # Flater
    "bakgrunn": "#fdfcf2",        # editor, panel, terminal
    "ramme": "#f4f1e4",           # sidelinje, faner, tittel- og statuslinje
    "widget": "#f4f1e4",          # hover, forslag, søkefelt i editoren
    "widgetkant": "#e2dcc8",
    "felt": "#fdfcf2",            # tekstfelt og nedtrekkslister
    "linje": "#f6f2e2",           # gjeldende linje
    "markering": "#e2d8bf",
    "markering_svak": "#efe8d6",  # inaktiv markering, like ord
    "sok": "#e8cca9",
    "sok_svak": "#f1dfc6",
    "klammepar": "#ebdbb2",
    "hjelpelinje": "#ebe5d3",     # innrykkslinjer, linjal
    "hjelpelinje_aktiv": "#d5cdb6",
    "mellomrom": "#ddd5bf",
    "liste_aktiv": "#e2d8bf",
    "liste_inaktiv": "#efe8d6",
    "liste_hover": "#efe9d6",
    "kommandosenter": "#ebe6d4",
    "kommandosenter_aktiv": "#e2dcc8",
    "rullefelt": "#3c3836",       # brukes med gjennomsiktighet
    # Terminalen: svart, hvit og de lyse variantene av dem
    "ansi_svart": "#282828",
    "ansi_hvit": "#e2dcc8",
    "ansi_lys_svart": "#7c6f64",
    "ansi_lys_hvit": "#fdfcf2",
    # iTerm: de 16 ANSI-fargene regnes ut nedenfor; her står bare resten
    "iterm": {
        "Background Color": "#fdfcf2",
        "Foreground Color": "#282828",
        "Bold Color": "#282828",
        "Cursor Color": "#282828",
        "Cursor Text Color": "#fdfcf2",
        "Cursor Guide Color": ("#f4f1e4", 0.6),
        "Selection Color": "#e2d8bf",
        "Selected Text Color": "#282828",
        "Link Color": "#781414",
        "Badge Color": ("#99380e", 0.5),
    },
}

HOSTKVELD = {
    "type": "dark",
    # De seks fargene regnes ut fra Høstlys nedenfor.
    "tekst": "#ebe2cb",
    "dempet": "#a3978c",
    "kommentar": "#928374",
    "inaktiv": "#998c76",
    "fane_inaktiv": "#aa9d87",
    "linjenr": "#7e7564",
    "plassholder": "#7e7564",
    "bakgrunn": "#211e17",
    "ramme": "#2d271d",
    "widget": "#29251d",
    "widgetkant": "#38332a",
    "felt": "#363022",
    "linje": "#29251d",
    "markering": "#443d30",
    "markering_svak": "#38332a",
    "sok": "#5c4220",
    "sok_svak": "#3f2f1a",
    "klammepar": "#443d30",
    "hjelpelinje": "#38332a",
    "hjelpelinje_aktiv": "#544c3e",
    "mellomrom": "#38332a",
    "liste_aktiv": "#3d3426",
    "liste_inaktiv": "#363022",
    "liste_hover": "#363022",
    "kommandosenter": "#363022",
    "kommandosenter_aktiv": "#3d3426",
    "rullefelt": "#ebe2cb",
    "ansi_svart": "#38332a",
    "ansi_hvit": "#ebe2cb",
    "ansi_lys_svart": "#928374",
    "ansi_lys_hvit": "#f7f0de",
    "iterm_svart": "#38332a",
    "iterm_hvit": "#efe7d2",
    "iterm_lys_svart": "#a39584",
    "iterm_lys_hvit": "#fffaf0",
    # Høstkveld i iTerm er litt lysere og hvitere fordi vinduet er halvgjennomsiktig
    "iterm": {
        "Background Color": "#211e17",
        "Foreground Color": "#f3ecda",
        "Bold Color": "#fffaf0",
        "Cursor Color": "#f3ecda",
        "Cursor Text Color": "#211e17",
        "Cursor Guide Color": ("#29251d", 0.6),
        "Selection Color": "#4d4535",
        "Selected Text Color": "#fffaf0",
        "Link Color": "@rod",
        "Badge Color": ("@rust", 0.5),
    },
}


# ---------- Høstkveld regnes ut fra Høstlys ----------
#
# Regelen, i OKLCH (lyshet L, metning C, kulør H):
#   L  = 0,281 + 0,837 · L i Høstlys   samme rekkefølge og avstander, skalert til mørk bakgrunn
#   C  = 1,35 · C i Høstlys            alle fargene gløder like mye mer
#   H  = H i Høstlys                   de varme fargene flyttes litt mot rødt, fordi lyse
#                                      farger ellers oppleves gulere enn mørke
LYSHET = (0.281, 0.837)
METNING = 1.35
KULOR = {"rod": -2.3, "rust": -4.0, "oransje": -4.0}


def tent_opp(navn, farge):
    L, C, H = til_oklch(farge)
    a, b = LYSHET
    return fra_oklch(a + b * L, METNING * C, H + KULOR.get(navn, 0.0))


for _navn in FARGER:
    HOSTKVELD[_navn] = tent_opp(_navn, HOSTLYS[_navn])


# ---------- Roller som bygger på de seks fargene ----------

def _roller(p, mork):
    fra_bla = 0.06 if mork else -0.06  # knappen blir lysere i mørkt tema og mørkere i lyst når musa er over
    p.update({
        "fokus": p["oransje"] if mork else p["bla"],
        "knapp": p["bla"],
        "knapp_hover": juster_lyshet(p["bla"], fra_bla),
        "lenke": p["rod"],
        "merke": p["rust"],                                   # tallmerker, f.eks. på kildekontroll-ikonet
        "diff_fjernet": p["rod"] if mork else p["rust"],     # rød med lav dekkevne blir rosa på lys bakgrunn
    })
    # Terminalen: de åtte plassene får palettfargene. Cyan-plassen får rust, så alle
    # seks fargene finnes i terminalen og turkis aldri dukker opp. De lyse variantene
    # er de samme fargene litt lysere.
    p["ansi"] = ansi(p, 0.0)
    # iTerm: Høstkveld gløder litt mer enn i VS Code. Terminalen ser man på i korte
    # økter, og vinduet er halvgjennomsiktig, så fargene tåler å være lysere og mer mettet.
    ekstra = ITERM_EKSTRA if mork else (0.0, 1.0)
    p["iterm"]["ansi"] = list(ansi(p, *ekstra, iterm=True).values())
    for k, v in list(p["iterm"].items()):
        if isinstance(v, str) and v.startswith("@"):
            p["iterm"][k] = juster(p[v[1:]], *ekstra)
        elif isinstance(v, tuple) and v[0].startswith("@"):
            p["iterm"][k] = (juster(p[v[0][1:]], *ekstra), v[1])


ITERM_EKSTRA = (0.04, 1.10)  # lyshet + 0,04 og metning × 1,10 i Høstkveld i iTerm


# ANSI-rekkefølgen: svart, rød, grønn, gul, blå, magenta, cyan, hvit, og så de lyse
ANSI_NAVN = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]
ANSI_FARGE = [None, "rod", "gronn", "oransje", "bla", "plum", "rust", None]


def ansi(p, dL, kC=1.0, iterm=False):
    svart, hvit = (p["iterm_svart"], p["iterm_hvit"]) if iterm and "iterm_svart" in p else (p["ansi_svart"], p["ansi_hvit"])
    lys_svart, lys_hvit = (p["iterm_lys_svart"], p["iterm_lys_hvit"]) if iterm and "iterm_svart" in p else (p["ansi_lys_svart"], p["ansi_lys_hvit"])
    ut = {}
    for navn, f in zip(ANSI_NAVN, ANSI_FARGE):
        ut[navn] = svart if navn == "Black" else hvit if navn == "White" else juster(p[f], dL, kC)
    for navn, f in zip(ANSI_NAVN, ANSI_FARGE):
        ut["Bright" + navn] = lys_svart if navn == "Black" else lys_hvit if navn == "White" else juster(p[f], dL + 0.07, kC)
    return ut


_roller(HOSTLYS, mork=False)
_roller(HOSTKVELD, mork=True)
