# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
- **`figsize.json`** (`_assets/`) stores canonical figure widths/heights in cm: `single`, `double`, `double_single_height`, `double_small`.
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
