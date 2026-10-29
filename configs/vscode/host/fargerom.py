"""Omregning mellom hex og OKLCH, og kontrast etter WCAG.

OKLCH beskriver en farge med lyshet (L, 0 til 1), metning (C) og kulør (H, grader).
Fargerommet er laget slik at like store tallforskjeller oppleves omtrent like store,
og derfor brukes det når Høstkveld regnes ut fra Høstlys.
"""
import math


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _srgb(c):
    c = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return max(0, min(255, round(c * 255)))


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def til_oklch(h):
    r, g, b = (_lin(x) for x in _rgb(h))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (x ** (1 / 3) for x in (l, m, s))
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360


def fra_oklch(L, C, H):
    """OKLCH til hex. Farger utenfor det skjermen kan vise, klippes."""
    A = C * math.cos(math.radians(H))
    B = C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return "#%02x%02x%02x" % (_srgb(r), _srgb(g), _srgb(b))


def kontrast(f1, f2):
    """WCAG-kontrast mellom to hex-farger (1 til 21)."""
    def lum(h):
        r, g, b = (_lin(x) for x in _rgb(h))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    a, b = sorted([lum(f1), lum(f2)], reverse=True)
    return (a + 0.05) / (b + 0.05)


def juster_lyshet(h, dL):
    """Samme farge, lysere (dL > 0) eller mørkere (dL < 0)."""
    L, C, H = til_oklch(h)
    return fra_oklch(L + dL, C, H)


def juster(h, dL=0.0, kC=1.0):
    """Samme kulør, med endret lyshet og metning (metningen ganges med kC)."""
    L, C, H = til_oklch(h)
    return fra_oklch(L + dL, C * kC, H)
