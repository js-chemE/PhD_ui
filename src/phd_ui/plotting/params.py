BASE_WIDTH = 0.8

BASE_PARAMS = {
    # ----------------------------------------------------
    # figure
    # ----------------------------------------------------
    # "figure.figsize": FIGSIZE["double"], is added in core.py to allow dynamic updates via update_params_string
    "figure.dpi": 300,            # screen DPI (export handled by savefig)
    

    # ----------------------------------------------------
    # text
    # ----------------------------------------------------
    "font.family": "sans-serif",
    "font.sans-serif": ["Source Sans 3"],
    "font.size": 8,

    # math text (honest + consistent)
    "mathtext.fontset": "custom",
    "mathtext.rm": "Source Serif 4",
    "mathtext.it": "Source Serif 4:italic",
    "mathtext.bf": "Source Serif 4:bold",

    "axes.unicode_minus": False,
    
    # ----------------------------------------------------
    # lines
    # ----------------------------------------------------
    "lines.linewidth": 1.2,
    "lines.markersize": 4,

    # ----------------------------------------------------
    # axes
    # ----------------------------------------------------
    "axes.linewidth": BASE_WIDTH,
    "axes.titlesize": 9.5,   # slightly reduced → matches font metrics
    "axes.labelsize": 9,
    "axes.labelpad": 8,      # tighter, avoids wasted vertical space

    # ----------------------------------------------------
    # ticks
    # ----------------------------------------------------
    "xtick.top": True,
    "ytick.right": True,

    "xtick.labelsize": 8,
    "ytick.labelsize": 8,

    "xtick.major.size": 3,
    "ytick.major.size": 3,

    "xtick.minor.size": 1.5,
    "ytick.minor.size": 1.5,

    "xtick.major.width": BASE_WIDTH,
    "ytick.major.width": BASE_WIDTH,

    "xtick.minor.width": BASE_WIDTH,
    "ytick.minor.width": BASE_WIDTH,

    "xtick.major.pad": 3,
    "ytick.major.pad": 3,

    "xtick.direction": "in",
    "ytick.direction": "in",

    #"xtick.minor.visible": True,
    #"ytick.minor.visible": True,

    # ----------------------------------------------------
    # grid
    # ----------------------------------------------------
    "axes.grid": False,
    "grid.color": "0.5",     # neutral gray, print-safe
    "grid.alpha": 0.2,
    "grid.linewidth": 0.4,

    # ----------------------------------------------------
    # legend
    # ----------------------------------------------------
    "legend.frameon": False,
    "legend.fontsize": 7,
    "legend.handlelength": 2,
    "legend.handletextpad": 0.6,
    "legend.borderpad": 0.2,

    # ----------------------------------------------------
    # savefig
    # ----------------------------------------------------
    "savefig.bbox": "tight",
    "savefig.dpi": 300,
    "savefig.transparent": True,
    "savefig.format": "pdf",
}
