import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from typing import Any, Tuple
from phd_ui.plotting.params import BASE_PARAMS, get_params, scale_for_key
from phd_ui.plotting.figsize import get_figsizes
import numpy as np

from matplotlib.ticker import AutoMinorLocator, MultipleLocator


FIGSIZE = get_figsizes()  # inches, matching matplotlib's `figure.figsize`

# Each preset carries both its size and the point sizes that suit the medium
# it is for: `slide_*` keys come out at 2x, everything else at print scale.
# See `params.py` for why one point size cannot serve both.
PARAMS = {
    key: {**get_params(scale_for_key(key)), "figure.figsize": FIGSIZE[key]}
    for key in FIGSIZE.keys()
}

def update_params(params: dict[str, Any]) -> None:
    """
    Apply a dict of rcParams to Matplotlib.

    Parameters
    ----------
    params : dict[str, Any]
        Mapping of rcParams keys to values, as accepted by
        ``matplotlib.pyplot.rcParams.update``.

    Returns
    -------
    None
    """
    plt.rcParams.update(params)


def update_params_string(params: str, **kwargs: Any) -> None:
    """
    Apply one of the named presets in `PARAMS`, with optional overrides.

    Parameters
    ----------
    params : str
        Key into `PARAMS` (e.g. 'single', 'double', 'slide_full'). The preset
        sets both the figure size and the point sizes that suit its medium:
        `slide_*` keys are twice print scale.
    **kwargs : Any
        rcParams keys to override in the selected preset before applying it.
        The override applies to this call only; the preset is left untouched.

    Returns
    -------
    None
    """
    # Copy first: mutating `PARAMS[params]` would leak the override into every
    # later call that asks for the same preset.
    params_dict = {**PARAMS[params], **kwargs}
    update_params(params_dict)


def set_locators(ax: plt.Axes, *, minor_x: int = 2, minor_y: int = 2, major_x: int | float | None = None, major_y: int | float | None = None) -> None:
    """
    Configure major/minor tick locators on an Axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to configure.
    minor_x : int, optional
        Number of minor intervals per major interval on the x-axis,
        applied only when the x-scale is linear. Ignored if None.
    minor_y : int, optional
        Number of minor intervals per major interval on the y-axis,
        applied only when the y-scale is linear. Ignored if None.
    major_x : int or float or None, optional
        Spacing between major x-ticks. If None, the existing major
        locator is left unchanged.
    major_y : int or float or None, optional
        Spacing between major y-ticks. If None, the existing major
        locator is left unchanged.

    Returns
    -------
    None
    """
    if major_x is not None:
        ax.xaxis.set_major_locator(MultipleLocator(major_x))
    if major_y is not None:
        ax.yaxis.set_major_locator(MultipleLocator(major_y))
    if minor_x is not None and ax.get_xscale() == "linear":
        ax.xaxis.set_minor_locator(AutoMinorLocator(minor_x))
    if minor_y is not None and ax.get_yscale() == "linear":
        ax.yaxis.set_minor_locator(AutoMinorLocator(minor_y))


def fix_right_ylabels(ax: Axes) -> None:
    """
    Right-align ytick labels on the right axis.

    Keeps outward padding consistent across labels.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes whose right-side y-tick labels should be aligned.

    Returns
    -------
    None
    """

    all_dx = [label.get_window_extent().bounds[2] for label in ax.yaxis.get_ticklabels()]
    min_dx = min(all_dx)
    max_dx = max(all_dx)
    delta_dx = max_dx - min_dx

    for label, tick in zip(ax.yaxis.get_ticklabels(), ax.yaxis.get_major_ticks()):
        pad = tick.get_pad()
        xloc = label.get_position()[0]

        #width = label.get_width()  # need to draw first to get the width
        
        if label.get_position()[0] > 0:  # right-side labels
            label.set_horizontalalignment("right")
            print(delta_dx)
            label.set_x(xloc + (1.5*pad) / ax.figure.dpi)  # shift outward

