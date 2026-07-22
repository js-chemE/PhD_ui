import matplotlib.pyplot as plt
from typing import Literal, Union
import numpy as np
import matplotlib as mpl
from matplotlib.colors import Colormap, Normalize
from matplotlib.transforms import Transform

from phd_ui.colors.cmaps import create_colormap_from_cmap

OffsetUnit = Literal["points", "pixels", "data"]


def _offset_to_pixels(
    value: float,
    unit: OffsetUnit,
    ax: plt.Axes,
    axis: Literal["x", "y"] = "x",
    origin: tuple[float, float] = (0.0, 0.0),
) -> float:
    """
    Convert a length given in points, pixels, or data units to pixels.

    Parameters
    ----------
    value : float
        Length to convert.
    unit : {'points', 'pixels', 'data'}
        Unit `value` is given in.
    ax : matplotlib.axes.Axes
        Axes providing the figure DPI and data transform.
    axis : {'x', 'y'}, optional
        Axis along which a 'data' unit length is measured.
    origin : tuple[float, float], optional
        Data-coordinate point the 'data' unit length is measured from.
        Only matters for nonlinear scales (e.g. log), where pixels per
        data unit vary with position.

    Returns
    -------
    float
        `value` converted to pixels.

    Raises
    ------
    ValueError
        If `unit` is not 'points', 'pixels', or 'data'.
    """
    dpi = ax.figure.dpi

    if unit == "points":
        return value * dpi / 72
    if unit == "pixels":
        return value
    if unit == "data":
        x0, y0 = origin
        p0 = ax.transData.transform((x0, y0))
        p1 = ax.transData.transform((x0 + value, y0) if axis == "x" else (x0, y0 + value))
        return (p1[0] - p0[0]) if axis == "x" else (p1[1] - p0[1])

    raise ValueError("unit must be 'points', 'pixels' or 'data'")


def draw_peak(
    ax: plt.Axes,
    wavenumber_cm: float,
    height: float,
    fontsize: float = 6,
    distance: float = 0,
    distance_unit: OffsetUnit = "points",
    linecolor: str = "black",
    ls: str = "--",
    lw: float = 0.5,
    fontcolor: str = "black",
    fontstyle: str = "normal",
    fontweight: str | int = "normal",
    side: Literal["left", "right"] = "left",
    rotation: float = 90,
) -> None:
    """
    Draw a peak marker with aligned label.

    The label is rendered once to measure its actual pixel bounding box,
    then repositioned so its near edge sits exactly `distance` from the
    line on both sides. Relying on ha/va alignment under rotation isn't
    reliably symmetric - it depends on matplotlib's internal font-metric
    padding rather than the literal rendered text box - so this measures
    the real geometry instead of assuming it.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to draw on.
    wavenumber_cm : float
        Data x-position of the peak (and the value shown in its label).
    height : float
        Data y-position of the peak label and vertical line target.
    fontsize : float, optional
        Font size of the label.
    distance : float, optional
        Gap between the vertical line and the label's near edge.
    distance_unit : {'points', 'pixels', 'data'}, optional
        Unit in which `distance` is given.
    linecolor : str, optional
        Color of the vertical marker line.
    ls : str, optional
        Line style of the vertical marker line.
    lw : float, optional
        Line width of the vertical marker line.
    fontcolor : str, optional
        Color of the label text.
    fontstyle : str, optional
        Style of the label text (e.g. 'normal', 'italic').
    fontweight : str or int, optional
        Weight of the label text (e.g. 'normal', 'bold').
    side : {'left', 'right'}, optional
        Side of the line on which the label is placed.
    rotation : float, optional
        Rotation angle of the label, in degrees.

    Returns
    -------
    None
    """
    ax.axvline(wavenumber_cm, color=linecolor, ls=ls, lw=lw)

    label = f"{wavenumber_cm}"
    fig = ax.figure

    txt = ax.text(
        wavenumber_cm, height, label,
        ha="center", va="center",
        rotation=rotation, rotation_mode="anchor",
        color=fontcolor, fontsize=fontsize, fontstyle=fontstyle, fontweight=fontweight,
    )

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox = txt.get_window_extent(renderer=renderer)

    dpi = fig.dpi
    distance_px = _offset_to_pixels(distance, distance_unit, ax, axis="x", origin=(wavenumber_cm, height))
    if distance_unit == "data":
        distance_px = abs(distance_px)

    line_px = ax.transData.transform((wavenumber_cm, height))[0]
    if side == "right":
        shift_px = (line_px + distance_px) - bbox.x0  # align label's left (near) edge
    else:
        shift_px = (line_px - distance_px) - bbox.x1  # align label's right (near) edge

    txt.remove()

    ax.annotate(
        label,
        xy=(wavenumber_cm, height),
        xycoords="data",
        xytext=(shift_px * 72 / dpi, 0),
        textcoords="offset points",
        ha="center",
        va="center",
        rotation=rotation,
        rotation_mode="anchor",
        color=fontcolor,
        fontsize=fontsize,
        fontstyle=fontstyle,
        fontweight=fontweight,
    )

