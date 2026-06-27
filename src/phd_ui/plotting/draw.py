import matplotlib.pyplot as plt
from typing import Literal

def draw_peak(
    ax: plt.Axes,
    wavenumber_cm: float,
    height: float,
    fontsize: float = 6,
    distance: float = 0,
    distance_unit: Literal["points", "pixels", "data"] = "points",
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
    if distance_unit == "points":
        distance_px = distance * dpi / 72
    elif distance_unit == "pixels":
        distance_px = distance
    else:  # data units
        x0_px = ax.transData.transform((wavenumber_cm, height))[0]
        x1_px = ax.transData.transform((wavenumber_cm + distance, height))[0]
        distance_px = abs(x1_px - x0_px)

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