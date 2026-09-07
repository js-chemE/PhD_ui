import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from phd_ui import plotting


@pytest.fixture
def strip():
    """Three panels carrying the same two labelled series, as a figure row."""
    fig, axes = plt.subplots(1, 3, constrained_layout=True)
    for ax in axes:
        ax.plot([0, 1], [0, 1], label="measured")
        ax.plot([0, 1], [1, 0], label="model")
    yield fig, axes
    plt.close(fig)


# ---------------------------------------------------------------------------
# legend_above
# ---------------------------------------------------------------------------
def test_entries_are_collected_once_across_the_row(strip):
    fig, _ = strip
    legend = plotting.legend_above(fig)
    assert [text.get_text() for text in legend.get_texts()] == ["measured", "model"]


def test_defaults_to_a_single_row(strip):
    fig, _ = strip
    assert plotting.legend_above(fig)._ncols == 2
    assert plotting.legend_above(fig, ncol=1)._ncols == 1


def test_sits_above_the_canvas_and_right_aligned(strip):
    """Anchored outside the figure, so the panels keep their full rectangle."""
    fig, axes = strip
    legend = plotting.legend_above(fig, pad=0.02)
    x, y = legend.get_bbox_to_anchor().transformed(fig.transFigure.inverted()).p0
    assert y == pytest.approx(1.02)
    assert x == pytest.approx(1.0)
    fig.canvas.draw()
    right = max(ax.get_position().x1 for ax in axes)
    assert legend.get_window_extent().transformed(
        fig.transFigure.inverted()
    ).x1 == pytest.approx(right, abs=0.02)


def test_alignment_names_pick_the_anchor(strip):
    fig, _ = strip
    for align, expected in [("right", 1.0), ("left", 0.0), ("center", 0.5)]:
        legend = plotting.legend_above(fig, align=align)
        x, _ = legend.get_bbox_to_anchor().transformed(fig.transFigure.inverted()).p0
        assert x == pytest.approx(expected)


def test_unknown_alignment_raises(strip):
    fig, _ = strip
    with pytest.raises(ValueError, match="align must be one of"):
        plotting.legend_above(fig, align="top")


def test_nothing_labelled_raises():
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    with pytest.raises(ValueError, match="no labelled artists"):
        plotting.legend_above(fig)
    plt.close(fig)


def test_explicit_handles_win_over_the_axes(strip):
    fig, _ = strip
    handle = plt.Line2D([], [], color="k")
    legend = plotting.legend_above(fig, [handle], ["one only"])
    assert [text.get_text() for text in legend.get_texts()] == ["one only"]
