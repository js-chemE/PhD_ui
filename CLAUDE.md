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

## Architecture

`phd_ui` is a Python library (Python ≥ 3.13, src-layout) that provides matplotlib styling, color utilities, and data renaming helpers for PhD research figures.

### Entry point: `initialize()`

`phd_ui.initialize()` (defined in `__init__.py`) is the intended first call in any script. It registers bundled fonts with matplotlib and applies the default `"single"` rcParams preset via `plt.rcParams.update`.

### `plotting/` — figure styling

- **`params.py`** defines `BASE_PARAMS`: a flat `dict` of matplotlib rcParams (font, tick, line, legend, savefig settings). Source Sans 3 is used for body text; Source Serif 4 for math (`mathtext`).
- **`figsize.json`** (`_assets/`) stores canonical figure widths/heights in cm. Two families: document presets — a full height × width matrix at 9 cm (`single_short`, `single`, `single_square`, `single_double`, `single_double_square`, `single_long`) and 18 cm (`double_short`, `double_single`, `double_single_square`, `double`, `double_square`, `double_long`) — and presentation presets (`slide_16x9`, `slide_4x3`, `slide_half`, `slide_tall`). See the README for a per-preset "when to use" guide.
- **`core.py`** builds the `PARAMS` dict at import time: `{key: {**BASE_PARAMS, "figure.figsize": FIGSIZE[key]} for key in FIGSIZE}`. `FIGSIZE` values are the JSON sizes converted to inches. Call `update_params_string("double")` to switch presets; it accepts `**kwargs` overrides.
- **`export.py`**: `save_figure(fig, path, name)` saves to PNG, PDF, and SVG simultaneously (all flags default to `True`).

### `colors/` — color utilities

- **`base.py`**: `SPECIES_COLORS` dict maps chemical species abbreviations (H2, CO, MeOH, …) to their canonical hex colors.
- **`manipulation.py`**: `hex_to_rgb` / `rgb_to_hex` (supports `"int"` and `"float"` modes), `adjust_saturation` (absolute or relative HSV saturation), `create_saturation_palette`.
- **`cmaps.py`**: `create_colormap_from_color` (saturation ramp around a base hex color) and `create_colormap_from_cmap` (sub-sample an existing matplotlib colormap). Both return either a `LinearSegmentedColormap` or a hex list depending on `as_hex`.

### `renaming/` — species alias resolution

`Renaming` is a pydantic `BaseModel` that loads a JSON file mapping canonical names → list of aliases. `get_renaming(value)` accepts a `str`, `list`, or `pd.Series` and returns the canonical name. The JSON data lives in `_assets/renaming.json`.

> **Note**: `renaming/__init__.py` still references a non-existent `_renaming.xlsx` via `MAIN_RENAMING`. Instantiating `MAIN_RENAMING` directly will fail; use `Renaming.from_json(path)` instead.

### `fonts/`

`load_fonts(fonts_dir)` recursively finds all `.ttf`/`.otf` files under the given directory and registers them with `matplotlib.font_manager`. Called automatically by `initialize()`.

### Assets (`_assets/`)

| File | Contents |
|------|----------|
| `figsize.json` | Figure size presets in cm |
| `renaming.json` | Chemical species canonical names → aliases |
| `fonts/Source_Sans_3/` | Body/UI font |
| `fonts/Source_Serif_4/` | Math text font |
