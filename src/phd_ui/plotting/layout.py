"""
Slide adaptation, panel labels and the layout check (added 2026-10-26).

`slide_ticks(fig)`
    Fewer, rounder major ticks on every linear axis of a slide figure: about
    three per axis (0, 4, 8 instead of 0, 2, 4, 6, 8; 0, 0.5, 1 instead of five
    quarter steps; 0, 300, 600). Axes with fixed (symbolic) ticks, log axes and
    axes without ticks are left alone. `save_figure` calls it on its own when
    the active preset is a `slide_*` key.

`panel_label(ax, "(a)")`
    A panel identifier above the top-left corner of the axes that is kept out
    of the layout, so it does not shrink the panel; the tight bounding box on
    save grows the file to include it, the same mechanism as `legend_above`.

`check_layout(fig)`
    Lists what a reader would see as broken: a text, annotation or legend that
    crosses its axes frame, an axis label longer than its own axis, labels or
    tick labels of one panel running into another panel, and a text or legend
    lying on top of plotted data. `save_figure` warns with it on every save.
"""

from __future__ import annotations

import math

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoLocator, AutoMinorLocator, MaxNLocator, MultipleLocator, ScalarFormatter
from matplotlib.transforms import Bbox

PANEL_LABEL_GID = "panel-label"
SLIDE_TICK_TARGET = 3
_STEPS = (1.0, 2.0, 5.0, 2.5, 4.0, 3.0)        # mantissas, in order of preference


def nice_ticks(lo: float, hi: float, target: int = SLIDE_TICK_TARGET) -> float | None:
    """
    Step of a round tick set with about `target` ticks inside [lo, hi].

    Parameters
    ----------
    lo, hi : float
        View limits.
    target : int, optional
        Wanted number of major ticks (default 3).

    Returns
    -------
    float or None
        The step, or None if the limits are degenerate. Ticks are the multiples
        of the step inside the view. Among candidates, the one closest to
        `target` ticks wins, then the one spanning more of the axis, then the
        simpler mantissa (1, 2, 5, 2.5, 4, 3).
    """
    lo, hi = min(lo, hi), max(lo, hi)
    span = hi - lo
    if not np.isfinite(span) or span <= 0:
        return None
    best, best_key = None, None
    base = 10.0 ** math.floor(math.log10(span))
    for exp in (base / 10, base, base * 10):
        for rank, m in enumerate(_STEPS):
            step = m * exp
            first = math.ceil(lo / step - 1e-9) * step
            ticks = np.arange(first, hi + step * 1e-9, step)
            n = len(ticks)
            if n < 2:
                continue
            cover = (ticks[-1] - ticks[0]) / span
            ends = int(abs(ticks[0] - lo) > 1e-9 * span) + int(abs(ticks[-1] - hi) > 1e-9 * span)
            # an axis starts and ends on a major tick where it can: that first
            # (2 to 4 ticks), then the tick count closest to `target`
            key = (ends if 2 <= n <= target + 1 else 3, abs(n - target), -round(cover, 3), rank)
            if best_key is None or key < best_key:
                best, best_key = step, key
    return best


def slide_ticks(fig: Figure, target: int = SLIDE_TICK_TARGET) -> None:
    """
    Thin the major ticks of every linear, automatically ticked axis to about `target`.

    Parameters
    ----------
    fig : Figure
        Figure to adapt in place.
    target : int, optional
        Major ticks per axis (default 3).

    Returns
    -------
    None
    """
    for ax in fig.axes:
        for axis, lim in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
            if axis.get_scale() != "linear" or not axis.get_visible():
                continue
            loc = axis.get_major_locator()
            if not isinstance(loc, (AutoLocator, MaxNLocator, MultipleLocator)):
                continue                                    # fixed, symbolic or null ticks stay as they are
            if not isinstance(axis.get_major_formatter(), ScalarFormatter):
                continue
            step = nice_ticks(*lim, target=target)
            if step is None:
                continue
            axis.set_major_locator(MultipleLocator(step))
            minor = axis.get_minor_locator()
            if isinstance(minor, AutoMinorLocator):
                axis.set_minor_locator(AutoMinorLocator(minor.ndivs if isinstance(minor.ndivs, int) else 2))


