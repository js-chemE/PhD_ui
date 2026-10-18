# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Knowledge vault (Obsidian): read this before asking

Julius keeps his PhD knowledge notes in an Obsidian vault at

`C:\Users\jsommer1\Documents\MyPhD\`

It sits outside every code repo and holds the context the code does not record:
background, decisions, literature notes, project and programme structure. When a
question is about *why* rather than *how the code works*, look there first. The
link is two-way: the vault's own header block lists `C:\Users\jsommer1\CODE` and
all four packages, so it expects you to come back here for the code.

**Entry points, in order.** The vault root has its own `CLAUDE.md` (it has to
live at root level), which does nothing but forward to `me.md`. `me.md` is the
briefing: who Julius is, how he wants to be worked with, and how the vault is
laid out. `me.md`, `Vault Map` and `Skills Map` all open with the same header
block, so any of the three orients you.

| file | what it is |
|---|---|
| `CLAUDE.md` | one line, points at `me.md` |
| `me.md` | the briefing and his working preferences (start here) |
| `000 AIOS/Maps/Vault Map.md` | folder structure and the AI tag system |
| `000 AIOS/Maps/Skills Map.md` | index of the skills the AI can run on his behalf |
| `Atlas.md` | topic map of the subject-matter notes |
| `000 AIOS/History/` | where AI-written notes go |
| `000 AIOS/Skills/<name>/` | one self-contained folder per skill: the note is the contract, the assets beside it are the implementation |

**Read those core notes from disk, via the shell, every time.** `me.md` asks for
this explicitly: never work from a cached or staged copy, and re-read
immediately before writing, because a stale copy has already nearly clobbered
his edits.

**Vault layout** (LYT ACE, plus AIOS): `+/` inbox for new captures, `+ Vault/`
imported sources (`+ Vault/Zotero/` named `@{first-author}.{three-word-title}.{year}`),
`100 Notes/` timeless notes (maps, people, quotes), `200 Calendar/` days and
reviews, `300 Efforts/` areas, projects and works, `x/` templates, attachments,
PDFs, images, scripts, `000 AIOS/` the AI operating system itself.

**Writing rules, from `me.md` and the Vault Map.** Read anything. Only *create*
notes inside `000 AIOS/History/`, tagged `ai/monitored`. Keep AI-written and
hand-written notes clearly separated. Whenever a note is touched beyond reading,
set or correct its AI tag:

| tag | when |
|---|---|
| `ai/checked` | language or consistency pass, no deeper content change |
| `ai/assisted` | more than cosmetic: parts written, formulas changed or adjusted |
| `ai/monitored` | AI maintains part or all of the note on a regular basis |

**Link generously, but only to notes that exist.** Wikipedia rule: link the
first meaningful mention, not every occurrence. If a link would point at a note
that does not exist yet, flag it and let Julius decide rather than creating it
silently.

`me.md` also states general working preferences, and those are not vault-only.
They apply to work in this repo as well, so read it rather than guessing.

## Commands

```bash
# Install in editable mode (uv is used in this project)
uv sync
# or: pip install -e .

# Run all tests
pytest