def right_align_yticks(ax: Axes, pad_points: int = 6) -> None:
    """
    Right-align right-side y-tick labels with a fixed padding in points from the axis spine.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes whose right-side y-tick labels should be aligned.
    pad_points : int, optional
        Padding between the axis spine and tick labels, in points.

    Returns
    -------
    None
    """
    # Apply padding via tick_params (pad is in points)
    ax.tick_params(axis="y", which="major", pad=pad_points)
    ax.tick_params(axis="y", which="minor", pad=pad_points)
    
    # Right-align right-side labels
    for tick in ax.yaxis.get_major_ticks() + ax.yaxis.get_minor_ticks():
        right_label = tick.label2  # right-side label
        if right_label.get_text():  # if a label exists
            right_label.set_horizontalalignment("right")

def fix_right_ylabels_with_padding(ax: Axes, pad_pixels: int = 6) -> None:
    """
    Right-align y-tick labels on the right side with a fixed pixel padding from the spine.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes whose right-side y-tick labels should be aligned.
    pad_pixels : int, optional
        Padding between the axis spine and tick labels, in pixels.

    Returns
    -------
    None
    """
    fig = ax.figure
    fig.canvas.draw()  # ensure text positions are computed

    for label in ax.yaxis.get_ticklabels():
        x, y = label.get_position()
        # check if this label is on the right
        if x > 0:  
            label.set_horizontalalignment("right")
            
            # convert pixels to axis units
            bbox = label.get_window_extent(renderer=fig.canvas.get_renderer())
            trans = ax.transAxes.inverted()
            # compute padding in axis units
            shift_axes = trans.transform([(bbox.x1 + pad_pixels, 0)])[0][0] - trans.transform([(bbox.x1, 0)])[0][0]
            
            label.set_x(x + shift_axes)

