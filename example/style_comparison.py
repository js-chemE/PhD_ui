"""
Compare a figure in matplotlib's defaults with the same figure in phd_ui.

Writes into ``docs/style_comparison/``:

- ``default.png/.pdf`` and ``phd_ui.png/.pdf``: the same two-panel figure,
  same data, same label strings, same physical size (``double_single``),
  once with ``matplotlib.rcParamsDefault`` and once with the phd_ui preset.
- ``comparison.png``: both stacked, for a quick look.
- ``formulas.png/.pdf``: the ways of writing a chemical formula or a quantity
  in a label, each rendered next to its source string.

Run from anywhere:

    python example/style_comparison.py
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

import phd_ui
from phd_ui import colors, plotting

OUT = Path(__file__).resolve().parent.parent / "docs" / "style_comparison"
OUT.mkdir(parents=True, exist_ok=True)

FIGSIZE_KEY = "double_single"

# Labels are identical in both versions, so the only difference is the style.
LABEL_T = "temperature / °C"
LABEL_S = "selectivity / %"
LABEL_INV_T = r"$1000\,T^{-1}$ / K$^{-1}$"
LABEL_LNR = r"$\ln\,r$ / –"
SPECIES_LABELS = {
    "MeOH": r"$\mathsf{CH_3OH}$",
    "CO": r"$\mathsf{CO}$",
    "CH4": r"$\mathsf{CH_4}$",
}


# ----------------------------------------------------------------------------
# synthetic data: CO2 hydrogenation over a Cu catalyst
# ----------------------------------------------------------------------------
rng = np.random.default_rng(3)
T_model = np.linspace(200, 300, 101)
T_data = np.arange(200, 301, 12.5)


def selectivities(T: np.ndarray) -> dict[str, np.ndarray]:
    """Methanol falls, CO rises, a little methane at the hot end."""
    s_ch4 = 6 / (1 + np.exp(-(T - 290) / 8))
    s_co = (100 - s_ch4) / (1 + np.exp(-(T - 245) / 15))
    return {"MeOH": 100 - s_co - s_ch4, "CO": s_co, "CH4": s_ch4}


S_model = selectivities(T_model)
S_data = {k: v + rng.normal(0, 2.0, v.size) for k, v in selectivities(T_data).items()}

# Arrhenius: ln r = ln A - Ea / (R T)
R = 8.314e-3  # kJ mol^-1 K^-1
E_A = {"MeOH": 45.0, "CO": 105.0}  # kJ mol^-1
LN_A = {"MeOH": 7.0, "CO": 21.0}
inv_T = 1000 / (T_data + 273.15)
inv_T_model = np.linspace(1.72, 2.12, 50)
lnr_model = {k: LN_A[k] - E_A[k] / (R * 1000) * inv_T_model for k in E_A}
lnr_data = {k: LN_A[k] - E_A[k] / (R * 1000) * inv_T + rng.normal(0, 0.12, inv_T.size) for k in E_A}


def draw(fig: Figure, axs: np.ndarray, *, house: bool) -> None:
    """Draw both panels; `house` switches the phd_ui helpers on."""
    ax_s, ax_a = axs

    for name, label in SPECIES_LABELS.items():
        kw = {"color": colors.SPECIES[name].color} if house else {}
        (line,) = ax_s.plot(T_model, S_model[name], label=label, **kw)
        ax_s.plot(T_data, S_data[name], "o", color=line.get_color(), mfc="none")
    ax_s.set_xlabel(LABEL_T)
    ax_s.set_ylabel(LABEL_S)
    ax_s.legend()

    for name in E_A:
        kw = {"color": colors.SPECIES[name].color} if house else {}
        (line,) = ax_a.plot(inv_T_model, lnr_model[name], label=SPECIES_LABELS[name], **kw)
        ax_a.plot(inv_T, lnr_data[name], "o", color=line.get_color(), mfc="none")
    ax_a.annotate(
        r"$E_\mathrm{a} = 105$ kJ mol$^{-1}$",
        xy=(1.82, 21 - E_A["CO"] / (R * 1000) * 1.82),
        xytext=(1.88, -1.3),
        arrowprops={"arrowstyle": "-", "lw": 0.6, "color": "0.3"},
    )
    ax_a.set_xlabel(LABEL_INV_T)
    ax_a.set_ylabel(LABEL_LNR)

    if house:
        # Limits on whole intervals, natural 0-100 % for a selectivity.
        ax_s.set_xlim(200, 300)
        ax_s.set_ylim(0, 100)
        plotting.set_locators(ax_s, major_x=25, major_y=25, minor_x=5, minor_y=5)
        ax_a.set_xlim(1.72, 2.12)
        ax_a.set_ylim(-8, 0)
        plotting.set_locators(ax_a, major_x=0.1, major_y=2, minor_x=2, minor_y=2)
        plotting.add_inverse_temperature_axis(ax_a, ticks=[200, 225, 250, 275, 300], label=LABEL_T)
    else:
        # What one usually writes by hand for the top axis.
        sec = ax_a.secondary_xaxis(
            "top", functions=(lambda v: 1000 / v - 273.15, lambda v: 1000 / (v + 273.15))
        )
        sec.set_xlabel(LABEL_T)


figsize = plotting.get_figsize(FIGSIZE_KEY)

# --- matplotlib defaults, at the same physical size -------------------------
with mpl.rc_context(mpl.rcParamsDefault):
    fig, axs = plt.subplots(1, 2, figsize=figsize, layout="constrained")
    draw(fig, axs, house=False)
    fig.savefig(OUT / "default.png", dpi=300)
    fig.savefig(OUT / "default.pdf")
    plt.close(fig)

# --- phd_ui -----------------------------------------------------------------
phd_ui.initialize()  # registers the fonts; without it Source Sans 3 is not found
plotting.update_params_string(FIGSIZE_KEY)
fig, axs = plt.subplots(1, 2)
draw(fig, axs, house=True)
plotting.save_figure(fig, OUT, "phd_ui")
plt.close(fig)

# --- stacked preview (a review sheet, not a figure for a document) ----------
with mpl.rc_context(mpl.rcParamsDefault):
    imgs = [plt.imread(OUT / f"{n}.png") for n in ("default", "phd_ui")]
    w = 10
    h = sum(w * im.shape[0] / im.shape[1] for im in imgs) + 0.8
    sheet, axes = plt.subplots(
        2, 1, figsize=(w, h), layout="constrained",
        gridspec_kw={"height_ratios": [im.shape[0] / im.shape[1] for im in imgs]},
    )
    for ax, im, tag in zip(axes, imgs, ("matplotlib defaults", "phd_ui  (double_single)")):
        ax.imshow(im)
        ax.set_axis_off()
        ax.text(0, -0.02, tag, transform=ax.transAxes, va="bottom", fontsize=11, family="monospace")
    sheet.savefig(OUT / "comparison.png", dpi=150, facecolor="white")
    plt.close(sheet)

# --- formula guide ----------------------------------------------------------
ROWS = [
    ("plain text", '"CO2"', "CO2"),
    ("unicode subscript", '"CO₂"', "CO₂"),
    ("maths roman (print: serif)", r'r"$\mathrm{CO_2}$"', r"$\mathrm{CO_2}$"),
    ("maths sans (follows the text)", r'r"$\mathsf{CO_2}$"', r"$\mathsf{CO_2}$"),
    ("ion, oxidation state", r'r"$\mathsf{Al^{3+}}$, $\mathsf{Cu^0}$"', r"$\mathsf{Al^{3+}}$, $\mathsf{Cu^0}$"),
    ("reaction", r'r"$\mathsf{CO_2 + 3H_2 \rightleftharpoons CH_3OH + H_2O}$"',
     r"$\mathsf{CO_2 + 3H_2 \rightleftharpoons CH_3OH + H_2O}$"),
    ("quantity, upright subscript", r'r"$S_\mathrm{MeOH}$ / %"', r"$S_\mathrm{MeOH}$ / %"),
    ("unit exponent, maths", r'r"kJ mol$^{-1}$"', r"kJ mol$^{-1}$"),
    ("unit exponent, sans", r'r"$\mathsf{kJ\,mol^{-1}}$"', r"$\mathsf{kJ\,mol^{-1}}$"),
    ("unit exponent, unicode", '"kJ mol⁻¹"', "kJ mol⁻¹"),
]
plotting.update_params_string("double_single_square")
fig, ax = plt.subplots()
ax.set_axis_off()
ax.set_xlim(0, 1)
ax.set_ylim(len(ROWS) - 0.5, -0.5)
for i, (what, src, rendered) in enumerate(ROWS):
    ax.text(0.0, i, what, va="center", color=colors.SCHEME["grey"].darkest)
    ax.text(0.30, i, src, va="center", family="monospace", fontsize=6.5, parse_math=False)
    ax.text(0.80, i, rendered, va="center", fontsize=10)
plotting.save_figure(fig, OUT, "formulas")
plt.close(fig)

print("wrote", *sorted(p.name for p in OUT.iterdir()), "to", OUT)
