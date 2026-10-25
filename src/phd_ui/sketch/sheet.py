"""
The atom sheet: every element of :data:`~phd_ui.colors.ATOMS` in both
states, plus the vacancy and the site ring, as one SVG.

It is the library to drag from when a drawing is made by hand in
Illustrator, and it is generated, so it cannot drift from the colours the
code uses. ``example/sketch_atoms.py`` writes it to ``docs/sketch/``.
"""

from __future__ import annotations

from phd_ui.colors.atoms import ATOMS, IONS, drawn_radius_pm
from phd_ui.sketch.primitives import label, site, vacancy
from phd_ui.sketch.scene import Scene, _num

__all__ = ["atom_sheet"]


def atom_sheet(symbols: list[str] | None = None, pm_per_mm: float = 65.0) -> Scene:
    """
    One column per element: plain state, oxidised state, vacancy, site ring,
    and below them the element's ions from :data:`~phd_ui.colors.IONS` at
    their ionic radius, labelled.

    Parameters
    ----------
    symbols : list of str, optional
        Elements to include, by default every key of ``ATOMS``.
    pm_per_mm : float, optional
        Drawing scale, the same default as :class:`Scene`, so atoms copied
        out of the sheet match a generated sketch in size.

    Returns
    -------
    Scene
        The sheet; ``.save(directory, 'atoms')`` writes it.
    """
    symbols = symbols or list(ATOMS)
    col_mm, row_mm = 9.0, 9.0
    left_mm, top_mm = 22.0, 10.0
    scene = Scene(left_mm + col_mm * len(symbols) + 4, top_mm + row_mm * 6 + 2,
                  pm_per_mm=pm_per_mm, title="phd_ui atom sheet", source="phd_ui.sketch.atom_sheet")
    m = scene.mm
    names = scene.layer("row-names")
    for i, text in enumerate(("plain", "ox", "vacancy", "site", "ion")):
        label(names, m(2), m(top_mm + row_mm * i) + scene.pt(3), text)
    for j, symbol in enumerate(symbols):
        x = m(left_mm + col_mm * j)
        col = scene.layer(f"element-{symbol}")
        label(col, x, m(top_mm) - m(4.5), symbol, anchor="middle", kind="title")
        r = scene.radius(symbol)
        col.group("plain").atom(symbol, x, m(top_mm))
        col.group("ox").atom(symbol, x, m(top_mm + row_mm), state="ox")
        vacancy(col.group("vacancy"), symbol, x, m(top_mm + 2 * row_mm))
        g = col.group("site")
        g.atom(symbol, x, m(top_mm + 3 * row_mm))
        site(g, x, m(top_mm + 3 * row_mm), r + scene.pt(2))
        # ions: plain circles in the element's style, one per IONS entry, the
        # default (octahedral) one in the row, others stacked under it
        ions = [ion for ion in IONS.values() if ion.symbol == symbol]
        for k, ion in enumerate(ions):
            y = m(top_mm + (4 + k) * row_mm)
            gi = col.group(f"ion-{ion.key}")
            r_ion = drawn_radius_pm(ion.radius_pm, scene.size_exponent)
            gi.add("circle", {"class": f"atom-{symbol}", "cx": _num(x), "cy": _num(y),
                              "r": _num(r_ion - scene.pt(0.3))})
            label(gi, x, y + r_ion + scene.pt(7), _ion_markup(ion.key), anchor="middle", kind="note")
    return scene


def _ion_markup(key: str) -> str:
    """``'Ga3+(IV)'`` to ``'Ga^{3+} IV'`` for the label markup."""
    name, _, cn = key.partition("(")
    i = next(k for k, ch in enumerate(name) if ch.isdigit() or ch in "+-")
    text = f"{name[:i]}^{{{name[i:]}}}"
    return f"{text} {cn.rstrip(')')}" if cn else text
