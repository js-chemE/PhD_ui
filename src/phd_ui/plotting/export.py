from pathlib import Path

from matplotlib.figure import Figure

from phd_ui.plotting.params import SAVEFIG_PAD_IN


def save_figure(
    fig: Figure,
    figure_path: str | Path,
    name: str,
    dpi: int = 300,
    as_svg: bool = False,
    as_pdf: bool = True,
    as_png: bool = True,
    pad: float | None = None,
) -> None:
    """
    Write one figure to `figure_path` as PNG and PDF, and optionally SVG.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to write.
    figure_path : str or Path
        Directory the files go into. Not created; the caller owns where
        figures live.
    name : str
        File stem, without an extension.
    dpi : int, optional
        Resolution of the raster output. Default is 300.
    as_svg : bool, optional
        Also write SVG. Default is False. Pass True only for a figure that
        will actually be opened in a vector editor: these SVGs are large.
    as_pdf, as_png : bool, optional
        Write PDF / PNG. Both default to True.
    pad : float, optional
        Rim left around the figure, in inches. `None` (default) takes
        `savefig.pad_inches` from the active preset, which is
        `SAVEFIG_PAD_IN` scaled with the preset. Pass `0.0` for a file
        trimmed flush to the content.

    Returns
    -------
    None

    Notes
    -----
    The bounding box is always `"tight"`. Under constrained layout that is a
    no-op on the content, so the saved width stays the width `get_figsize`
    asked for plus the constant rim; it matters only when an artist has been
    placed outside the canvas on purpose (a legend hung below the axes, say),
    where it grows the file instead of clipping.
    """
    figure_path = Path(figure_path)
    pad_inches = SAVEFIG_PAD_IN if pad is None else pad
    kwargs = {"bbox_inches": "tight", "pad_inches": pad_inches, "dpi": dpi}

    if as_png:
        fig.savefig(figure_path / f"{name}.png", **kwargs)
    if as_pdf:
        fig.savefig(figure_path / f"{name}.pdf", **kwargs)
    if as_svg:
        fig.savefig(figure_path / f"{name}.svg", **kwargs)
