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
    slide: bool | None = None,
    check: bool = True,
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
    slide : bool, optional
        Adapt the figure for a slide before saving (`layout.slide_ticks`:
        about three round major ticks per linear axis). `None` (default)
        decides from the active preset: on for `slide_*` keys.
    check : bool, optional
        Warn about layout problems (`layout.check_layout`): texts or legends
        leaving their axes or lying on data, axis labels longer than their
        axis, labels running into another panel. Default True.

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
    import warnings

    from phd_ui.plotting import core
    from phd_ui.plotting.layout import check_layout, slide_ticks

    figure_path = Path(figure_path)
    if slide is None:
        slide = bool(core.ACTIVE_KEY and core.ACTIVE_KEY.startswith("slide"))
    if slide:
        slide_ticks(fig)
    if check:
        for problem in check_layout(fig):
            warnings.warn(f"{name}: {problem}", stacklevel=2)
    pad_inches = SAVEFIG_PAD_IN if pad is None else pad
    kwargs = {"bbox_inches": "tight", "pad_inches": pad_inches, "dpi": dpi}
    # panel labels are kept out of the layout, which also keeps them out of the
    # default tight box; hand them in explicitly so the file grows to hold them
    from phd_ui.plotting.layout import PANEL_LABEL_GID
    tags = [t for ax in fig.axes for t in ax.texts if t.get_gid() == PANEL_LABEL_GID and t.get_visible()]
    if tags:
        kwargs["bbox_extra_artists"] = list(fig.get_default_bbox_extra_artists()) + tags
    if getattr(fig, "_phd_component", False):
        # components (`layout.component`) are written canvas-exact, so all of one
        # key share their canvas and axes box and line up when placed side by side
        kwargs = {"bbox_inches": fig.bbox_inches, "pad_inches": 0.0, "dpi": dpi}

    if as_png:
        fig.savefig(figure_path / f"{name}.png", **kwargs)
    if as_pdf:
        fig.savefig(figure_path / f"{name}.pdf", **kwargs)
    if as_svg:
        fig.savefig(figure_path / f"{name}.svg", **kwargs)
