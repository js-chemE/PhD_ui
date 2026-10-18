"""
Wong's colour-blind-safe palette and the rules it comes with.

Bang Wong, "Points of view: Color blindness", Nature Methods 8, 441 (2011),
doi:10.1038/nmeth.1618, kept at ``docs/wong2011-color-blindness.pdf``. The
eight colours are Okabe and Ito's "colour universal design" set; Wong made
them the default answer in the life sciences, and many journals' author
guides still point at them.

What the paper says, and how the PhD scheme answers it
------------------------------------------------------
- **Red-green colour vision deficiency is common**: up to 8 % of men and
  0.5 % of women of Northern European ancestry. Three male reviewers give a
  22 % chance that at least one is colour blind. The scheme is checked
  against a deuteranopia simulation (:func:`phd_ui.colors.plot_species`).
- **Vary lightness and saturation, not only hue.** Colours that differ in
  hue alone collapse in greyscale and for a deuteranope. The scheme's line
  tones sit in a fixed lightness band, so neighbours in the cycle differ
  in hue *and* are ordered to keep the largest simulated distance; species
  sharing a hue (CO2 and H2, MF and DME, the inerts) differ in lightness.
- **Any colour with red and green components is suspect**, not only pure
  red and pure green. In the scheme that means the green target (MeOH)
  against the pink and red families: MeOH against MF or CH4 needs a label
  or a line style as well, and every DRIFTS band keeps its text label.
- **Replace red with magenta in a red/green pair** (or green with
  turquoise). The scheme's pink family is the magenta option when a
  two-colour contrast has to survive colour blindness.
- **Soft-proof**: in Illustrator, View > Proof Setup > Color Blindness
  (document in RGB). The same check this module's palette passes.

Use the palette itself when a figure has to follow it, e.g. a journal that
asks for it, or a categorical plot with no species meaning. Otherwise the
scheme's line tones (:data:`phd_ui.colors.SCHEME_LINE`) are the default.
"""

__all__ = ["WONG", "WONG_COLORS"]

#: Wong (2011) Fig. 2, in the paper's order, as ``{name: hex}`` from its RGB column.
WONG: dict[str, str] = {
    "black": "#000000",
    "orange": "#e69f00",
    "sky blue": "#56b4e9",
    "bluish green": "#009e73",
    "yellow": "#f0e442",
    "blue": "#0072b2",
    "vermillion": "#d55e00",
    "reddish purple": "#cc79a7",
}

#: The palette as a list, black last: it is the outline colour, not a series.
WONG_COLORS: list[str] = [c for name, c in WONG.items() if name != "black"] + [WONG["black"]]