def panel_label(ax: Axes, text: str, *, inside: bool = True, pad_pt: float = 4.0, **kwargs) -> object:
    """
    A panel identifier, ``(a)``, ``(b)``, ... in the top-left corner of `ax`.

    Parameters
    ----------
    ax : Axes
        Panel to label.
    text : str
        The identifier, e.g. ``"(a)"``.
    inside : bool, optional
        True (default, set 2026-10-26): inside the frame, `pad_pt` in from the
        top-left corner. It is then an ordinary annotation, so `check_layout`
        warns if it lies on data; keep that corner free. False: above the
        top-left corner, kept out of the layout so the panel does not shrink,
        and added to the tight bounding box on save.
    pad_pt : float, optional
        Distance from the corner (inside) or the top spine (outside), in pt at
        print scale, scaled with the preset.
    **kwargs
        Passed to `Axes.annotate` (e.g. ``fontweight``).

    Returns
    -------
    matplotlib.text.Annotation
        The label.
    """
    from phd_ui.plotting.params import scale_for_key
    from phd_ui.plotting import core

    scale = scale_for_key(core.ACTIVE_KEY) if core.ACTIVE_KEY else 1.0
    kwargs.setdefault("fontweight", "semibold")
    if inside:
        label = ax.annotate(text, xy=(0, 1), xycoords="axes fraction", xytext=(pad_pt * scale, -pad_pt * scale),
                            textcoords="offset points", ha="left", va="top", **kwargs)
        label.set_gid("panel-label-inside")
        return label
    kwargs.setdefault("fontsize", "large")
    label = ax.annotate(text, xy=(0, 1), xycoords="axes fraction", xytext=(0, pad_pt * scale),
                        textcoords="offset points", ha="left", va="bottom", annotation_clip=False, **kwargs)
    label.set_in_layout(False)
    label.set_gid(PANEL_LABEL_GID)
    return label


# ---------------------------------------------------------------- check

def _visible_texts(ax: Axes) -> list:
    return [t for t in ax.texts if t.get_visible() and t.get_text() and t.get_gid() != PANEL_LABEL_GID]


def _label_boxes(ax: Axes, renderer) -> list[tuple[str, Bbox]]:
    boxes = []
    for name, axis in (("x", ax.xaxis), ("y", ax.yaxis)):
        if not axis.get_visible():
            continue
        lab = axis.label
        if lab.get_visible() and lab.get_text():
            boxes.append((f"{name} label {lab.get_text()!r}", lab.get_window_extent(renderer)))
        lo, hi = sorted(axis.get_view_interval())
        for tick in axis.get_major_ticks() + axis.get_minor_ticks():
            loc = tick.get_loc()
            if loc is None or not (lo - 1e-9 * abs(hi - lo) <= loc <= hi + 1e-9 * abs(hi - lo)):
                continue                                   # outside the view: not drawn
            for t in (tick.label1, tick.label2):
                if t.get_visible() and t.get_text():
                    boxes.append((f"{name} tick label {t.get_text()!r}", t.get_window_extent(renderer)))
    return boxes


def _line_points(line: Line2D, step_px: float = 2.0) -> np.ndarray:
    """Display-space points along a line, densified to about `step_px`."""
    xy = line.get_transform().transform(np.column_stack(line.get_data()).astype(float))
    xy = xy[np.all(np.isfinite(xy), axis=1)]
    if len(xy) < 2:
        return xy
    # every segment a -> b gets n = clip(|b - a| / step_px, 1, 200) points a + (k / n)(b - a), k = 1..n;
    # vectorised (2026-11-04): the per-segment loop took about a minute on a figure with 40 dense spectra per panel
    seg = xy[1:] - xy[:-1]
    n = np.minimum(200, np.maximum(1, np.hypot(seg[:, 0], seg[:, 1]) / step_px)).astype(int)
    which = np.repeat(np.arange(len(seg)), n)
    k = np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n) + 1
    t = (k / np.repeat(n, n))[:, None]
    return np.vstack([xy[:1], xy[:-1][which] + t * seg[which]])


