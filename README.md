# PhD_ui

Helper functions to better visualise and interact with data and graphs obtained and generated during my PhD at Urakawa group at TU Delft.

`phd_ui` bundles the things that would otherwise be copy-pasted into every plotting script: a consistent matplotlib style, the fonts that go with it, canonical figure sizes, a species colour palette, colormap helpers, a few annotation primitives, and a small alias resolver for chemical species names.

## Installation

```bash
uv sync           # editable install of the project + dependencies
# or
pip install -e .
```

Requires Python ≥ 3.13.

## Quick start

```python
import matplotlib.pyplot as plt
import phd_ui
from phd_ui.plotting import update_params_string, save_figure, set_locators
from phd_ui.colors import SPECIES_COLORS

phd_ui.initialize()                  # register fonts + apply the "single" preset
update_params_string("double")       # switch to a two-column figure

fig, ax = plt.subplots()
ax.plot(x, y, color=SPECIES_COLORS["MeOH"], label="MeOH")
set_locators(ax, minor_x=2, minor_y=2)
save_figure(fig, "figures", "conversion")   # writes PNG + PDF (add as_svg=True for SVG)
```

---

## `initialize()`

Defined in [\_\_init\_\_.py](src/phd_ui/__init__.py). The intended first call in any script. It

1. registers all bundled `.ttf`/`.otf` fonts with matplotlib's font manager, and
2. applies the default `"single"` rcParams preset.

Both steps log a warning instead of raising on failure, so a broken font path never kills a script.

## `plotting/` — styling, sizes, export, annotations

### Style presets — [params.py](src/phd_ui/plotting/params.py), [core.py](src/phd_ui/plotting/core.py)

`get_params(scale)` builds a full rcParams set: Source Sans 3 for body text, Source Serif 4 for math, inward ticks on all four sides, frameless legends, constrained layout, `savefig` at 300 dpi on a transparent background. `BASE_PARAMS = get_params()` is the print set.

**Two rendered sizes, picked for you.** The base font is 8 pt for print, and `slide_*` presets come out at **2x** (16 pt base, 18 pt axis labels, and every line width, tick length and pad doubled to match). One point size cannot serve both media: a 16:9 slide canvas is 33.9 cm against a 16–18 cm text block, and is read from metres rather than arm's length, so 8 pt on a slide subtends about half the angle 10 pt body text does on paper. Scaling the fonts alone would leave hairline axes next to large labels, so everything measured in points scales together.

`core.py` combines that with every figure size into `PARAMS = {name: {**get_params(scale_for_key(name)), "figure.figsize": ...}}`, so the scale follows from the key you already pass. Two ways to apply it:

- `update_params_string("slide_full", **overrides)`: pick a preset by name, optionally overriding individual rcParams for that call only.
- `update_params(my_dict)`: apply an arbitrary rcParams dict.

**Do not call `fig.tight_layout()` or `fig.subplots_adjust()`.** Constrained layout is on with a zero outer pad, so the drawn content fills the canvas and the saved file is exactly the width `figsize` asked for. Calling either of the two warns and drops the figure back to the old behaviour, where `bbox="tight"` trims the unused margin and the file comes out 5–20 % narrower than requested, by an amount that depends on how much label text the figure carries. Placing such a file at a fixed width scales it back up, and the effective font size then varies from figure to figure, the exact thing the shared size table exists to prevent. `bbox="tight"` is kept with `pad_inches=0` as a safety net: normally a no-op, but an artist deliberately placed outside the canvas grows the file instead of being clipped.

Also in `core.py`:

- `set_locators(ax, minor_x=2, minor_y=2, major_x=None, major_y=None)` — set major tick spacing and the number of minor intervals per major one. Minor locators are only applied on linear scales.
- `fix_right_ylabels(ax)` — right-align the tick labels on a right-hand y-axis so their outer edges line up.

### Figure sizes — [figsize.py](src/phd_ui/plotting/figsize.py), [figsize.json](src/phd_ui/_assets/figsize.json)

Sizes live in `figsize.json` in **centimetres**; `get_figsizes(in_metric=False)` / `get_figsize(key, in_metric=False)` return them converted to inches (what matplotlib wants). An unknown key raises `FigsizeKeyError`, listing every available key and naming the replacement if it is one that was renamed.

