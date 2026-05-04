from matplotlib.figure import Figure
from pathlib import Path

def save_figure(fig: Figure, figure_path: str | Path, name: str, dpi: int = 300, as_svg: bool = True, as_pdf: bool = True, as_png: bool = True) -> None:
    figure_path = Path(figure_path)
    if as_png:
        fig.savefig(figure_path / f"{name}.png", dpi=dpi)
    if as_pdf:
        fig.savefig(figure_path / f"{name}.pdf", dpi=dpi)
    if as_svg:
        fig.savefig(figure_path / f"{name}.svg", dpi=dpi)