def check_layout(fig: Figure, tol_px: float = 0.5) -> list[str]:
    """
    List the layout problems of a figure.

    Parameters
    ----------
    fig : Figure
        Figure to check; it is drawn first.
    tol_px : float, optional
        Tolerance in display pixels.

    Returns
    -------
    list of str
        One entry per problem, empty when the figure is clean:

        - a text, annotation arrow or legend crossing its axes frame
          (panel labels from `panel_label` excepted);
        - an axis label longer than its own axis (it would reach past the
          panel it belongs to);
        - an axis label or tick label of one panel overlapping another
          panel's frame or labels;
        - a text or legend lying on a plotted line (texts placed by
          `draw_curve_label` excepted).
    """
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    problems: list[str] = []
    axes = [ax for ax in fig.axes if ax.get_visible() and ax.axison]
    frames = {ax: ax.get_window_extent(r) for ax in axes}

    for i, ax in enumerate(axes):
        frame = frames[ax]
        items = [(f"text {t.get_text()!r}", t) for t in _visible_texts(ax)]
        items += [(f"arrow of {t.get_text()!r}", t.arrow_patch) for t in _visible_texts(ax)
                  if getattr(t, "arrow_patch", None) is not None and t.arrow_patch.get_visible()]
        if ax.get_legend() is not None and ax.get_legend().get_visible():
            items.append(("legend", ax.get_legend()))
        for label, artist in items:
            b = artist.get_window_extent(r)
            if b.x0 < frame.x0 - tol_px or b.x1 > frame.x1 + tol_px or b.y0 < frame.y0 - tol_px or b.y1 > frame.y1 + tol_px:
                problems.append(f"axes {i}: {label} crosses the axes frame")

        # axis labels must not be longer than their axis
        if ax.yaxis.get_visible() and ax.yaxis.label.get_text():
            b = ax.yaxis.label.get_window_extent(r)
            if b.y0 < frame.y0 - tol_px or b.y1 > frame.y1 + tol_px:
                problems.append(f"axes {i}: y label {ax.yaxis.label.get_text()!r} is longer than its axis "
                                f"({b.height:.0f} px against {frame.height:.0f} px)")
        if ax.xaxis.get_visible() and ax.xaxis.label.get_text():
            b = ax.xaxis.label.get_window_extent(r)
            if b.x0 < frame.x0 - tol_px or b.x1 > frame.x1 + tol_px:
                problems.append(f"axes {i}: x label {ax.xaxis.label.get_text()!r} is longer than its axis")

        # text or legend on top of data
        lines = [ln for ln in ax.get_lines() if ln.get_visible() and len(ln.get_xdata()) > 0]
        # texts placed on a curve on purpose are exempt: `draw_curve_label`, or any
        # text given `set_gid("on-data")` (a vector name at its arrow tip, say)
        covers = [(f"text {t.get_text()!r}", t.get_window_extent(r)) for t in _visible_texts(ax)
                  if t.get_gid() not in ("curve-label", "on-data")]
        if ax.get_legend() is not None and ax.get_legend().get_visible():
            covers.append(("legend", ax.get_legend().get_window_extent(r)))
        for label, box in covers:
            inner = box.expanded(1.0, 1.0)
            x0, y0, x1, y1 = inner.x0 + 1, inner.y0 + 1, inner.x1 - 1, inner.y1 - 1
            for ln in lines:
                pts = _line_points(ln)
                if pts.size and np.any((pts[:, 0] > x0) & (pts[:, 0] < x1) & (pts[:, 1] > y0) & (pts[:, 1] < y1)):
                    name = ln.get_label()
                    problems.append(f"axes {i}: {label} lies on data" + (f" ({name})" if not name.startswith("_") else ""))
                    break

    # a linear, automatically ticked axis should start and end on a major tick
    for k, ax in enumerate(axes):
        for name, axis, lim in (("x", ax.xaxis, ax.get_xlim()), ("y", ax.yaxis, ax.get_ylim())):
            if axis.get_scale() != "linear" or not axis.get_visible():
                continue
            if not isinstance(axis.get_major_locator(), (AutoLocator, MaxNLocator, MultipleLocator)):
                continue
            lo, hi = sorted(lim)
            locs = [v for v in axis.get_majorticklocs() if lo - 1e-9 * (hi - lo) <= v <= hi + 1e-9 * (hi - lo)]
            if locs and (abs(locs[0] - lo) > 1e-6 * (hi - lo) or abs(locs[-1] - hi) > 1e-6 * (hi - lo)):
                problems.append(f"axes {k}: {name} axis {lo:g}-{hi:g} does not start and end on a major tick")

    # a component is written canvas-exact: everything has to fit on the canvas
    if getattr(fig, "_phd_component", False):
        canvas = fig.bbox
        for k, ax in enumerate(axes):
            for lab, box in _label_boxes(ax, r):
                if box.x0 < canvas.x0 - tol_px or box.x1 > canvas.x1 + tol_px or box.y0 < canvas.y0 - tol_px or box.y1 > canvas.y1 + tol_px:
                    problems.append(f"axes {k}: {lab} leaves the canvas (widen the component margins)")

    # rows of a grid share a height, columns a width
    grid = [(ax, ax.get_subplotspec()) for ax in axes if ax.get_subplotspec() is not None]
    for i, (a, sa) in enumerate(grid):
        for b, sb in grid[i + 1:]:
            if sa.get_gridspec() is not sb.get_gridspec():
                continue
            if sa.rowspan == sb.rowspan and abs(frames[a].height - frames[b].height) > 1.0:
                problems.append(f"axes {axes.index(a)} and {axes.index(b)} share a row but not a height")
            if sa.colspan == sb.colspan and abs(frames[a].width - frames[b].width) > 1.0:
                problems.append(f"axes {axes.index(a)} and {axes.index(b)} share a column but not a width")

    # figure-level pieces (legends hung above, panel labels) must not collide
    pieces = [(f"figure legend", lg.get_window_extent(r)) for lg in fig.legends if lg.get_visible()]
    pieces += [(f"panel label {t.get_text()!r}", t.get_window_extent(r)) for ax in axes for t in ax.texts
               if t.get_gid() == PANEL_LABEL_GID and t.get_visible()]
    targets = pieces + [(f"axes {k} frame", frames[ax]) for k, ax in enumerate(axes)]
    targets += [(f"axes {k} {lab}", box) for k, ax in enumerate(axes) for lab, box in _label_boxes(ax, r)]
    for i, (la, ba) in enumerate(pieces):
        for lb, bb in targets[i + 1:]:
            if (min(ba.x1, bb.x1) - max(ba.x0, bb.x0) > tol_px) and (min(ba.y1, bb.y1) - max(ba.y0, bb.y0) > tol_px):
                problems.append(f"{la} overlaps {lb}")

    # labels of one panel running into another panel
    boxes = {ax: _label_boxes(ax, r) for ax in axes}
    for i, a in enumerate(axes):
        for j, b in enumerate(axes):
            if a is b:
                continue
            others = [("frame", frames[b])] + boxes[b]
            for label, box in boxes[a]:
                hit = next((o for o, ob in others if box.overlaps(ob) and
                            min(box.x1, ob.x1) - max(box.x0, ob.x0) > tol_px and
                            min(box.y1, ob.y1) - max(box.y0, ob.y0) > tol_px), None)
                if hit is not None:
                    problems.append(f"axes {i}: {label} runs into axes {j} ({hit})")
    return problems


