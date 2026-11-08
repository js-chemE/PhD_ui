"""Slide ticks, panel labels and the layout check (2026-10-26)."""

import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

from phd_ui import plotting
from phd_ui.plotting import check_layout, nice_ticks, panel_label, slide_ticks


@pytest.mark.parametrize("lim, ticks", [((0, 8), [0, 4, 8]), ((0, 1), [0, 0.5, 1.0]), ((0, 760), [0, 300, 600])])
def test_nice_ticks(lim, ticks):
    step = nice_ticks(*lim)
    got = np.arange(np.ceil(lim[0] / step) * step, lim[1] + 1e-9, step)
    assert np.allclose(got, ticks)


def test_slide_ticks_leave_fixed_ticks_alone():
    fig, ax = plt.subplots()
    ax.plot([0, 8], [0, 1])
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.3, 1], labels=["0", "a", "1"])
    slide_ticks(fig)
    inside = lambda t: [v for v in t if 0 - 1e-9 <= v <= 8 + 1e-9]
    assert inside(ax.get_xticks()) == [0, 4, 8]
    assert list(ax.get_yticks()) == [0, 0.3, 1]
    plt.close(fig)


def test_panel_label_does_not_shrink_axes():
    plotting.update_params_string("double_short")
    sizes = []
    for label in (False, True):
        fig, axs = plt.subplots(1, 3, layout="constrained")
        if label:
            for ax, t in zip(axs, "abc"):
                panel_label(ax, f"({t})", inside=False)
        fig.canvas.draw()
        sizes.append(axs[0].get_window_extent().height)
        plt.close(fig)
    assert sizes[0] == pytest.approx(sizes[1])


def test_check_layout_finds_problems():
    plotting.update_params_string("slide_third")
    fig, ax = plt.subplots(layout="constrained")
    x = np.linspace(0, 1, 50)
    ax.plot(x, x)
    ax.text(0.5, 0.5, "on the line", ha="center")
    ax.text(1.02, 0.5, "outside")
    ax.set_ylabel("a very long y label that cannot fit along this short axis at all")
    problems = check_layout(fig)
    assert any("lies on data" in p for p in problems)
    assert any("crosses the axes frame" in p for p in problems)
    assert any("longer than its axis" in p for p in problems)
    plt.close(fig)


def test_check_layout_clean():
    plotting.update_params_string("double")
    fig, ax = plt.subplots(layout="constrained")
    ax.plot([0, 1], [0, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("x / –")
    ax.set_ylabel("y / –")
    assert check_layout(fig) == []
    plt.close(fig)


def test_components_share_their_axes_box():
    from phd_ui.plotting import component
    boxes = []
    for ylabel in ("y / –", r"a much longer label $V_\mathrm{p}$ / cm$^3$ g$^{-1}$"):
        fig, ax = component("slide_third")
        ax.plot([0, 1], [0, 1000])
        ax.set_ylabel(ylabel)
        fig.canvas.draw()
        boxes.append(tuple(np.round(ax.get_position().bounds, 6)))
        plt.close(fig)
    assert boxes[0] == boxes[1]


def test_check_layout_wants_ticks_at_the_ends():
    fig, ax = plt.subplots(layout="constrained")
    ax.plot([0, 1], [0, 700])
    ax.set_ylim(0, 760)
    ax.set_xlim(0, 1)
    ax.yaxis.set_major_locator(plt.MultipleLocator(200))
    assert any("does not start and end on a major tick" in p for p in check_layout(fig))
    plt.close(fig)


def test_panel_label_inside_sits_in_the_frame():
    plotting.update_params_string("double_short")
    fig, ax = plt.subplots(layout="constrained")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    lab = panel_label(ax, "(a)")
    fig.canvas.draw()
    box, frame = lab.get_window_extent(), ax.get_window_extent()
    assert frame.x0 < box.x0 and box.x1 < frame.x1 and frame.y0 < box.y0 and box.y1 < frame.y1
    assert check_layout(fig) == []
    plt.close(fig)