Presets fall into two families. **Document** presets assume a ~18 cm text block: 9 cm is one column of a two-column layout (or a half-width figure in a thesis), 18 cm is the full text width. **Presentation** (`slide_*`) presets are cut from the slide *body box*, what is left of a 16:9 canvas once the title band and the side margins are taken off, so they deliberately do *not* fill the slide edge to edge. Aspect ratio is not part of the naming: 16:9 and 4:3 decks are the same height (19.05 cm / 7.5″) and differed only in usable width, and the reason to reach for a slide key is the 2x point size that comes with it, not the shape of the deck.

**Document presets** (for papers / the thesis) form a full **height × width matrix**: every height exists at both the single (9 cm) and double (18 cm) width, and the narrow name mirrors the wide one at the same height. Pick the width from your column layout and the height from the figure's content.

| Height (cm) | single — 9 cm wide | double — 18 cm wide |
|---|---|---|
| 4.5 | `single_short` | `double_short` |
| 6.5 | `single` *(default)* | `double_single` |
| 9 | `single_square` | `double_single_square` |
| 11.5 | `single_double` | `double` |
| 18 | `single_double_square` | `double_square` |
| 24 | `single_long` | `double_long` |

| Preset | Size (cm) | When to use |
|---|---|---|
| `single_short` | 9 × 4.5 | Half-width strip: a small inset, a mini time trace or spectrum. |
| `single` | 9 × 6.5 | **Default.** One-column journal / half-width thesis figure — the workhorse. |
| `single_square` | 9 × 9 | Square half-width axes: parity / correlation plots, 1:1 lines. |
| `single_double` | 9 × 11.5 | Tall half-width figure: a vertical profile or tall bar chart. |
| `single_double_square` | 9 × 18 | Very tall half-width: a stacked-spectra column beside body text. |
| `single_long` | 9 × 24 | Full-height half-width column: a long reaction pathway / timeline. |
| `double` | 18 × 11.5 | Full text width; 2 × 2 panel grids or one busy plot. |
| `double_single` | 18 × 6.5 | Full width at a single figure's height — a row of 2–3 panels (a)(b)(c). (Formerly `double_single_height`.) |
| `double_single_square` | 18 × 9 | Full width, moderate height: wide 1 × 3 panels, a map. |
| `double_short` | 18 × 4.5 | Full width and short: time series / on-stream (TOS) traces, spectra strips. (Formerly `double_small`.) |
| `double_square` | 18 × 18 | Full width and tall: 3 × 3 grids, correlation matrices, heatmaps. |
| `double_long` | 18 × 24 | Whole-page portrait figure: SI figure stacks, overviews. Documents only. (Formerly `fullpage`.) |

**Presentation presets.** All but the last are cut from the **body box**, 31 × 14.5 cm, which is a 33.87 × 19.05 cm 16:9 canvas minus a 1.4 cm side margin, a 3.3 cm title band and a 1.25 cm bottom margin. Half of that width, with a 2 cm gutter, lands on 14.5 cm as well, so a half-width figure and a square one share a width. `SLIDE_CANVAS` and `SLIDE_BODY` hold those two boxes, and a test checks that every slide preset still fits inside the second.

| Preset | Size (cm) | When to use |
|---|---|---|
| `slide_short` | 31 × 6.5 | Band across the body: a TOS trace or a spectra strip, with room for a line of text under it. |
| `slide` | 31 × 10 | Full body width at a comfortable height, leaving room for a takeaway line below. |
| `slide_full` | 31 × 14.5 | **Hero figure**, filling everything under the title. The one you want most of the time. |
| `slide_half` | 14.5 × 10 | One of two figures placed side by side. |
| `slide_square` | 14.5 × 14.5 | Square at full body height: a parity plot, or a figure beside a bullet list. |
| `slide_full_16x9` | 33.87 × 19.05 | True full-bleed slide, no title and no margins. Rare, hence the explicit name. |

> A worked example that draws every preset to scale on an A4 page and in the body box of a 16:9 slide, plus a multi-page PDF report and a PowerPoint deck with the figures at true size, lives in [example/figsize_comparison.ipynb](example/figsize_comparison.ipynb).

Rules of thumb:

- Pick the size **before** plotting, not afterwards — rescaling a finished figure breaks the font-size/line-width balance the presets are tuned for.
- Never shrink `figsize` to make text look smaller. Keep the preset and reduce the content, or move up a size.
- Reuse the same few presets throughout a manuscript so line widths and label sizes stay comparable across figures.

