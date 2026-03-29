from matplotlib.figure import Figure

def save_figure(fig: Figure, figure_path: str, name: str, dpi: int = 300) -> None:
    fig.savefig(figure_path + rf"\{name}.png", dpi=dpi)
    fig.savefig(figure_path + rf"\{name}.pdf", dpi=dpi)