def add_reciprocal_axis(
    ax: Axes,
    *,
    scale: float = 1.0,
    offset: float = 0.0,
    where: str = "top",
    axis: str = "x",
    ticks: list[float] | None = None,
    label: str | None = None,
    hide_primary: bool = True,
) -> Any:
    """
    Add a second axis showing the reciprocal of the one already plotted.

    For an axis carrying ``scale / (v + offset)``, this adds a companion
    showing `v`. The classic case is a van 't Hoff or Arrhenius plot, whose
    x-axis is ``1000 / T``: the slope is only readable against the reciprocal,
    but nobody thinks in it, so the figure wants both.
    `add_inverse_temperature_axis` is that case pre-filled.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes whose `axis` carries ``scale / (v + offset)``.
    scale : float, optional
        Numerator of the primary axis, i.e. 1000 for ``1000 / T``. Must be
        non-zero. Default is 1.0.
    offset : float, optional
        Added to the new axis' value before taking the reciprocal, i.e. 273.15
        to plot degrees Celsius against ``1000 / T`` in kelvin. Default is 0.0.
    where : {'top', 'bottom', 'left', 'right'}, optional
        Spine to put the new axis on. Default is ``'top'``.
    axis : {'x', 'y'}, optional
        Which axis of `ax` is the reciprocal one. Default is ``'x'``.
    ticks : list of float, optional
        Tick positions, in the new axis' own units. Chosen automatically if
        None, which rarely reads well on a reciprocal axis: prefer round
        values. Ticks outside the primary limits are dropped by matplotlib.
    label : str, optional
        Axis label.
    hide_primary : bool, optional
        Remove the primary axis' own ticks from `where`. Default is True, and
        it is almost always what you want: `phd_ui` sets ``xtick.top`` and
        ``ytick.right``, so without it a second, unlabelled set of reciprocal
        ticks interleaves with the new ones.

    Returns
    -------
    matplotlib.axis.SecondaryAxis
        The new axis, for further styling.

    Raises
    ------
    ValueError
        If `scale` is zero, or `axis` is not ``'x'`` or ``'y'``.

    Notes
    -----
    The two transforms are exact inverses of each other, so the ticks stay
    correct if the primary limits change afterwards. Both guard against
    division by zero, which matplotlib probes for while laying the axis out.
    """
    if scale == 0:
        raise ValueError("scale must be non-zero")
    if axis not in ("x", "y"):
        raise ValueError("axis must be 'x' or 'y'")

    def from_reciprocal(reciprocal):
        reciprocal = np.asarray(reciprocal, dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(reciprocal == 0, np.inf, scale / reciprocal) - offset

    def to_reciprocal(value):
        shifted = np.asarray(value, dtype=float) + offset
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(shifted == 0, np.inf, scale / shifted)

    if hide_primary:
        ax.tick_params(
            axis=axis, which="both",
            **({"top": False} if where == "top" else {}),
            **({"bottom": False} if where == "bottom" else {}),
            **({"left": False} if where == "left" else {}),
            **({"right": False} if where == "right" else {}),
        )

    make = ax.secondary_xaxis if axis == "x" else ax.secondary_yaxis
    secondary = make(where, functions=(from_reciprocal, to_reciprocal))

    if ticks is not None:
        (secondary.set_xticks if axis == "x" else secondary.set_yticks)(list(ticks))
    if label is not None:
        (secondary.set_xlabel if axis == "x" else secondary.set_ylabel)(label)
    return secondary


def add_inverse_temperature_axis(
    ax: Axes,
    *,
    ticks: list[float] | None = None,
    unit: str = "degC",
    scale: float = 1000.0,
    label: str | None = None,
    **kwargs: Any,
) -> Any:
    """
    Add a temperature axis on top of a plot drawn against inverse temperature.

    A van 't Hoff or Arrhenius plot puts ``scale / T`` on x, with `T` in
    kelvin: that is the axis the slope is read from, but not the one anyone
    thinks in. This is `add_reciprocal_axis` with the temperature conversion
    and the house axis label filled in.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes whose x-axis is ``scale / T``, with `T` in kelvin.
    ticks : list of float, optional
        Temperatures to tick, in `unit`. Prefer round temperatures; the
        automatic choice rarely reads well on a reciprocal axis.
    unit : {'degC', 'K'}, optional
        Unit of the new axis. Default is ``'degC'``.
    scale : float, optional
        Numerator of the primary axis, i.e. 1000 for ``1000 / T``. Must be
        positive. Default is 1000.0.
    label : str, optional
        Axis label. Defaults to the house form, ``temperature / degC`` or
        ``temperature / K``.
    **kwargs : Any
        Forwarded to `add_reciprocal_axis` (``where``, ``hide_primary``, ...).

    Returns
    -------
    matplotlib.axis.SecondaryAxis
        The new axis, for further styling.

    Raises
    ------
    ValueError
        If `unit` is not ``'degC'`` or ``'K'``, or `scale` is not positive.
    """
    if unit not in ("degC", "K"):
        raise ValueError("unit must be 'degC' or 'K'")
    if scale <= 0:
        raise ValueError("scale must be positive")

    if label is None:
        label = r"temperature /$\,^\circ$C" if unit == "degC" else r"temperature /$\,$K"

    return add_reciprocal_axis(
        ax,
        scale=scale,
        offset=273.15 if unit == "degC" else 0.0,
        ticks=ticks,
        label=label,
        **kwargs,
    )


def freeze_layout(fig) -> None:
    """
    Stop the layout engine from moving anything else on this figure.

    Constrained layout is on for every `phd_ui` figure, and it re-runs on each
    draw. Anything positioned from *measured* geometry (a label rotated onto a
    curve, a gap sized from rendered text, an artist placed against a spine) is
    measured against a layout that the next draw is still free to change, so
    the measurement and the result can disagree by the time the figure is
    saved. Draw once, freeze, then place.

    The obvious ``fig.set_layout_engine("none")`` raises `RuntimeError` as soon
    as the figure has a colorbar, because dropping the engine changes how
    colorbar space is accounted for. This installs a placeholder engine
    carrying the current engine's own flags instead, which is how
    `Figure.tight_layout` restores itself, so it works with or without one.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to freeze. Call `fig.canvas.draw()` first, or the frozen layout
        is whatever it was before the engine last ran.

    Returns
    -------
    None

    Notes
    -----
    A no-op on a figure that has no layout engine, so it is safe to call
    unconditionally.
    """
    from matplotlib.layout_engine import PlaceHolderLayoutEngine

    engine = fig.get_layout_engine()
    if engine is None:
        return
    fig.set_layout_engine(
        PlaceHolderLayoutEngine(engine.adjust_compatible, engine.colorbar_gridspec)
    )


def legend_above(
    fig,
    handles=None,
    labels=None,
    *,
    ax: Axes | None = None,
    ncol: int | None = None,
    align: str = "right",
    pad: float = 0.02,
    **kwargs,
):
    """
    Hang a legend above the figure, right-aligned with the axes by default.

    The house placement for a legend that does not fit *inside* the axes: a
    single strip over the top of the panels, ending flush with their right
    edge. It is read before the data rather than after it, it competes with
    nothing (the x label and its tick labels own the bottom), and it costs the
    panels no plot area.

    The strip is anchored *outside* the canvas, at `1 + pad` in figure
    coordinates. That is deliberate: `savefig.bbox = "tight"` grows the saved
    file to include an artist placed outside the canvas, so the axes keep the
    exact rectangle `get_figsize` asked for and only the file's height grows.
    The alternative, `loc="outside upper center"`, hands the strip to
    constrained layout, which makes room for it by shrinking the panels.

    Right-aligned because the axes' right edge is the one edge shared by every
    panel of a row and by the figure itself; a centred strip floats against
    nothing and drifts as entries are added.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to put the legend on.
    handles, labels : list, optional
        As `Figure.legend`. If omitted, they are collected from `ax`, or from
        every axes of the figure when `ax` is None, keeping the first
        occurrence of each label so shared series are not repeated.
    ax : matplotlib.axes.Axes, optional
        Take the entries from this axes alone.
    ncol : int, optional
        Columns in the strip. Defaults to one entry per column, i.e. a single
        row, which is what the placement is for.
    align : {'right', 'left', 'center'}, optional
        Which edge of the figure the strip is aligned to. `'right'` is the
        convention; the others are for a figure whose top-right corner is
        already spoken for.
    pad : float, optional
        Gap between the top of the canvas and the bottom of the strip, as a
        fraction of the figure height.
    **kwargs
        Passed to `Figure.legend`, overriding the compact defaults used here
        (`frameon=False` and tightened handle/column spacing).

    Returns
    -------
    matplotlib.legend.Legend

    Raises
    ------
    ValueError
        If `align` is not one of the three names, or if no labelled artist was
        found to build the legend from.

    Examples
    --------
    >>> fig, axes = plt.subplots(1, 3, constrained_layout=True)
    >>> legend_above(fig)
    """
    anchors = {"right": (1.0, "lower right"), "left": (0.0, "lower left"),
               "center": (0.5, "lower center")}
    if align not in anchors:
        raise ValueError(f"align must be one of {sorted(anchors)}, got {align!r}")
    x, loc = anchors[align]

    if handles is None or labels is None:
        found_handles, found_labels = [], []
        for axes in ([ax] if ax is not None else fig.axes):
            for handle, label in zip(*axes.get_legend_handles_labels()):
                if label not in found_labels:
                    found_handles.append(handle)
                    found_labels.append(label)
        handles = found_handles if handles is None else handles
        labels = found_labels if labels is None else labels
    if not labels:
        raise ValueError("no labelled artists to build a legend from")

    style = dict(frameon=False, handlelength=1.2, columnspacing=1.2,
                 handletextpad=0.4, borderpad=0.0, borderaxespad=0.0)
    return fig.legend(handles, labels, loc=loc, bbox_to_anchor=(x, 1.0 + pad),
                      ncol=ncol or len(labels), **{**style, **kwargs})
