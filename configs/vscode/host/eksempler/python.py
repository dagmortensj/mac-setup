"""Eksempelfil for å se Høst-temaene på Python."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional

import matplotlib.pyplot as plt
import numpy as np

G: float = 6.674e-11  # gravitasjonskonstanten
GRENSE = 0x1F
DEBUG = False


@dataclass
class Planet:
    """En planet i bane rundt sola."""

    navn: str
    masse: float
    posisjon: np.ndarray = field(default_factory=lambda: np.zeros(2))

    def __post_init__(self) -> None:
        if self.masse <= 0:
            raise ValueError(f"Massen må være positiv, fikk {self.masse!r}")

    @property
    def er_tung(self) -> bool:
        return self.masse > 1e24 and not DEBUG

    @classmethod
    def fra_tekst(cls, tekst: str) -> Planet:
        navn, masse = tekst.split(";")
        return cls(navn.strip(), float(masse))

    def __repr__(self) -> str:
        return f"Planet({self.navn}, {self.masse:.3e} kg)"


def euler(f: Callable[[float, float], float], y0: float, t: np.ndarray) -> list[float]:
    """Løser y' = f(t, y) med Eulers metode."""
    y = [y0]
    for i in range(len(t) - 1):
        dt = t[i + 1] - t[i]
        y.append(y[-1] + f(t[i], y[-1]) * dt)
    return y


async def hent(url: str, tidsavbrudd: Optional[int] = None) -> dict[str, int]:
    try:
        svar = await last_ned(url, timeout=tidsavbrudd or 10)
    except (TimeoutError, ConnectionError) as feil:
        print(f"Feil: {feil}\n\tPrøv igjen", end="")
        return {}
    finally:
        pass
    return {"status": 200, "lengde": len(svar)}


def tolk(linje: str) -> str | None:
    if (treff := re.match(r"^(\d+)\s*([a-z]+)$", linje)) is not None:
        return treff.group(2)
    match linje.split():
        case ["stopp"]:
            return None
        case [kommando, *argumenter] if kommando in {"flytt", "snu"}:
            return f"{kommando}: {', '.join(argumenter)}"
        case _:
            return 'ukjent'


if __name__ == "__main__":
    jorda = Planet("Jorda", 5.972e24)
    t = np.linspace(0, 10, 101)
    v = euler(lambda t, v: -9.81, 0.0, t)
    z = 3 + 4j
    print(jorda, abs(z), len(v), GRENSE, sep=" | ")
    plt.plot(t, v, color="tab:red", label=r"$v(t)$")
    plt.xlabel("$t$ / s")
    plt.legend()
    plt.show()
