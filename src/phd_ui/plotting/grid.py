"""Grids of fixed-size panels: the figure grows with the grid, the panels never shrink."""

from typing import Hashable, Literal, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from phd_ui.plotting.conversion import cm_to_inches

Share = bool | Literal["all", "row", "col"]
Span = tuple[int | slice, int | slice]


class _Geometry:
    """Cell positions of a fixed-size grid, in cm from the top-left corner."""

    def __init__(self, nrows, ncols, panel_cm, gap_cm, margin_cm):
        self.w, self.h = (panel_cm, panel_cm) if np.isscalar(panel_cm) else panel_cm
        gx, gy = (gap_cm, gap_cm) if np.isscalar(gap_cm) else gap_cm
        self.gx = self._gaps(gx, ncols, "columns")    # gap after column j, j = 0 .. ncols - 2
        self.gy = self._gaps(gy, nrows, "rows")
        self.left, self.right, self.bottom, self.top = margin_cm
        self.x = self.left + np.arange(ncols) * self.w + np.concatenate([[0.0], np.cumsum(self.gx)])
        self.y = self.top + np.arange(nrows) * self.h + np.concatenate([[0.0], np.cumsum(self.gy)])
        self.width = self.x[-1] + self.w + self.right
        self.height = self.y[-1] + self.h + self.bottom

    @staticmethod
    def _gaps(gap, n: int, what: str) -> np.ndarray:
        """One gap per space between n cells: a scalar for all of them, or a sequence of n - 1."""
        if np.isscalar(gap):
            return np.full(max(n - 1, 0), float(gap))
        gaps = np.asarray(gap, dtype=float)
        if gaps.shape != (max(n - 1, 0),):
            raise ValueError(f"{len(gaps)} gaps given for {n} {what}: need {n - 1}")
        return gaps

    def rect(self, r0: int, r1: int, c0: int, c1: int) -> tuple[float, float, float, float]:
        """Figure-fraction rectangle of the block from cell (r0, c0) to cell (r1, c1), inclusive.

        The block's edges are the outer edges of its corner cells, so the gaps between
        the cells it covers become part of it and it lines up with the cells around it.
        Positions are measured from the top-left corner: rows added below and columns
        added to the right move nothing.
        """
        x0, x1 = self.x[c0], self.x[c1] + self.w
        y_top, y_bot = self.y[r0], self.y[r1] + self.h
        return (x0 / self.width, 1 - y_bot / self.height, (x1 - x0) / self.width, (y_bot - y_top) / self.height)


def _figure(geo: _Geometry) -> Figure:
    return plt.figure(figsize=(cm_to_inches(geo.width), cm_to_inches(geo.height)), layout="none")


def _indices(span: int | slice, n: int) -> tuple[int, int]:
    """First and last index (inclusive) of an int or slice into range(n)."""
    idx = range(n)[span]
    if isinstance(idx, int):
        return idx, idx
    if len(idx) == 0 or idx.step != 1:
        raise ValueError(f"a merged block must be a contiguous, non-empty range, got {span!r}")
    return idx[0], idx[-1]


def panel_grid(
    nrows: int,
    ncols: int,
    panel_cm: float | tuple[float, float] = 3.5,
    gap_cm: float | tuple[float, float] = 0.4,
    margin_cm: Sequence[float] = (1.4, 0.4, 1.1, 0.7),
    sharex: Share = False,
    sharey: Share = False,
    merge: Sequence[Span] = (),
) -> tuple[Figure, np.ndarray]:
    """
    Figure with an ``nrows`` x ``ncols`` grid of panels of one fixed physical size.

    Every panel has the same size and sits at a fixed distance from the top-left
    corner of the canvas. Adding columns makes the figure wider to the right,
    adding rows makes it taller downwards, and the panels already there keep
    their size and position. Use it for small-multiple figures that grow with
    their content (an evidence grid, a parity grid per model), where the usual
    rule of taking the width from `get_figsize` does not apply.

    Parameters
    ----------
    nrows, ncols : int
        Grid shape.
    panel_cm : float or (float, float), optional
        Panel width and height in cm; a single number gives square panels.
        Default is 3.5.
    gap_cm : float or (x, y), optional
        Gap between panels in cm, room for tick labels when axes are not
        shared. ``x`` and ``y`` are each a number (every gap) or a sequence with
        one gap per space, ``ncols - 1`` and ``nrows - 1`` long, e.g. to leave
        room for titles below a first row. Default is 0.4.
    margin_cm : sequence of 4 float, optional
        Left, right, bottom and top margin in cm, room for outer axis labels,
        row labels and column titles. Default is (1.4, 0.4, 1.1, 0.7).
    sharex, sharey : bool or {'all', 'row', 'col'}, optional
        Share axes as in `matplotlib.pyplot.subplots`; inner tick labels of a
        shared axis are hidden. Default is False.
    merge : sequence of (rows, cols), optional
        Blocks of cells drawn as one panel, each given as a pair of ints or
        slices, e.g. ``(0, slice(1, 3))`` merges columns 1 and 2 of row 0. The
        merged panel's outline is the outer boundary of its cells (the gaps
        between them included), so it lines up with the grid. Blocks must not
        overlap. Default is none.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure, with no layout engine: positions are fixed by design.
    axes : ndarray of matplotlib.axes.Axes
        Shape ``(nrows, ncols)``. Every cell of a merged block holds the same
        Axes. Hide an unused slot with ``axes[i, j].set_visible(False)``.

    Notes
    -----
    Constrained layout is deliberately off, since it would shrink the panels to
    fit the canvas. `save_figure` still trims the outer margin to the drawn
    content (``bbox_inches="tight"``), which changes the file size but not the
    panel size, so panels of two figures made with the same `panel_cm` print
    at the same size.

    See Also
    --------
    panel_mosaic : the same grid described by a layout of labels.
    """
    layout = np.arange(nrows * ncols, dtype=object).reshape(nrows, ncols)
    for k, (rows, cols) in enumerate(merge):
        r0, r1 = _indices(rows, nrows)
        c0, c1 = _indices(cols, ncols)
        block = layout[r0:r1 + 1, c0:c1 + 1]
        if any(isinstance(v, tuple) for v in block.ravel()):
            raise ValueError(f"merged block {k} overlaps an earlier one")
        for i in range(r0, r1 + 1):
            for j in range(c0, c1 + 1):
                layout[i, j] = ("merged", k)
    fig, by_label, cells = _build(layout.tolist(), panel_cm, gap_cm, margin_cm)
    axes = np.empty((nrows, ncols), dtype=object)
    for i in range(nrows):
        for j in range(ncols):
            axes[i, j] = by_label[layout[i, j]]
    _share(axes, cells, sharex, "x")
    _share(axes, cells, sharey, "y")
    return fig, axes