def draw_vscale(
    ax: plt.Axes,
    x: float,
    y: float,
    value: float | None = None,
    scale: float = 1.0,
    transform: Transform | None = None,
    autosize: float = 0.12,
    fontsize: float = 7,
    offset_x: float = 2,
    offset_y: float = 0,
    offset_unit: OffsetUnit = "points",
    linecolor: str = "black",
    ls: str = "-",
    lw: float = 1.2,
    fontcolor: str = "black",
    fontstyle: str = "normal",
    fontweight: str | int = "normal",
    ha: Literal["left", "center", "right"] = "left",
    va: Literal["bottom", "center", "top"] = "center",
) -> None:
    """
    Draw a vertical intensity scale bar.

    Parameters
    ----------
    x, y
        Bottom position of the scale bar.

        If transform=ax.transData:
            x and y are data coordinates.

        If transform=ax.transAxes:
            x and y are axes coordinates.

    value
        Value represented by the scale bar.

        If None:
            A suitable value is chosen automatically.

        If given:
            The bar is labelled with this value.

    scale
        Displayed height of the scale bar **in y-data units**.

        Only used when value is given.

    transform
        Coordinate system for x and y.
    """

    if transform is None:
        transform = ax.transData

    ymin, ymax = ax.get_ylim()
    yrange = ymax - ymin

    # ------------------------------------------------------------
    # Automatic mode
    # ------------------------------------------------------------

    if value is None:

        target = autosize * yrange

        exponent = np.floor(np.log10(target))
        base = target / 10**exponent

        if base < 1.5:
            value = 1 * 10**exponent
        elif base < 3.5:
            value = 2 * 10**exponent
        elif base < 7.5:
            value = 5 * 10**exponent
        else:
            value = 10 * 10**exponent

        scale = value

    # ------------------------------------------------------------
    # Convert displayed height if anchored in axes coordinates
    # ------------------------------------------------------------

    if transform == ax.transAxes:
        scale_plot = scale / yrange
    else:
        scale_plot = scale

    # ------------------------------------------------------------
    # Draw scale bar
    # ------------------------------------------------------------

    ax.plot(
        [x, x],
        [y, y + scale_plot],
        transform=transform,
        color=linecolor,
        lw=lw,
        ls=ls,
        solid_capstyle="butt",
        clip_on=False,
    )

    # ------------------------------------------------------------
    # Convert text offsets
    # ------------------------------------------------------------

    dpi = ax.figure.dpi

    offset_x_pts = _offset_to_pixels(offset_x, offset_unit, ax, axis="x") * 72 / dpi
    offset_y_pts = _offset_to_pixels(offset_y, offset_unit, ax, axis="y") * 72 / dpi

    # ------------------------------------------------------------
    # Draw label
    # ------------------------------------------------------------

    ax.annotate(
        f"{value:g}",
        xy=(x, y + scale_plot / 2),
        xycoords=transform,
        xytext=(offset_x_pts, offset_y_pts),
        textcoords="offset points",
        ha=ha,
        va=va,
        fontsize=fontsize,
        color=fontcolor,
        fontstyle=fontstyle,
        fontweight=fontweight,
        clip_on=False,
    )


def draw_colorbar(
    ax: plt.Axes,
    cmap: Union[str, Colormap],
    vmin: float,
    vmax: float,
    cmap_vmin: float = 0.0,
    cmap_vmax: float = 1.0,
    label: str | None = None,
    orientation: Literal["vertical", "horizontal"] = "vertical",
    cax: plt.Axes | None = None,
    **colorbar_kwargs,
) -> mpl.colorbar.Colorbar:
    """
    Draw a colorbar matching the color mapping used by `value_to_color`.

    Matplotlib's built-in colorbar has no notion of sampling only a
    sub-range of a colormap's domain, so this builds a colormap
    truncated to [cmap_vmin, cmap_vmax] (via `create_colormap_from_cmap`)
    and pairs it with a Normalize over [vmin, vmax] -- reproducing
    exactly the colors `value_to_color` would return for the same
    `vmin`/`vmax`/`cmap_vmin`/`cmap_vmax`.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to attach the colorbar to (used as the parent when `cax`
        is not given).
    cmap : str or Colormap
        Name of a matplotlib colormap, or a colormap instance.
    vmin, vmax : float
        Data range shown on the colorbar.
    cmap_vmin, cmap_vmax : float, optional
        Sub-range of the colormap's [0, 1] domain to sample from, as in
        `value_to_color`.
    label : str, optional
        Colorbar label.
    orientation : {'vertical', 'horizontal'}, optional
        Colorbar orientation.
    cax : matplotlib.axes.Axes, optional
        Axes into which the colorbar is drawn. If None, space is stolen
        from `ax`.
    **colorbar_kwargs
        Additional keyword arguments forwarded to `Figure.colorbar`.

    Returns
    -------
    matplotlib.colorbar.Colorbar
        The created colorbar, for further customization (e.g. `set_ticks`).

    Raises
    ------
    ValueError
        If `vmin >= vmax`, or if `cmap_vmin`/`cmap_vmax` do not satisfy
        ``0 <= cmap_vmin < cmap_vmax <= 1`` (raised by
        `create_colormap_from_cmap`).
    """
    if vmin >= vmax:
        raise ValueError("vmin must be < vmax")

    truncated_cmap = create_colormap_from_cmap(cmap, vmin=cmap_vmin, vmax=cmap_vmax, number=256)

    sm = mpl.cm.ScalarMappable(norm=Normalize(vmin=vmin, vmax=vmax), cmap=truncated_cmap)
    sm.set_array([])

    cbar = ax.figure.colorbar(sm, ax=ax, cax=cax, orientation=orientation, **colorbar_kwargs)
    if label is not None:
        cbar.set_label(label)
    return cbar