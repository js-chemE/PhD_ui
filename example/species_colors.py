"""
Render the phd_ui species colours and check them for accessibility.

The species palette is derived from the colour scheme, with the hue encoding
each species' role on a desirability axis: green = target (MeOH), blue = feed
(CO2, H2), purple/pink = side products (EtOH, MF, DME), red/amber = undesired
(CH4, CO), grey = inert (Ar, He, N2); water gets a literal ocean blue. This
script draws the palette grouped by role under normal, greyscale and
deuteranopic vision, and prints each colour with its role, so the mapping and
its colour-blind / mono legibility are both visible.

Writes ``species_colors`` (PNG + PDF + SVG) into ``docs/colorscheme/`` and
mirrors it into the shared figure dump:

    python example/species_colors.py
"""

import shutil
from pathlib import Path

import phd_ui
from phd_ui.colors import SPECIES, plot_species
from phd_ui.plotting import save_figure

phd_ui.initialize()

OUT = Path(__file__).resolve().parent.parent / "docs" / "colorscheme"
OUT.mkdir(parents=True, exist_ok=True)

# Mirror everything written to docs/ into the shared figure dump.
DUMP = Path(r"C:\Users\jsommer1\OneDrive\02_Projects\[UniZeug]\2024_PhD\01_Project\[figure_dump]") / "phd_ui" / "colorscheme"
DUMP.mkdir(parents=True, exist_ok=True)

# The mapping, as a quick text summary.
print(f"{'species':6s} {'hex':9s} {'role':10s} family")
for name, sp in SPECIES.items():
    print(f"{name:6s} {sp.color:9s} {sp.role:10s} {sp.family or '(literal)'}")

fig = plot_species(figsize_key="double")
save_figure(fig, OUT, "species_colors")
for f in OUT.glob("species_colors.*"):
    try:
        shutil.copy2(f, DUMP / f.name)
    except PermissionError:
        print(f"  (skipped locked file: {f.name})")

print("wrote species preview to", OUT, "and", DUMP)
