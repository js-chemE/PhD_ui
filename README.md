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
save_figure(fig, "figures", "conversion")   # writes PNG + PDF + SVG
```

---

## `initialize()`

Defined in [\_\_init\_\_.py](src/phd_ui/__init__.py). The intended first call in any script. It

1. registers all bundled `.ttf`/`.otf` fonts with matplotlib's font manager, and
2. applies the default `"single"` rcParams preset.

Both steps log a warning instead of raising on failure, so a broken font path never kills a script.

## `plotting/` — styling, sizes, export, annotations

### Style presets — [params.py](src/phd_ui/plotting/params.py), [core.py](src/phd_ui/plotting/core.py)

`BASE_PARAMS` is a flat dict of rcParams tuned for print: Source Sans 3 for body text, Source Serif 4 for math, 8 pt base font, inward ticks on all four sides, frameless legends, `savefig` at 300 dpi with `bbox="tight"` and a transparent background.

`core.py` combines it with every figure size into `PARAMS = {name: {**BASE_PARAMS, "figure.figsize": ...}}`. Two ways to apply it:

- `update_params_string("double", **overrides)` — pick a preset by name, optionally overriding individual rcParams.
- `update_params(my_dict)` — apply an arbitrary rcParams dict.

Also in `core.py`:

- `set_locators(ax, minor_x=2, minor_y=2, major_x=None, major_y=None)` — set major tick spacing and the number of minor intervals per major one. Minor locators are only applied on linear scales.
- `fix_right_ylabels(ax)` — right-align the tick labels on a right-hand y-axis so their outer edges line up.

### Figure sizes — [figsize.py](src/phd_ui/plotting/figsize.py), [figsize.json](src/phd_ui/_assets/figsize.json)

Sizes live in `figsize.json` in **centimetres**; `get_figsizes(in_metric=False)` / `get_figsize(key, in_metric=False)` return them converted to inches (what matplotlib wants). An unknown key logs a warning and falls back to matplotlib's default `(6.4, 4.8)` in.

Presets fall into two families. **Document** presets assume a ~18 cm text block: 9 cm is one column of a two-column layout (or a half-width figure in a thesis), 18 cm is the full text width. **Presentation** (`slide_*`) presets are sized to sit on a slide leaving room for a title and margins — deliberately *not* filling the slide edge to edge. Note that 16:9 and 4:3 PowerPoint slides are the **same height** (19.05 cm / 7.5″); only the width differs (33.87 vs 25.4 cm), so the slide presets mostly differ in width.

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

**Presentation presets** (for slides; all 19.05 cm tall media):

| Preset | Size (cm) | When to use |
|---|---|---|
| `slide_16x9` | 26 × 14 | Hero figure filling a 16:9 slide, with room for a title bar and side margins. |
| `slide_4x3` | 21 × 14 | Hero figure for a 4:3 slide (narrower usable width). |
| `slide_half` | 14.5 × 12 | One of two figures placed side by side on a 16:9 slide. |
| `slide_tall` | 12 × 15 | A portrait figure beside a bullet list. |

> A worked example that draws every preset to scale on an A4 page and on 16:9/4:3 slides — plus a multi-page PDF report and PowerPoint decks with the figures at true size — lives in [example/figsize_comparison.ipynb](example/figsize_comparison.ipynb).

Rules of thumb:

- Pick the size **before** plotting, not afterwards — rescaling a finished figure breaks the font-size/line-width balance the presets are tuned for.
- Never shrink `figsize` to make text look smaller. Keep the preset and reduce the content, or move up a size.
- Reuse the same few presets throughout a manuscript so line widths and label sizes stay comparable across figures.

### Unit conversion — [conversion.py](src/phd_ui/plotting/conversion.py)

`INCH2CM`, `cm_to_inches()`, `inches_to_cm()`. Scalars and numpy arrays.

### Export — [export.py](src/phd_ui/plotting/export.py)

`save_figure(fig, figure_path, name, dpi=300, as_png=True, as_pdf=True, as_svg=True)` writes the same figure to all three formats in one call: PNG for slides, PDF for the manuscript, SVG for hand-editing.

### Annotations — [draw.py](src/phd_ui/plotting/draw.py)

- `draw_peak(ax, wavenumber_cm, height, ...)` — vertical marker line at a peak with a rotated label beside it. The label is rendered once to measure its real pixel bounding box and then re-placed, so the gap to the line is identical whether the label sits left or right (matplotlib's `ha`/`va` alignment is not symmetric under rotation).
- `draw_vscale(ax, x, y, value=None, scale=1.0, ...)` — vertical intensity scale bar for plots with an arbitrary or offset y-axis (stacked spectra). With `value=None` it picks a "nice" 1/2/5 × 10ⁿ value covering ~12 % of the y-range automatically. Anchor in data coordinates (`ax.transData`, default) or axes coordinates (`ax.transAxes`).
- `draw_colorbar(ax, cmap, vmin, vmax, cmap_vmin=0.0, cmap_vmax=1.0, ...)` — a colorbar that matches `value_to_color`, including the case where only a sub-range of the colormap is sampled (matplotlib's own colorbar cannot express that).

## `colors/` — palette and colormaps

### [base.py](src/phd_ui/colors/base.py)

`SPECIES_COLORS` maps species abbreviations (`Ar`, `N2`, `CO2`, `H2`, `MeOH`, `MF`, `CO`, `CH4`, `H2O`, `DME`, `EtOH`) to their canonical hex colours. Use it everywhere so a species keeps the same colour across all figures.

### [manipulation.py](src/phd_ui/colors/manipulation.py)

- `hex_to_rgb(hex, mode="int"|"float")` / `rgb_to_hex(rgb, mode=...)` — `"int"` is 0–255, `"float"` is 0–1 (what matplotlib uses).
- `adjust_saturation(hex, value, mode="relative"|"absolute")` — either multiply the current HSV saturation or set it outright.
- `create_saturation_palette(hex, n_colors=5, sat_range=(0.3, 1.0))` — a series of tints of one base colour. Good for "same species, different conditions".

### [cmaps.py](src/phd_ui/colors/cmaps.py)

- `create_colormap_from_color(color, min_sat, max_sat, number, location, as_hex=False)` — build a colormap as a saturation ramp around one hue, pinning the base colour at a chosen position.
- `create_colormap_from_cmap(cmap, vmin=0, vmax=1, number=10, as_hex=False)` — sub-sample an existing matplotlib colormap, e.g. `vmin=0.2, vmax=0.8` on `"Greens"` to avoid the near-white and near-black ends.
- `value_to_color(value, cmap, vmin, vmax, cmap_vmin=0.0, cmap_vmax=1.0, clip=True, as_hex=False)` — map data values (scalar or array, vectorised) to colours, e.g. colour spectra by temperature. Pair it with `draw_colorbar` using the same four range arguments to get a legend that actually matches.

`create_colormap_from_color` and `create_colormap_from_cmap` return either a `LinearSegmentedColormap` or a list of hex strings, depending on `as_hex`.

## `fonts/` — [fonts.py](src/phd_ui/fonts/fonts.py)

`load_fonts(fonts_dir)` recursively finds every `.ttf`/`.otf` under a directory and registers it with `matplotlib.font_manager`. Raises `FileNotFoundError` if the directory is missing and `RuntimeError` if it contains no fonts. Called for you by `initialize()`.

## `renaming/` — [renaming.py](src/phd_ui/renaming/renaming.py)

`Renaming` is a pydantic model over a JSON file mapping a canonical name to its aliases (`{"MeOH": ["MeOH", "Methanol"], ...}`). `get_renaming(value)` accepts a `str`, `list`, or `pd.Series` and returns the canonical name(s); unknown inputs are passed through with a warning.

```python
from phd_ui.renaming.renaming import Renaming

r = Renaming.from_json("src/phd_ui/_assets/renaming.json")
r.get_renaming("Methanol")            # -> "MeOH"
r.get_renaming(df["species"])         # -> pd.Series of canonical names
```

## Assets — [\_assets/](src/phd_ui/_assets/)

| File | Contents |
|---|---|
| `figsize.json` | Figure size presets, in cm |
| `renaming.json` | Species canonical names → aliases |
| `fonts/Source_Sans_3/` | Body/UI font |
| `fonts/Source_Serif_4/` | Math font |

## Tests

```bash
pytest                                          # all tests
pytest tests/test_colors.py::test_rgb_to_hex    # a single test
```

## Known rough edges

- `phd_ui.renaming.__init__` builds `MAIN_RENAMING` with a `filepath=` argument and an `_renaming.xlsx` path, neither of which the current `Renaming` model accepts — so importing `phd_ui.renaming` fails. Import `Renaming` from `phd_ui.renaming.renaming` and use `Renaming.from_json()` instead. (`phd_ui.initialize()` is unaffected; it does not touch this module.)
- `numpy`, `pandas`, and `pydantic` are used but not declared in `pyproject.toml`; they currently come in transitively via matplotlib or the environment.