# Run a single test
pytest tests/test_colors.py::test_rgb_to_hex
```

## Conventions

- **Docstrings**: NumPy/SciPy style (summary line, then `Parameters`, `Returns`, `Raises`, `Notes` sections as applicable). Follow this convention for any docstring you write or edit.
- **Type hints**: all function and method signatures (parameters and return types) should be fully typed.

## Text & plot style conventions

Applies to code comments, docstrings, printed/repr output, and any figure text this library produces or that callers build with it (titles, axis labels, tick labels, legends, annotations). The same rule set lives in `me.md` in the Obsidian vault and in the sibling repos' `CLAUDE.md` files; keep them in sync if this changes. Any change to a style, plotting or typography rule also goes into the vault note `100 Notes/My PhD Style Guide.md` (the distributable style guide; update the affected section, the quick reference, *Still to do* and the change log).

- No em dashes ("—"). Use a comma, period, or separate sentence instead.
- Capitalize only in headers/titles, proper nouns, or where otherwise grammatically correct. Axis labels, tick labels, legend entries, and other in-plot text are lowercase by default.
- Axis labels use the format `quantity / unit` (the quantity divided by its unit), e.g. `time / s`, `temperature / K`. If the quantity is dimensionless, use an en dash "–" in place of the unit, e.g. `fraction / –`.
- Units and exponents use power notation, not slashes: `m^2 s^-1`, `mol m^-3 s^-1`, not `m^2/s`, `mol/m^3/s`. Applies in code, plots, printed output, and LaTeX math. In Obsidian notes, `\frac{}{}` fraction style is fine in math environments; code and plots still use the power form.
- Chemical species, formulas and reactions use the mhchem `\ce{}` package, always inside math: `$\ce{CO2}$`, `$\ce{Cu^0}$`, `$\ce{Al^3+}$`, `$\ce{CO2 + 3H2 <=> CH3OH + H2O}$`. Applies to Obsidian notes and LaTeX (thesis). Plain text stays only where math cannot render: file names/note titles, wikilinks, frontmatter, and code. Plot labels (set 2026-10-18): matplotlib has no mhchem, so a species standing as a name (legend entry, annotation) is written `$\mathsf{CO_2}$`, `$\mathsf{Al^{3+}}$`, `$\mathsf{CO_2 + 3H_2 \rightleftharpoons CH_3OH + H_2O}$`: `\mathsf` resolves to Source Sans 3, so the formula matches the words beside it. A species as the subscript of a quantity stays `\mathrm` (`$S_\mathrm{MeOH}$`, `$E_\mathrm{a}$`) to match the maths symbol it hangs on. Not `$\mathrm{CO_2}$` for a bare species: on print presets that comes out in Source Serif 4, a serif formula in sans text. Rendered comparison: `phd_ui/docs/style_comparison/formulas.png`.
- Fonts: two families, both open and bundled in `phd_ui`: Source Sans 3 and Source Serif 4. Source Sans 3 is used for all figure and slide text, with hierarchy by size and weight, never a second sans. Maths matches the body text it sits beside: Source Serif 4 in print figures and the thesis body, Source Sans 3 italic on slides. Words and units upright, quantities italic. Matplotlib uses mathtext, not usetex. Slides use Source Sans 3 (embedded in the pptx) instead of Segoe UI. Thesis: LuaLaTeX, Source Serif 4 body, Source Sans 3 headings and captions, unicode-math with Source Serif 4 letters over STIX Two Math symbols. Details, preamble and open to-dos: `phd_ui` CLAUDE.md, section *Typography*.
- Citing a paper where the reference stands alone, on a slide or in a source line on a figure (set 2026-10-18; not for running text, where the document's own citation style applies, numbered or a short author-year form, and the bibliography follows that same style): `<first author> et al. (<group lead>), <journal abbreviation> <year>`, e.g. `Vico van Berkel et al. (Urakawa), J. Catal. 2024`. The bracket names the professor or well-known name behind the paper, usually the last author, and is dropped when the first author is that name (`Urakawa et al., J. Phys. Chem. C 2019`). Two authors: `Maeder & Zilian, Chemom. Intell. Lab. Syst. 1988`; one: `Noda, Appl. Spectrosc. 1993`. Journal abbreviations as Zotero gives them (ISO 4, with dots). `text.cite()` builds the string; in the vault it sits beside the Zotero wikilink, which stays `[[@Key.Title.Year]]`.

## Plotting conventions

**This is the canonical copy.** These rules govern every figure built on
`phd_ui`, in this repo and in every caller (`phd_execute` notebooks above all).
The sibling repos point here rather than restating them; when a rule changes,
it changes here. Examples are written as `plotting.<fn>`; callers that import
the package as `ui` read that as `ui.plotting.<fn>`.

### Reach for a helper before writing matplotlib by hand

If `phd_ui` has a function for it, use it. Sizing, saving, tick locators,
colours and colormaps, species colours: none of it gets reimplemented at the
call site. The ones that come up constantly:

| instead of | use |
|---|---|
| `figsize=(7.1, 3.5)` | `plotting.get_figsize("double_single")` |
| `fig.savefig(...)` twice for png + pdf | `plotting.save_figure(fig, dir_figures, name)` |
| `ax.xaxis.set_major_locator(MultipleLocator(...))` + `AutoMinorLocator` | `plotting.set_locators(ax, minor_x=…, minor_y=…, major_x=…, major_y=…)` |
| `"tab:blue"`, `"#1f77b4"`, `viridis`, `"0.3"` | `colors.BLUE.line` for a line or marker, `colors.BLUE.base` for a fill, `colors.SPECIES["MeOH"].color`, `colors.create_colormap_from_cmap(...)` |
| `ax.secondary_xaxis("top", functions=(lambda v: 1000/v - 273.15, …))` | `plotting.add_inverse_temperature_axis(ax, ticks=[…])`, or `add_reciprocal_axis` for the general case |
| `fig.set_layout_engine("none")`, `fig.tight_layout()` | `plotting.freeze_layout(fig)` |
| hand-drawn `Circle`s for atoms, CPK colours typed in | `plotting.draw_molecule(ax, atoms, bonds)`, colours from `colors.ATOMS` |
| hand-rolled rotated text along a curve | `plotting.draw_curve_label(ax, x, y, text, at_x=…, offset=…)` |
| `fig.legend(..., bbox_to_anchor=(…, …))` for a legend that does not fit inside the axes | `plotting.legend_above(fig)` |
| small multiples whose panels must keep one physical size while the grid grows (`plt.subplots` shrinks them instead) | `plotting.panel_grid(nrows, ncols, panel_cm=3.5)`, with `merge=[(rows, cols)]` for a panel spanning several cells; or `plotting.panel_mosaic(layout)`. The width depends on content here, the one `get_figsize` exception |

Get the live inventory from the package (`dir(plotting)`, `dir(colors)`) rather
than from this table; the table is a reminder, not the list.

### Line tones for lines, fill tones for fills

Every scheme hue has four fill tones (`light`, `base`, `dark`, `darkest`)
and one line tone (`line`). **A plotted line or marker takes `.line`; a
band, patch or drawn shape takes `.base` (or another fill tone).** The
fill tones were chosen on filled boxes in a drawing and are deliberately
mid-chroma, which is right there and wrong on a 1 pt stroke: a thin line
is perceived less saturated than the same colour as an area, so blue and
amber `base` fall to 2:1 against white and read as pastel. `.line` is the
same hue with the chroma lifted and the lightness pinned to the band line
palettes use, see *Line tones* in `colors/scheme.py` for the numbers.

`SCHEME_LINE` is the default `axes.prop_cycle` in every preset, so an
`ax.plot` without `color=` already comes out right. Species colours follow
the same split: `SPECIES[name].color` (and `SPECIES_COLORS`) for a trace,
`.fill` (`SPECIES_FILL_COLORS`) for a drawing. Red, pink and orange lie
within 41 degrees of hue, so two of them on one panel also need a line
style or a direct label; the inert greys separate by lightness only.

### Always size figures with `get_figsize`

**Never hardcode a `figsize` tuple.** Every figure takes its size from the
shared table:

```python
fig, ax = plt.subplots(figsize=plotting.get_figsize("double"))
```

- **It returns inches by default** (changed 2026-07; it used to default to cm
  and every call site had to pass `in_metric=False`). Pass `in_metric=True`
  only when you actually want the stored centimetres, e.g. to print a size or
  compare against a template.
- **Keys are named for the target column width**, not for a shape: `single_*`
  = 9 cm (one journal column), `double_*` = 18 cm (full width), `slide_*` for
  talks. On the document keys the suffix sets the height: `_short` 4.5, none
  6.5 (single) / 11.5 (double), `_square`, `_double`, `_long` 24 cm. The slide
  keys carry their own suffixes, see the next bullet. Get the live list with
  `get_figsizes()`; it is the authority, this list is a summary.
- **Slide keys say how much of the slide the figure fills, not which deck it is
  for.** They are cut from the *body box*, 31 × 14.5 cm, which is a 16:9 canvas
  (`SLIDE_CANVAS`, 33.87 × 19.05) minus a 1.4 cm side margin, a 3.3 cm title
  band and a 1.25 cm bottom margin; `SLIDE_BODY` holds it and a test keeps the
  table inside it. Half that width plus a 2 cm gutter is 14.5 cm again, so the
  half-width and square keys share a width:

  | key | cm | for |
  |---|---|---|
  | `slide_short` | 31 × 6.5 | a band across the body, text under it |
  | `slide` | 31 × 10 | full width, room left for a takeaway line |
  | `slide_full` | 31 × 14.5 | the hero figure, everything under the title |
  | `slide_half` | 14.5 × 10 | one of two side by side |
  | `slide_square` | 14.5 × 14.5 | square at full body height, or beside bullets |
  | `slide_full_16x9` | 33.87 × 19.05 | true full bleed, no title. Rare |

  Aspect ratio is deliberately not in the names: 16:9 and 4:3 decks are the
  same height and differed only in usable width, and the reason to reach for a
  slide key is the 2x point size, not the shape of the deck. `slide_16x9` and
  `slide_4x3` now raise, pointing at `slide_full`; `slide_tall` at
  `slide_square`.
- **An unknown key raises** `FigsizeKeyError` (a `KeyError`), listing every
  available key and naming the replacement if one of the retired names was
  used (`double_single_height` → `double_single`, `double_small` →
  `double_short`, `fullpage` → `double_long`, plus the three slide keys
  above). It used to warn and fall back to matplotlib's default, so typos
  quietly produced wrongly-sized figures.
- For a grid whose height must scale with its content, **take the width from
  the table and compute only the height**, which keeps the column width right
  while letting the figure grow:
  ```python
  figsize=(plotting.get_figsize("double")[0], 1.45 * nrow)
  ```
  A figure whose *width* genuinely depends on content (an N×M parity grid, say)
  is the one legitimate exception; leave it computed and say so in a comment.

The point is that every figure destined for the same thesis, paper or talk
shares one width, so nothing gets rescaled on import and font sizes stay
consistent across figures.

### Font size comes from the preset, and slides get 2x

**Do not pass `fontsize=` at the call site.** `update_params_string(key)` sets
both the figure size and the point sizes that suit the medium, so pick the
preset and let it decide:

- **print keys** (`single_*`, `double_*`): 8 pt base, 9 pt axis labels, 8 pt
  ticks and legend. That is the publisher window (5-9 pt) and matches 10 pt
  body text at reading distance.
- **slide keys** (`slide_*`): **2x everything**, so 16 pt base, 18 pt labels,
  and doubled line widths, tick lengths and pads.

One point size cannot serve both media, and it should not. Absolute point size
is the right invariant *within* a medium, since every figure in a paper shares
a page and every figure in a talk shares a slide canvas. Between media it
breaks: a 16:9 canvas is 33.9 cm against a 16–18 cm text block, and is read
from metres rather than arm's length, so 8 pt on a slide subtends roughly half
the angle 10 pt body text does on paper. Scaling only the text would leave
hairline axes beside large labels, so everything measured in points scales
together (`scale_for_key`, `SLIDE_SCALE = 2.0`, see Architecture below).

If a figure genuinely needs a third scale, apply one
(`update_params(get_params(1.5))`) rather than patching individual `fontsize=`
arguments, which is how older notebooks ended up with a spread of 5 to 11.5 pt
inside one project.

### Typography: one sans for text, maths follows the medium

Decided 2026-10-18. Two families, both bundled in `_assets/fonts/`, both
open (OFL), designed as a pair by Adobe: **Source Sans 3** and **Source
Serif 4**. Nothing else, in figures, slides or thesis.

**General rules**

1. **One sans for all figure and slide text.** Source Sans 3: labels, ticks,
   legends, annotations, slide titles and bullets. Hierarchy comes from size
   and weight, never from a second sans.
2. **Maths matches the body text it sits beside.** A variable in a figure
   looks like the same variable in the paragraph or bullet next to it. This
   rule, not taste, picks the maths font.
3. **At most two families per document**, one serif and one sans, from the
   same design family.
4. **Upright for names, italic for variables.** Words, units, species and
   descriptive subscripts are upright (`$S_\mathrm{MeOH}$`,
   `$E_\mathrm{a}$`, `$\mathsf{CO_2}$`); quantities are italic.
5. **Mathtext, not `usetex`.** `text.usetex` stays off: mathtext is fast,
   needs no TeX install, and lets the preset choose the maths font.

**Per medium**

| medium | text | maths | status |
|---|---|---|---|
| print figures (`single_*`, `double_*`) | Source Sans 3 | Source Serif 4, to match the thesis body | in params now |
| slide figures (`slide_*`) | Source Sans 3 | Source Sans 3 italic, to match the slide text | **to do** |
| slides (PowerPoint text) | Source Sans 3, embedded in the pptx | Cambria Math is PowerPoint's only option; put real equations in a figure instead | **to do**: replaces Segoe UI |
| thesis body | Source Serif 4 | `unicode-math`, Latin letters, digits and Greek from Source Serif 4 | **to do**: no template yet |
| thesis headings, captions, tables | Source Sans 3 | as body | **to do** |

Why the slide maths changes: a serif $E_\mathrm{a}$ in a figure on a sans
slide is the one place the current setup looks dated, and on a slide there
is no serif body text for it to match. Why Segoe UI goes: it ships only
with Windows, so on a Mac or a conference laptop it is replaced by whatever
is there; it cannot be bundled; and the figures beside it are Source Sans 3
anyway. Source Sans 3 looks nearly the same, so nothing jumps.

**To do, in order**

1. *Slide maths in params.* In `get_params`, when `scale` is the slide
   scale, set `mathtext.rm` to `Source Sans 3`, `mathtext.it` to
   `Source Sans 3:italic`, `mathtext.bf` to `Source Sans 3:bold`, and
   `mathtext.fallback` to `stixsans` (symbols the text font lacks, such as
   the integral sign, then come from a sans). The cleanest home is a
   `math_family` argument picked by `scale_for_key`'s caller, the way the
   point sizes are.
2. *Slides.* Set the slide master's theme fonts (heading and body) to
   Source Sans 3; install it from `_assets/fonts/Source_Sans_3/` on every
   machine you present from, and tick File > Options > Save > *Embed fonts
   in the file* (all characters) for decks that leave your laptop.
3. *Thesis.* LuaLaTeX, with this preamble as the starting point:

   ```latex
   \usepackage{fontspec}
   \usepackage{unicode-math}
   \setmainfont{Source Serif 4}
   \setsansfont{Source Sans 3}
   % symbols from a complete maths font, letters from the body font
   \setmathfont{STIX Two Math}
   \setmathfont{Source Serif 4}[range=up/{latin,Latin,num}]
   \setmathfont{Source Serif 4 Italic}[range=it/{latin,Latin,greek,Greek}]
   \usepackage[version=4]{mhchem}  % \ce{} follows the text font
   % headings and captions in the sans, as the figures
   \usepackage{sectsty}\allsectionsfont{\sffamily}
   \usepackage[font=sf]{caption}
   ```

   If the thesis ends up in classic Computer Modern instead, set the print
   presets' `mathtext.fontset` to `cm`. The mismatch is the mistake, not
   either font.

The same rule set lives in the vault's `me.md` under *Text & Plot Style
Conventions*; when this section changes, carry the per-medium table there.

### Never call `fig.tight_layout()` or `fig.subplots_adjust()`

Constrained layout is on in every preset with a zero outer pad, so the drawn
content fills the canvas and the saved file is exactly the width `get_figsize`
asked for. Both of those calls warn ("The figure layout has changed to tight")
and revert the figure, after which `savefig(bbox="tight")` trims the margin and
the file lands 5-20 % narrower than requested, by an amount that depends on how
much label text that figure happens to carry. Placed at a fixed width in LaTeX
or PowerPoint it is then scaled back up, and its effective point size no longer
matches the figure beside it.

Nothing is gained by reverting. Measured on a 2×2 grid at `double`, as the
fraction of the figure width the axes actually span: constrained **0.929**,
`tight_layout()` 0.895, no engine 0.775. Constrained gives *more* plot area,
and is the only one whose saved file matches the requested width.

Tuning knobs, reached through the engine after the figure exists:

```python
fig.get_layout_engine().set(wspace=0.08, hspace=0.08)
```

| knob | unit | effect | keeps the saved size exact? |
|---|---|---|---|
| `wspace`, `hspace` | fraction of figure width/height | gap *between* panels | yes (measured 1.000) |
| `w_pad`, `h_pad` | inches | margin *outside* everything | no (1.4 % lost at 0.05 in) |
| `rect` | figure fraction | confine the layout to a sub-rectangle | no |

`wspace`/`hspace` are the equivalent of `tight_layout(w_pad=…, h_pad=…)` and
cost nothing. Avoid `w_pad`/`h_pad`: they inset the content from the canvas
edge and `savefig(bbox="tight")` trims that inset straight back off, putting
you back to a file narrower than requested.

**The rim around the file is `savefig.pad_inches`, and it is not zero.**
`SAVEFIG_PAD_IN = 0.08` in (0.16 on a slide key) is added outside the tight
bbox, so nothing sits flush against the edge of the PDF or of a notebook cell
and a figure looks finished on its own, not only inside a LaTeX float. A
*constant* pad is safe where the two knobs above are not: constrained layout
makes the tight bbox equal the canvas, so every figure grows by the same
2 × pad and two of them placed at one width still share an effective point
size. Override per call with `save_figure(..., pad=…)`; `pad=0.0` gives a file
trimmed flush to the content.

For genuine manual positioning (axes that must align pixel-for-pixel across two
figures, an inset at an exact spot), freeze the engine with
`plotting.freeze_layout(fig)`, then `fig.subplots_adjust(...)`, and save with
`bbox_inches=None`, otherwise the tight bbox deletes the margins you just set.
Do not reach for `fig.set_layout_engine("none")`: it raises `RuntimeError` once
the figure has a colorbar.

### Axis limits and ticks: set them, do not let matplotlib guess

Limits and major tick spacing are chosen *together*, with
`plotting.set_locators(ax, minor_x=…, minor_y=…, major_x=…, major_y=…)` doing
the spacing half.

- **A major tick lands on each end of the axis.** Pick the limits and the major
  spacing so the range is a whole number of intervals, e.g. `set_xlim(0.75, 2.25)`
  with `major_x=0.25`, not `(0.74, 2.34)` with `major_x=0.2`, which leaves a
  stub of an interval hanging past the last labelled tick at both ends. A
  half-interval at the end of an axis reads as an accident and makes two figures
  of the same quantity harder to compare.
- **Start at the quantity's natural zero, and end at its natural ceiling, where
  it has one.** Conversion, selectivity and yield are `0-100 %`; a mole
  fraction, a coverage or a normalised intensity is `0-1`; a count is `0-n`. Do
  not let autoscaling crop such an axis to the data range, since it exaggerates
  small differences and hides how much headroom is left. This is about the
  quantity, not about the data: a conversion that only reaches 12 % still gets a
  0-100 % axis unless the figure is specifically about resolving that 12 %, and
  then say so in a comment.

  A quantity with no natural zero is exempt and must not be forced to one:
  temperature, wavenumber, pressure on a log axis, a residual or bias, and
  anything logarithmic (`ln K`, `log10 X`, absorbance ratios) take limits from
  the data plus the first rule.

### A legend that does not fit inside the axes goes above them, on the right

Put the legend **inside** the axes wherever it fits, in a corner the data
leaves free. When it does not fit, it goes **above the figure, right-aligned**,
as one row:

```python
plotting.legend_above(fig)                  # entries collected off the axes
plotting.legend_above(fig, handles, labels, ncol=3)
```

Not below the panels, where it competes with the x label and its ticks and is
read after the data instead of before it. Not squeezed inside at the cost of
overlapping points. Right-aligned because the axes' right edge is the one edge
every panel of a row shares with the figure itself; a centred strip is aligned
to nothing and drifts sideways as entries are added.

The helper anchors the strip *outside* the canvas, at `1 + pad` in figure
coordinates. That is the same mechanism `savefig.bbox = "tight"` gives the rest
of the library: the saved file grows to include an artist placed outside the
canvas, so the axes keep the exact rectangle `get_figsize` asked for and only
the file's height grows. `loc="outside upper center"` instead hands the strip
to constrained layout, which makes room by shrinking the panels, and a figure
built that way no longer overlays a sibling figure of the same preset.

One row is the default (`ncol` = one entry per column). If the row is too wide
for the figure, shorten the *names* first, then fall back to `ncol=`. `align=`
takes `"left"` and `"center"` for a figure whose top-right corner is already
spoken for.

### No footnotes or captions on the figure

**Do not put explanatory text on a figure.** No `fig.text` footnote, no
`supxlabel` used as a caption, no note wedged under the axes explaining what a
glyph means or how to read a panel. Ask first, and only add one when Julius
says yes.

The figure carries the plot: axis labels, tick labels, a legend of **names**,
and annotations that point at a specific datum. Anything needing a sentence is
prose, and it belongs where prose belongs, in the notebook markdown cell above
the plot, in the slide's own text, or in the paper's caption. A figure that has
to explain itself in a paragraph is being asked to do the surrounding
document's job.

Practical reasons on top of the editorial one: `savefig.bbox = "tight"` means a
long line grows the canvas sideways and silently breaks the figure's aspect
ratio, a caption sized for print is unreadable at slide scale and vice versa,
and the text has to be re-edited in two places once the same figure is reused.

A **legend entry is a name, not a sentence**: `$S_\mathrm{MF}$`, not
`$S_\mathrm{MF}$, fixed at 0.045 without an MF route`. If a key cannot be
understood from its name, explain it in the surrounding prose.

### No titles either

**Do not set a title.** No `ax.set_title` on a single-panel figure, no
`fig.suptitle`, ever. The figure is the plot. A title is the surrounding
document's job: a slide has a title box, a paper has a caption, a notebook has
the markdown cell above the one that drew the plot. Put it there and it can be
rewritten without regenerating the figure, and it comes out at the medium's own
type size rather than at the figure's.

**A panel identifier is not a title.** In a multi-panel figure the short label
saying which panel is which, the quantity, the feed, `a` / `b` / `c`, stays:
the reader needs it to read the panel at all, and it is in the same class as an
axis label or a legend entry. A one-line claim is the opposite ("every rate law
finds the same slope"): that is the argument, and the argument belongs in prose.

Same reasoning as the section above, plus one of its own: a title is the first
thing that changes when a figure is reused, and a figure that has to be
regenerated to be retitled will be retitled in the wrong place instead.

### Saving

`plotting.save_figure(fig, path, name)` writes **png + pdf**. SVG is off by
default; pass `as_svg=True` only for a figure that will actually be opened in
Illustrator. Where the files go is the caller's business: `phd_execute` mirrors
its project folders into `[figure_dump]/<project>/`, and its `CLAUDE.md` owns
that rule.

## Architecture

`phd_ui` is a Python library (Python ≥ 3.13, src-layout) that provides matplotlib styling, the PhD colour scheme and species colours, and colormap helpers for PhD research figures. Species renaming is not here: it lives in `phd_parser.naming.species`.

### Entry point: `initialize()`

`phd_ui.initialize()` (defined in `__init__.py`) is the intended first call in any script. It registers bundled fonts with matplotlib and applies the default `"single"` rcParams preset via `plt.rcParams.update`.

### `plotting/` — figure styling

- **`params.py`** defines `get_params(scale)`, which builds the full rcParams `dict` (font, tick, line, legend, layout, savefig) with every point-valued entry multiplied by `scale`. `BASE_PARAMS = get_params()` is the print set, kept as a name for backwards compatibility. Source Sans 3 is used for body text; Source Serif 4 for math (`mathtext`).
- **`figsize.json`** (`_assets/`) stores canonical figure widths/heights in cm. Two families: document presets — a full height × width matrix at 9 cm (`single_short`, `single`, `single_square`, `single_double`, `single_double_square`, `single_long`) and 18 cm (`double_short`, `double_single`, `double_single_square`, `double`, `double_square`, `double_long`) — and presentation presets cut from the slide body box (`slide_short`, `slide`, `slide_full`, `slide_half`, `slide_square`, plus the full-bleed `slide_full_16x9`). `SLIDE_CANVAS` and `SLIDE_BODY` in `figsize.py` hold the two boxes those slide sizes are derived from, and `tests/test_figsize.py` checks every slide key still fits the body box. See the README for a per-preset "when to use" guide.
- **`core.py`** builds the `PARAMS` dict at import time: `{key: {**get_params(scale_for_key(key)), "figure.figsize": FIGSIZE[key]} for key in FIGSIZE}`. `FIGSIZE` values are the JSON sizes converted to inches. Call `update_params_string("double")` to switch presets; it accepts `**kwargs` overrides, which apply to that call only.

  The scale attached to each key (`scale_for_key`, `SLIDE_SCALE = 2.0`) and the layout settings (`figure.constrained_layout.use` with `w_pad = h_pad = 0`, `savefig.bbox = "tight"` with `pad_inches = SAVEFIG_PAD_IN * scale`) are the mechanism behind "Plotting conventions" above. `savefig.bbox` stays `"tight"` as a safety net: under constrained layout it is a no-op on the content, but an artist deliberately placed outside the canvas grows the file rather than being silently clipped. `SAVEFIG_PAD_IN = 0.08` in is the rim outside that bbox, a constant so it cannot vary the content-to-canvas ratio between figures.
- **`core.py`** also holds the axis helpers: `set_locators`, `fix_right_ylabels`, `freeze_layout`, `legend_above`, and the reciprocal-axis pair. **`legend_above(fig)`** is the house placement for a legend that does not fit inside the axes, see "Plotting conventions" above: one row over the top of the panels, right-aligned, anchored outside the canvas so the panels keep their rectangle. Entries are collected off the figure's axes and de-duplicated by label, so a row of panels sharing one set of series needs no `handles`/`labels` argument. **`add_reciprocal_axis`** puts a second axis on a spine showing `v` where the plotted one carries `scale / (v + offset)`; **`add_inverse_temperature_axis`** is that with the temperature conversion and the house label pre-filled, for van 't Hoff and Arrhenius plots. Both default to `hide_primary=True`, which is nearly always right: `xtick.top`/`ytick.right` are on, so otherwise a second unlabelled set of reciprocal ticks interleaves with the new ones.
- **`freeze_layout(fig)`** stops constrained layout re-running, for anything positioned from measured geometry (rotated curve labels, gaps sized from rendered text). Draw once, freeze, then place. **Use it instead of `fig.set_layout_engine("none")`**, which raises `RuntimeError` the moment the figure has a colorbar; this installs a placeholder engine carrying the current engine's own flags, the way `Figure.tight_layout` restores itself.
- **`draw.py`**: `draw_peak`, `draw_vscale` (vertical intensity scale bar), `draw_colorbar`, and **`draw_curve_label(ax, x, y, text)`**, which writes a label onto a curve rotated with its local slope, so a curve names itself and needs no legend entry. Pass `line=` to have that artist broken around the label the way `clabel` breaks a contour; `offset` is perpendicular in points, positive above the curve. The tangent is flipped to point rightwards on screen first, so a curve stored back-to-front (a `1/T` axis, a descending wavenumber axis) still gets an upright label. It measures rendered geometry, so call it after `fig.canvas.draw()` and after `freeze_layout`.
- **`export.py`**: `save_figure(fig, path, name)` writes **PNG and PDF** (`as_png=True`, `as_pdf=True`), always with a tight bbox and the preset's rim; `pad=` overrides that rim for one call and `pad=0.0` trims flush. **SVG is off by default** (`as_svg=False`): pass `as_svg=True` only when a figure is actually going to be edited downstream, e.g. in Illustrator. SVGs of these figures are large and were being written on every save for no reason.
- **`matrix.py`**: block diagrams of matrix equations, added 2026-10-18 for the chemometrics tutorials. `draw_matrix(ax, x, y, rows, cols, label)` draws one matrix as a rectangle whose drawn width and height stand for its columns and rows (the caller picks drawn sizes, a 101 × 201 data matrix with three species would make the factors invisible), with optional dimension labels, a title and highlighted column or row `Stripe`s; `draw_matrix_equation(ax, [Term(...), "=", Term(...), Term(...), "+", Term(...)])` lays a whole equation out left to right (`align` top, centre or bottom), operators as text one unit wide or `(text, width)` for a long one, and sets equal aspect and no frame unless `autoscale=False` (several equations on one axes, the caller sets the limits). Fill `light`, edge `dark`, symbol `darkest` of the term's colour family; line widths follow the preset scale like `molecule.py`. Returns an `Equation` with the `Block`s (edges, centre, and every artist drawn for the block, so a reveal step can toggle it) and the operator texts. The MCR tutorials in `phd_execute/runs_tutorials/chemometrics/mcr/` are the worked examples.

### `text.py`

`cite(first_author, journal, year, lead=None, *, second_author=None, et_al=True)` builds the house citation string of "Text & plot style conventions": `Vico van Berkel et al. (Urakawa), J. Catal. 2024`, `Maeder & Zilian, Chemom. Intell. Lab. Syst. 1988`, `Noda, Appl. Spectrosc. 1993`. Exposed as `phd_ui.text`.

### `colors/` — color utilities

- **`scheme.py`**: the PhD colour scheme. Ten `ColorFamily` hues, each with the four fill tones `light`/`base`/`dark`/`darkest` and the line tone `line`; `SCHEME` keys them by name, `SCHEME_COLORS` lists the base tones, `SCHEME_LINE` the line tones in the cycle order that keeps adjacent entries apart under normal and colour-deficient vision (brute-forced over all orders, worst adjacent OKLab dE x100 of 17.6 normal / 9.2 simulated). `params.py` imports `SCHEME_LINE` for `axes.prop_cycle`, which is why `preview.py` imports plotting lazily inside its functions: the other way round would be a circular import.
- **`base.py`**: `SPECIES` maps species abbreviations (H2, CO, MeOH, …) to a `Species` with `color` (line tone, for traces) and `fill` (fill tone, for drawings), both looked up from the scheme so hue encodes role. `SPECIES_COLORS` and `SPECIES_FILL_COLORS` are the flat `{name: hex}` views.
- **`nature.py`**: `NATURE`, the Nature-branded palette (eleven six-step families: background, main accents, extended) for conceptual drawings in Nature's house style, with `nature_colors` and `nature_cmap`. The values are those of `hoanglongcao/nature-plot-style`, read off Nature's palette SVG; the guide is `docs/natrev-artworkguide.pdf`.
- **`wong.py`**: `WONG`, the eight colours of Wong (2011, *Nature Methods*, the Okabe-Ito set), with the paper's accessibility rules mapped onto the scheme in the docstring. Paper at `docs/wong2011-color-blindness.pdf`.
- **`atoms.py`**: `ATOMS` and `BOND_STYLES`, the one reference for drawing atoms and bonds (figures, IR-bands, Illustrator). CPK hues toned to the scheme, flat fill plus darker edge, carbon `GREY.darkest` and never black, radius = covalent radius (Cordero 2008). Ball and stick draws radii at `BALL_SCALE = 0.5` with centres at the true bond length (`bond_length_pm`), so the visible bond is about half the centre distance; 1.0 is space-filling. Symbols go inside an atom only from `LABEL_MIN_DIAMETER_MM = 4` mm at final size, never in H. IR-bands' `frontend/src/lib/elementColors.ts` copies these colours: change them here first. `plotting/molecule.py` holds `draw_atom`, `draw_bond`, `draw_molecule` (pm, equal aspect, bonds under atoms, line widths follow the preset scale).
- **`preview.py`**: `plot_swatches`, `plot_ramps`, `plot_demo`, `plot_species`, `plot_nature`, `plot_wong`, `plot_atoms` and `save_previews`; `example/color_scheme.py` writes them into `docs/colorscheme/`.
- **`manipulation.py`**: `hex_to_rgb` / `rgb_to_hex` (supports `"int"` and `"float"` modes), `adjust_saturation` (absolute or relative HSV saturation), `create_saturation_palette`.
- **`cmaps.py`**: `create_colormap_from_color` (saturation ramp around a base hex color) and `create_colormap_from_cmap` (sub-sample an existing matplotlib colormap). Both return either a `LinearSegmentedColormap` or a hex list depending on `as_hex`.

### `fonts/`

`load_fonts(fonts_dir)` recursively finds all `.ttf`/`.otf` files under the given directory and registers them with `matplotlib.font_manager`. Called automatically by `initialize()`.

### Assets (`_assets/`)

| File | Contents |
|------|----------|
| `figsize.json` | Figure size presets in cm |
| `fonts/Source_Sans_3/` | Body/UI font |
| `fonts/Source_Serif_4/` | Math text font |
