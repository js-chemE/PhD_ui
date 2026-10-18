import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

from phd_ui.plotting import cm_to_inches, panel_grid


def _panel_box_cm(fig, ax):
    """Panel (x0 from left, y0 from top, width, height) in cm."""
    w_in, h_in = fig.get_size_inches()
    b = ax.get_position()
    to_cm = 2.54
    return (b.x0 * w_in * to_cm, (1 - b.y1) * h_in * to_cm, b.width * w_in * to_cm, b.height * h_in * to_cm)


def test_panels_have_the_requested_size():
    fig, axes = panel_grid(2, 3, panel_cm=3.0)
    for ax in axes.ravel():
        _, _, w, h = _panel_box_cm(fig, ax)
        assert w == pytest.approx(3.0) and h == pytest.approx(3.0)
    plt.close(fig)


def test_growing_the_grid_moves_nothing():
    small, a = panel_grid(2, 2, panel_cm=3.0)
    big, b = panel_grid(3, 4, panel_cm=3.0)
    for i in range(2):
        for j in range(2):
            assert _panel_box_cm(small, a[i, j]) == pytest.approx(_panel_box_cm(big, b[i, j]))
    assert big.get_size_inches()[0] > small.get_size_inches()[0]
    assert big.get_size_inches()[1] > small.get_size_inches()[1]
    plt.close("all")


def test_figure_size_is_margins_panels_and_gaps():
    fig, _ = panel_grid(1, 2, panel_cm=(4.0, 2.0), gap_cm=(1.0, 0.5), margin_cm=(1.0, 1.0, 1.0, 1.0))
    assert fig.get_size_inches() == pytest.approx((cm_to_inches(1 + 4 + 1 + 4 + 1), cm_to_inches(1 + 2 + 1)))
    assert fig.get_layout_engine() is None
    plt.close(fig)


def test_shared_axes_link_and_hide_inner_labels():
    fig, axes = panel_grid(2, 2, sharex="col", sharey="row")
    axes[1, 0].set_xlim(0, 7)
    assert axes[0, 0].get_xlim() == pytest.approx((0, 7))
    assert not axes[0, 0].xaxis.get_tick_params()["labelbottom"]
    assert not axes[0, 1].yaxis.get_tick_params()["labelleft"]
    plt.close(fig)


def test_merged_block_spans_the_outer_edges_of_its_cells():
    plain, p = panel_grid(2, 3, panel_cm=3.0, gap_cm=0.5)
    fig, axes = panel_grid(2, 3, panel_cm=3.0, gap_cm=0.5, merge=[(0, slice(1, 3)), (slice(0, 2), 0)])
    x0, y0, w, h = _panel_box_cm(fig, axes[0, 1])
    assert axes[0, 1] is axes[0, 2]
    assert (x0, y0) == pytest.approx(_panel_box_cm(plain, p[0, 1])[:2])
    assert w == pytest.approx(3.0 + 0.5 + 3.0) and h == pytest.approx(3.0)
    _, _, w, h = _panel_box_cm(fig, axes[1, 0])
    assert axes[0, 0] is axes[1, 0] and h == pytest.approx(6.5) and w == pytest.approx(3.0)
    assert _panel_box_cm(fig, axes[1, 2]) == pytest.approx(_panel_box_cm(plain, p[1, 2]))
    assert len(set(map(id, axes.ravel()))) == 4
    plt.close("all")


def test_overlapping_merges_are_refused():
    with pytest.raises(ValueError):
        panel_grid(2, 2, merge=[(0, slice(0, 2)), (slice(0, 2), 1)])
    plt.close("all")


def test_mosaic_labels_and_empty_cells():
    from phd_ui.plotting import panel_mosaic
    fig, ax = panel_mosaic([["a", "b", "b"], ["c", "b", "b"], [".", "d", "d"]], panel_cm=2.0, gap_cm=0.4)
    assert set(ax) == {"a", "b", "c", "d"}
    _, _, w, h = _panel_box_cm(fig, ax["b"])
    assert w == pytest.approx(4.4) and h == pytest.approx(4.4)
    with pytest.raises(ValueError):
        panel_mosaic([["a", "b"], ["b", "a"]])
    plt.close("all")


def test_shared_axes_with_a_merged_panel():
    fig, axes = panel_grid(2, 3, sharex="col", merge=[(1, slice(1, 3))])
    assert axes[1, 1] is axes[1, 2]
    plt.close(fig)


def test_one_gap_per_row_moves_only_what_is_below():
    even, a = panel_grid(3, 2, panel_cm=3.0, gap_cm=(0.4, 0.4))
    wide, b = panel_grid(3, 2, panel_cm=3.0, gap_cm=(0.4, [1.4, 0.4]))
    assert _panel_box_cm(wide, b[0, 1]) == pytest.approx(_panel_box_cm(even, a[0, 1]))
    assert _panel_box_cm(wide, b[1, 0])[1] == pytest.approx(_panel_box_cm(even, a[1, 0])[1] + 1.0)
    with pytest.raises(ValueError):
        panel_grid(3, 2, gap_cm=(0.4, [1.0]))
    plt.close("all")