### Unit conversion — [conversion.py](src/phd_ui/plotting/conversion.py)

`INCH2CM`, `cm_to_inches()`, `inches_to_cm()`. Scalars and numpy arrays.

### Export — [export.py](src/phd_ui/plotting/export.py)

`save_figure(fig, figure_path, name, dpi=300, as_svg=False, as_pdf=True, as_png=True)` writes the same figure to several formats in one call: PNG for slides, PDF for the manuscript. **SVG is opt-in** — pass `as_svg=True` for a figure you will hand-edit in Illustrator. It used to default to `True`, which wrote a large SVG on every save whether or not anything ever opened it.

### Annotations — [draw.py](src/phd_ui/plotting/draw.py)

- `draw_peak(ax, wavenumber_cm, height, ...)` — vertical marker line at a peak with a rotated label beside it. The label is rendered once to measure its real pixel bounding box and then re-placed, so the gap to the line is identical whether the label sits left or right (matplotlib's `ha`/`va` alignment is not symmetric under rotation).
- `draw_vscale(ax, x, y, value=None, scale=1.0, ...)` — vertical intensity scale bar for plots with an arbitrary or offset y-axis (stacked spectra). With `value=None` it picks a "nice" 1/2/5 × 10ⁿ value covering ~12 % of the y-range automatically. Anchor in data coordinates (`ax.transData`, default) or axes coordinates (`ax.transAxes`).
- `draw_colorbar(ax, cmap, vmin, vmax, cmap_vmin=0.0, cmap_vmax=1.0, ...)` — a colorbar that matches `value_to_color`, including the case where only a sub-range of the colormap is sampled (matplotlib's own colorbar cannot express that).

## `colors/` — palette and colormaps

The colour scheme itself is documented in [scheme.py](src/phd_ui/colors/scheme.py), with previews in [docs/colorscheme/](docs/colorscheme/). Nature's guide to designing figures, the reference the scheme's hierarchy and accessibility rules follow, is kept at [docs/natrev-artworkguide.pdf](docs/natrev-artworkguide.pdf).

### [scheme.py](src/phd_ui/colors/scheme.py)

Ten hues (`PINK`, `ORANGE`, `RED`, `AMBER`, `GREEN`, `BLUE`, `PURPLE`, `GREY`, `SAND`, `INK`), each a `ColorFamily` with four **fill tones** (`light`, `base`, `dark`, `darkest`) and one **line tone** (`line`). The fill tones are the drawing vocabulary; `line` is the same hue with more chroma and mid lightness, because a 1 pt stroke reads washed out in a colour that is right on a filled box. `SCHEME_LINE` is the categorical cycle built from the line tones and is what `axes.prop_cycle` carries in every preset, so an unstyled `ax.plot` already comes out in the scheme.

```python
ax.plot(x, y, color=colors.BLUE.line)                 # a line or a marker
ax.fill_between(x, lo, hi, color=colors.BLUE.base)    # a band or a patch
ax.text(..., color=colors.INK.base)                   # text
```

### [base.py](src/phd_ui/colors/base.py)

`SPECIES` maps species abbreviations (`Ar`, `N2`, `CO2`, `H2`, `MeOH`, `MF`, `CO`, `CH4`, `H2O`, `DME`, `EtOH`, `He`) to a `Species` with a `color` for traces and markers and a `fill` for drawings, both resolved from the scheme so the hue encodes the species' role (green target, CO2 dark blue and H2 light red as the two feeds, purple/pink side products, red/amber undesired, grey inert). `SPECIES_COLORS` is the `{name: hex}` of the line colours, `SPECIES_FILL_COLORS` that of the fills. Use them everywhere so a species keeps its colour across all figures.

### [nature.py](src/phd_ui/colors/nature.py)

`NATURE` is the Nature-branded palette (eleven families, six steps each) that Nature's art editors use for conceptual figures, grouped as `NATURE_BACKGROUND`, `NATURE_ACCENTS` and `NATURE_EXTENDED`. `nature_colors(families, step)` picks one hex per family, `nature_cmap(family)` interpolates a family into a colormap. For drawings meant to look like a Nature figure; plots use the scheme. The guide it follows is [docs/natrev-artworkguide.pdf](docs/natrev-artworkguide.pdf).

### [manipulation.py](src/phd_ui/colors/manipulation.py)

- `hex_to_rgb(hex, mode="int"|"float")` / `rgb_to_hex(rgb, mode=...)` — `"int"` is 0–255, `"float"` is 0–1 (what matplotlib uses).
- `adjust_saturation(hex, value, mode="relative"|"absolute")` — either multiply the current HSV saturation or set it outright.
- `create_saturation_palette(hex, n_colors=5, sat_range=(0.3, 1.0))` — a series of tints of one base colour. Good for "same species, different conditions".

### [wong.py](src/phd_ui/colors/wong.py)

`WONG` is the colour-blind-safe palette of Wong, *Nature Methods* 8, 441 (2011), from the paper's own RGB column; the paper is at [docs/wong2011-color-blindness.pdf](docs/wong2011-color-blindness.pdf). The module docstring maps the paper's rules (vary lightness and saturation, not only hue; any colour with red and green components is suspect; replace red with magenta; soft-proof in Illustrator) onto what the scheme does about each.

### [atoms.py](src/phd_ui/colors/atoms.py)

The reference for drawing atoms and bonds, in figures, the IR-bands animations and Illustrator. `ATOMS` gives every element a flat `fill`, a darker `edge`, a `light` tint for an oxidised rim, a `text` colour and its covalent radius. The hues are CPK (H white, C dark grey, N blue, O red, P orange, S yellow), toned to the scheme. `BOND_STYLES` has the five bond kinds: single, double, triple, partial (dashed), and surface (dotted). The drawing helpers are `plotting.draw_atom`, `draw_bond` and `draw_molecule`, in pm on an equal-aspect axes. The reference sheet is [docs/colorscheme/colorscheme_atoms.png](docs/colorscheme/colorscheme_atoms.png).

### [cmaps.py](src/phd_ui/colors/cmaps.py)

- `create_colormap_from_color(color, min_sat, max_sat, number, location, as_hex=False)` — build a colormap as a saturation ramp around one hue, pinning the base colour at a chosen position.
- `create_colormap_from_cmap(cmap, vmin=0, vmax=1, number=10, as_hex=False)` — sub-sample an existing matplotlib colormap, e.g. `vmin=0.2, vmax=0.8` on `"Greens"` to avoid the near-white and near-black ends.
- `value_to_color(value, cmap, vmin, vmax, cmap_vmin=0.0, cmap_vmax=1.0, clip=True, as_hex=False)` — map data values (scalar or array, vectorised) to colours, e.g. colour spectra by temperature. Pair it with `draw_colorbar` using the same four range arguments to get a legend that actually matches.

`create_colormap_from_color` and `create_colormap_from_cmap` return either a `LinearSegmentedColormap` or a list of hex strings, depending on `as_hex`.

## `fonts/` — [fonts.py](src/phd_ui/fonts/fonts.py)

**Typography rule.** Source Sans 3 is used for all figure and slide text. Maths follows the text it sits beside: Source Serif 4 in print figures, to match a Source Serif 4 thesis body, and Source Sans 3 italic on slides. Segoe UI is retired for slides. The full guideline, with the thesis preamble and the open to-dos, is in [CLAUDE.md](CLAUDE.md), under *Typography: one sans for text, maths follows the medium*. Page 10 of [docs/mock_report.pdf](docs/mock_report.pdf) shows the fonts at true size.

`load_fonts(fonts_dir)` recursively finds every `.ttf`/`.otf` under a directory and registers it with `matplotlib.font_manager`. Raises `FileNotFoundError` if the directory is missing and `RuntimeError` if it contains no fonts. Called for you by `initialize()`.

## Assets — [\_assets/](src/phd_ui/_assets/)

| File | Contents |
|---|---|
| `figsize.json` | Figure size presets, in cm |
| `fonts/Source_Sans_3/` | Body/UI font |
| `fonts/Source_Serif_4/` | Math font |

## Tests

```bash
pytest                                          # all tests
pytest tests/test_colors.py::test_rgb_to_hex    # a single test
```

## Known rough edges

- Species renaming used to live here as `phd_ui.renaming`. It was removed in 2026-10: the one implementation is `phd_parser.naming.species` (`rename_species`, `SpeciesConvention`), whose convention is a superset of the old alias file.
