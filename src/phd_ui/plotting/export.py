from matplotlib.figure import Figure
from pathlib import Path

def save_figure(fig: Figure, figure_path: str | Path, name: str, dpi: int = 300) -> None:
    figure_path = Path(figure_path)
    fig.savefig(figure_path / f"{name}.png", dpi=dpi)
    fig.savefig(figure_path / f"{name}.pdf", dpi=dpi)