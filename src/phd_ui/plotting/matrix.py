"""
Block diagrams of matrix equations: X = C S^T + E as labelled rectangles.

A matrix is a rectangle whose width and height are its numbers of columns
and rows in drawn units, so the shapes carry the dimensions: a data matrix
of spectra over time is wide, its concentration factor is a tall thin strip,
its spectral factor a short wide one. Blocks are placed in data coordinates
on an axes with equal aspect and no frame; `draw_matrix_equation` lays a
whole equation out left to right.

Colours follow the house rule for drawn shapes: the fill is the family's
``light`` tone, the edge its ``dark`` tone, the symbol inside its ``darkest``.
Line widths follow the active preset (print widths times the preset scale,
read off ``lines.linewidth``), font sizes come from the preset too.

The drawn sizes are the caller's choice, not the true matrix sizes: a
101 x 201 data matrix with three species would make the factors invisible,
so one passes e.g. ``rows=6, cols=10`` for X and ``rows=6, cols=1.2`` for C.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.artist import Artist
from matplotlib.patches import Rectangle
from matplotlib.text import Text

from phd_ui.colors.scheme import GREY, ColorFamily

__all__ = ["Block", "Equation", "Stripe", "Term", "draw_matrix", "draw_matrix_equation"]

_PRINT_LINEWIDTH = 1.2
_BLOCK_Z = 2.0

Align = Literal["top", "center", "bottom"]


def _scale() -> float:
    """Preset scale, read off the active line width."""
    return plt.rcParams["lines.linewidth"] / _PRINT_LINEWIDTH


@dataclass(frozen=True)
class Block:
    """
    Where a drawn matrix sits, in data coordinates.

    Attributes
    ----------
    x0, y0, x1, y1 : float
        Left, bottom, right, top edge.
    label : str
        The symbol drawn inside.
    artists : tuple of Artist
        Everything drawn for this block (rectangle, stripes, texts), so a
        caller can hide or reveal the block as one.
    """

    x0: float
    y0: float
    x1: float
    y1: float
    label: str = ""
    artists: tuple[Artist, ...] = ()

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def cx(self) -> float:
        return 0.5 * (self.x0 + self.x1)

    @property
    def cy(self) -> float:
        return 0.5 * (self.y0 + self.y1)


@dataclass(frozen=True)
class Stripe:
    """
    A highlighted band of columns or rows inside a matrix.

    Attributes
    ----------
    lo, hi : float
        Start and end of the band, in drawn units from the left edge
        (columns) or from the top edge (rows).
    label : str, optional
        Written under the block (columns) or to its right (rows).
    color : ColorFamily, optional
        Family of the band; default is the block's own.
    axis : {"col", "row"}, optional
        Whether the band spans columns (default) or rows.
    """

    lo: float
    hi: float
    label: str = ""
    color: ColorFamily | None = None
    axis: Literal["col", "row"] = "col"


@dataclass(frozen=True)
class Equation:
    """
    What `draw_matrix_equation` drew.

    Attributes
    ----------
    blocks : list of Block
        One per `Term`, in order.
    operators : list of Text
        One per operator string, in order.
    """

    blocks: list[Block]
    operators: list[Text]


@dataclass(frozen=True)
class Term:
    """
    One matrix of an equation, for `draw_matrix_equation`.

    Attributes
    ----------
    label : str
        Symbol inside the block, e.g. ``r"$\\mathbf{X}$"``.
    rows, cols : float
        Drawn height and width, in units.
    color : ColorFamily, optional
        Colour family of the block.
    dims : tuple of (str or None, str or None), optional
        Row and column dimension labels, written left of and above the block.
    stripes : sequence of Stripe, optional
        Highlighted bands.
    title : str, optional
        A short name written above the block (above the column dimension).
    """

    label: str
    rows: float
    cols: float
    color: ColorFamily = GREY
    dims: tuple[str | None, str | None] | None = None
    stripes: Sequence[Stripe] = field(default_factory=tuple)
    title: str | None = None


def draw_matrix(
    ax: plt.Axes,
    x: float,
    y: float,
    rows: float,
    cols: float,
    label: str = "",
    *,
    color: ColorFamily = GREY,
    unit: float = 1.0,
    align: Align = "top",
    dims: tuple[str | None, str | None] | None = None,
    stripes: Sequence[Stripe] = (),
    title: str | None = None,
    zorder: float = _BLOCK_Z,
) -> Block:
    """
    Draw one matrix as a labelled rectangle.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes; `draw_matrix_equation` sets equal aspect and hides the
        frame, a caller of this function does that itself.
    x : float
        Left edge, in data coordinates.
    y : float
        Top edge (``align="top"``, default), vertical centre or bottom edge.
    rows, cols : float
        Drawn height and width, in units of `unit`.
    label : str, optional
        Symbol written in the centre, e.g. ``r"$\\mathbf{X}$"``.
    color : ColorFamily, optional
        Colour family: ``light`` fill, ``dark`` edge, ``darkest`` symbol.
    unit : float, optional
        Data units per drawn unit.
    align : {"top", "center", "bottom"}, optional
        What `y` refers to.
    dims : tuple of (str or None, str or None), optional
        Row and column dimension labels, written left of and above the block.
    stripes : sequence of Stripe, optional
        Highlighted column or row bands with their labels.
    title : str, optional
        Short name written above the block, above the column label.
    zorder : float, optional
        Drawing order of the block.

    Returns
    -------
    Block
        The rectangle's edges, for placing neighbours and annotations.
    """
    width, height = cols * unit, rows * unit
    if align == "top":
        y1 = y
    elif align == "center":
        y1 = y + 0.5 * height
    elif align == "bottom":
        y1 = y + height
    else:
        raise ValueError(f"align must be 'top', 'center' or 'bottom', not {align!r}")
    x0, y0, x1 = x, y1 - height, x + width
    cx, cy = x0 + 0.5 * width, y0 + 0.5 * height
    scale = _scale()
    pad = 0.15 * unit
    small = plt.rcParams["xtick.labelsize"]
    drawn: list[Artist] = []

    drawn.append(ax.add_patch(Rectangle((x0, y0), width, height, facecolor=color.light, edgecolor=color.dark,
                                        linewidth=_PRINT_LINEWIDTH * scale, zorder=zorder)))
    for stripe in stripes:
        family = color if stripe.color is None else stripe.color
        if stripe.axis == "col":
            sx0, sx1 = x0 + stripe.lo * unit, x0 + stripe.hi * unit
            drawn.append(ax.add_patch(Rectangle((sx0, y0), sx1 - sx0, height, facecolor=family.base,
                                                edgecolor="none", alpha=0.6, zorder=zorder + 0.1)))
            if stripe.label:
                drawn.append(ax.text(0.5 * (sx0 + sx1), y0 - pad, stripe.label, ha="center", va="top",
                                     color=family.darkest, fontsize=small, zorder=zorder + 0.3))
        else:
            sy1, sy0 = y1 - stripe.lo * unit, y1 - stripe.hi * unit
            drawn.append(ax.add_patch(Rectangle((x0, sy0), width, sy1 - sy0, facecolor=family.base,
                                                edgecolor="none", alpha=0.6, zorder=zorder + 0.1)))
            if stripe.label:
                drawn.append(ax.text(x1 + pad, 0.5 * (sy0 + sy1), stripe.label, ha="left", va="center",
                                     color=family.darkest, fontsize=small, zorder=zorder + 0.3))
    if label:
        drawn.append(ax.text(cx, cy, label, ha="center", va="center", color=color.darkest,
                             fontsize=plt.rcParams["axes.labelsize"], zorder=zorder + 0.3))
    top = y1 + pad
    if dims is not None:
        row_label, col_label = dims
        if row_label:
            drawn.append(ax.text(x0 - pad, cy, row_label, ha="right", va="center", fontsize=small,
                                 zorder=zorder + 0.3))
        if col_label:
            drawn.append(ax.text(cx, top, col_label, ha="center", va="bottom", fontsize=small, zorder=zorder + 0.3))
            top += 0.9 * unit
    if title:
        drawn.append(ax.text(cx, top, title, ha="center", va="bottom", fontsize=small, zorder=zorder + 0.3))
    return Block(x0, y0, x1, y1, label, tuple(drawn))


def draw_matrix_equation(
    ax: plt.Axes,
    terms: Sequence[Term | str],
    *,
    x: float = 0.0,
    y: float = 0.0,
    unit: float = 1.0,
    gap: float = 0.6,
    align: Align = "top",
    pad: float = 1.2,
    autoscale: bool = True,
) -> Equation:
    """
    Lay a matrix equation out left to right, matrices as blocks, operators as text.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes. Its aspect is set equal and its frame hidden.
    terms : sequence of Term, str or (str, float)
        Matrices (`Term`) and operators (``"="``, ``"+"``, ``r"$\\times$"``,
        ``r"$\\approx$"``, ``r"$\\rightarrow$"``) in reading order. Two
        adjacent matrices with nothing between them are a product. An
        operator is one unit wide; a longer one is given as ``(text, width)``
        with its width in units, e.g. ``(r"$+ \\lambda \\log\\det($", 5)``.
    x, y : float, optional
        Left edge of the first block and the alignment line (top edge,
        centre or bottom edge of every block, see `align`).
    unit : float, optional
        Data units per drawn unit.
    gap : float, optional
        Horizontal space between items, in units.
    align : {"top", "center", "bottom"}, optional
        How the blocks line up vertically. Operators sit at the vertical
        centre of the tallest block.
    pad : float, optional
        Margin around the drawing when the axis limits are set, in units;
        make it larger when dimension labels or titles need the room.
    autoscale : bool, optional
        Set the axis limits to the drawing plus `pad` (default). Pass False
        when several equations share one axes and the caller sets the limits.

    Returns
    -------
    Equation
        The blocks, one per `Term`, and the operator texts, both in order,
        so a reveal can show a term or an operator at a time.
    """
    height_max = max((t.rows for t in terms if isinstance(t, Term)), default=0.0) * unit
    if align == "top":
        y_mid = y - 0.5 * height_max
    elif align == "center":
        y_mid = y
    elif align == "bottom":
        y_mid = y + 0.5 * height_max
    else:
        raise ValueError(f"align must be 'top', 'center' or 'bottom', not {align!r}")

    blocks: list[Block] = []
    operators: list[Text] = []
    cursor = x
    op_width = 1.0 * unit
    for term in terms:
        if isinstance(term, (str, tuple)):
            text, w = (term, 1.0) if isinstance(term, str) else term
            w = w * unit
            operators.append(ax.text(cursor + 0.5 * w, y_mid, text, ha="center", va="center",
                                     fontsize=plt.rcParams["axes.labelsize"], zorder=_BLOCK_Z + 0.3))
            cursor += w + gap * unit
        else:
            block = draw_matrix(ax, cursor, y, term.rows, term.cols, term.label, color=term.color, unit=unit,
                                align=align, dims=term.dims, stripes=term.stripes, title=term.title)
            blocks.append(block)
            cursor = block.x1 + gap * unit
    cursor -= gap * unit

    ax.set_aspect("equal")
    ax.set_axis_off()
    if autoscale:
        y_lo = min((b.y0 for b in blocks), default=y_mid) - pad * unit
        y_hi = max((b.y1 for b in blocks), default=y_mid) + pad * unit
        ax.set_xlim(x - pad * unit, cursor + pad * unit)
        ax.set_ylim(y_lo, y_hi)
    return Equation(blocks, operators)