# ---------------------------------------------------------------- components

COMPONENT_MARGINS_PT = (44.0, 38.0, 10.0, 8.0)
"""Default margins of a component, left, bottom, right, top, in pt at print scale
(times the preset scale): room for tick labels and an axis label on the left and
bottom, half a tick label on the right, a little air on top."""


def component(key: str, margins_pt: tuple[float, float, float, float] | None = None, **subplot_kw):
    """
    A one-panel figure whose axes box sits at fixed margins, the same in every file.

    Components of one figure (pieces placed side by side on a slide or page) are
    only aligned if their axes boxes are identical, which neither constrained
    layout nor a tight bounding box guarantees: both move the axes with the
    width of the tick and axis labels. Here the canvas is the preset size, the
    axes box is the canvas minus fixed margins, and `save_figure` writes the
    canvas exactly (no tight box), so every component of one key lines up.

    Parameters
    ----------
    key : str
        Figure-size key; activates the preset (`update_params_string`).
    margins_pt : tuple of float, optional
        Left, bottom, right, top margins in pt at print scale, multiplied by the
        preset scale. Default `COMPONENT_MARGINS_PT`. Use one set for all the
        components that belong together.
    **subplot_kw
        Passed to `Figure.add_axes` (e.g. ``projection``).

    Returns
    -------
    (Figure, Axes)
        `save_figure` recognises the figure and writes it canvas-exact;
        `check_layout` warns if a label does not fit inside the canvas.
    """
    import matplotlib.pyplot as plt

    from phd_ui.plotting.core import update_params_string
    from phd_ui.plotting.figsize import get_figsize
    from phd_ui.plotting.params import scale_for_key

    update_params_string(key)
    w_in, h_in = get_figsize(key)
    s = scale_for_key(key)
    left, bottom, right, top = (m * s / 72 for m in (margins_pt or COMPONENT_MARGINS_PT))
    from matplotlib.layout_engine import PlaceHolderLayoutEngine

    fig = plt.figure(figsize=(w_in, h_in))
    # an explicit no-op engine: `layout=None` would fall back to the preset's
    # constrained layout, and savefig restores the engine it found after each file
    fig.set_layout_engine(PlaceHolderLayoutEngine(adjust_compatible=True, colorbar_gridspec=True))
    ax = fig.add_axes((left / w_in, bottom / h_in, 1 - (left + right) / w_in, 1 - (bottom + top) / h_in), **subplot_kw)
    fig._phd_component = True
    return fig, ax