def panel_mosaic(
    layout: Sequence[Sequence[Hashable]],
    panel_cm: float | tuple[float, float] = 3.5,
    gap_cm: float | tuple[float, float] = 0.4,
    margin_cm: Sequence[float] = (1.4, 0.4, 1.1, 0.7),
    empty: Hashable = ".",
) -> tuple[Figure, dict[Hashable, Axes]]:
    """
    Fixed-size panel grid described by a layout of labels, as `subplot_mosaic`.

    Cells with the same label form one panel whose outline is the outer
    boundary of those cells; each label must cover a rectangle. Sizes and
    positions follow `panel_grid`: one cell is ``panel_cm``, and the figure
    grows with the layout.

    Parameters
    ----------
    layout : sequence of sequences of hashable
        One row per inner sequence, all the same length, e.g.
        ``[["a", "b", "b"], ["c", "b", "b"]]``.
    panel_cm, gap_cm, margin_cm
        As in `panel_grid`.
    empty : hashable, optional
        Label of a cell left blank. Default is ``"."``.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure, with no layout engine.
    axes : dict
        Label to Axes.
    """
    fig, by_label, _ = _build([list(r) for r in layout], panel_cm, gap_cm, margin_cm, empty=empty)
    return fig, by_label


def _build(layout, panel_cm, gap_cm, margin_cm, empty=object()):
    """Place one Axes per label over its block of cells; return the figure, label -> Axes, Axes -> block."""
    nrows, ncols = len(layout), len(layout[0])
    if any(len(r) != ncols for r in layout):
        raise ValueError("every row of the layout must have the same length")
    geo = _Geometry(nrows, ncols, panel_cm, gap_cm, margin_cm)
    fig = _figure(geo)
    blocks: dict = {}
    for i, row in enumerate(layout):
        for j, label in enumerate(row):
            if label == empty:
                continue
            r0, r1, c0, c1 = blocks.get(label, (i, i, j, j))
            blocks[label] = (min(r0, i), max(r1, i), min(c0, j), max(c1, j))
    by_label, cells = {}, {}
    for label, (r0, r1, c0, c1) in blocks.items():
        if any(layout[i][j] != label for i in range(r0, r1 + 1) for j in range(c0, c1 + 1)):
            raise ValueError(f"label {label!r} does not cover a rectangle")
        ax = fig.add_axes(geo.rect(r0, r1, c0, c1))
        by_label[label], cells[ax] = ax, (r0, r1, c0, c1)
    return fig, by_label, cells


def _share(axes: np.ndarray, cells: dict, share: Share, which: str) -> None:
    """Link axes along rows, columns or the whole grid, and hide inner tick labels."""
    if not share:
        return
    mode = "all" if share is True else share
    nrows, ncols = axes.shape
    for i in range(nrows):
        for j in range(ncols):
            ref = {"all": axes[0, 0], "row": axes[i, 0], "col": axes[0, j]}[mode]
            ax = axes[i, j]
            if ax is ref or getattr(ax, f"get_shared_{which}_axes")().joined(ax, ref):
                continue
            try:
                getattr(ax, f"share{which}")(ref)
            except ValueError:   # a merged panel spanning two columns (rows) keeps its first share
                pass
    for ax, (r0, r1, c0, c1) in cells.items():
        if which == "x" and mode in ("all", "col") and r1 < nrows - 1:
            ax.tick_params(axis="x", labelbottom=False)   # not on the bottom row
        if which == "y" and mode in ("all", "row") and c0 > 0:
            ax.tick_params(axis="y", labelleft=False)     # not in the first column
