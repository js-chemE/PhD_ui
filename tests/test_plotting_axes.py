import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

from phd_ui import plotting


@pytest.fixture
def vant_hoff_axes():
    """An axes with 1000/T on x, over 1.25-2.25 K^-1 (527-170 degC)."""
    fig, ax = plt.subplots()
    inverse = np.linspace(1.25, 2.25, 50)
    ax.plot(inverse, -5000 * inverse / 1000 + 12)
    ax.set_xlim(1.25, 2.25)
    yield ax
    plt.close(fig)


# ---------------------------------------------------------------------------
# add_inverse_temperature_axis
# ---------------------------------------------------------------------------
def test_inverse_temperature_axis_maps_celsius(vant_hoff_axes):
    secondary = plotting.add_inverse_temperature_axis(vant_hoff_axes, ticks=[200, 300])
    forward, inverse = secondary._functions
    # 1000/T = 2.0 K^-1 is 500 K, i.e. 226.85 degC
    assert forward(2.0) == pytest.approx(226.85)
    assert inverse(226.85) == pytest.approx(2.0)


def test_inverse_temperature_axis_kelvin_and_scale():
    fig, ax = plt.subplots()
    ax.set_xlim(1.0, 2.0)
    secondary = plotting.add_inverse_temperature_axis(ax, unit="K", scale=1.0)
    forward, inverse = secondary._functions
    assert forward(0.002) == pytest.approx(500.0)
    assert inverse(500.0) == pytest.approx(0.002)
    assert "K" in secondary.get_xlabel()
    plt.close(fig)


def test_inverse_temperature_axis_roundtrips(vant_hoff_axes):
    secondary = plotting.add_inverse_temperature_axis(vant_hoff_axes)
    forward, inverse = secondary._functions
    probe = np.array([1.25, 1.6, 2.25])
    assert np.allclose(inverse(forward(probe)), probe)


def test_inverse_temperature_axis_survives_zero(vant_hoff_axes):
    """Matplotlib probes the transform while laying the axis out, zero included."""
    secondary = plotting.add_inverse_temperature_axis(vant_hoff_axes)
    forward, inverse = secondary._functions
    assert np.isinf(forward(np.array([0.0]))[0])
    assert np.isinf(inverse(np.array([-273.15]))[0])
    vant_hoff_axes.figure.canvas.draw()  # must not raise


def test_inverse_temperature_axis_clears_the_top_spine(vant_hoff_axes):
    plotting.add_inverse_temperature_axis(vant_hoff_axes)
    assert not any(tick.tick2line.get_visible()
                   for tick in vant_hoff_axes.xaxis.get_major_ticks())


def test_inverse_temperature_axis_can_keep_the_top_spine(vant_hoff_axes):
    vant_hoff_axes.tick_params(axis="x", which="both", top=True)
    plotting.add_inverse_temperature_axis(vant_hoff_axes, hide_primary=False)
    assert any(tick.tick2line.get_visible()
               for tick in vant_hoff_axes.xaxis.get_major_ticks())


@pytest.mark.parametrize("kwargs", [{"unit": "F"}, {"scale": 0.0}, {"scale": -1.0}])
def test_inverse_temperature_axis_rejects_bad_arguments(vant_hoff_axes, kwargs):
    with pytest.raises(ValueError):
        plotting.add_inverse_temperature_axis(vant_hoff_axes, **kwargs)


# ---------------------------------------------------------------------------
# add_reciprocal_axis, the general form underneath it
# ---------------------------------------------------------------------------
def test_reciprocal_axis_plain_inverse(vant_hoff_axes):
    secondary = plotting.add_reciprocal_axis(vant_hoff_axes)
    forward, inverse = secondary._functions
    assert forward(4.0) == pytest.approx(0.25)
    assert inverse(0.25) == pytest.approx(4.0)


def test_reciprocal_axis_on_y():
    fig, ax = plt.subplots()
    ax.set_ylim(1.0, 4.0)
    secondary = plotting.add_reciprocal_axis(ax, axis="y", where="right", scale=2.0)
    forward, _ = secondary._functions
    assert forward(4.0) == pytest.approx(0.5)
    plt.close(fig)


@pytest.mark.parametrize("kwargs", [{"scale": 0.0}, {"axis": "z"}])
def test_reciprocal_axis_rejects_bad_arguments(vant_hoff_axes, kwargs):
    with pytest.raises(ValueError):
        plotting.add_reciprocal_axis(vant_hoff_axes, **kwargs)


# ---------------------------------------------------------------------------
# freeze_layout
# ---------------------------------------------------------------------------
def test_freeze_layout_stops_the_engine_rerunning():
    fig, ax = plt.subplots(layout="constrained")
    ax.plot([0, 1], [0, 1])
    fig.canvas.draw()
    before = ax.get_position().bounds

    plotting.freeze_layout(fig)
    ax.set_ylabel("a label long enough to move the panel" * 2)
    fig.canvas.draw()

    assert ax.get_position().bounds == pytest.approx(before)
    plt.close(fig)


def test_freeze_layout_survives_a_colorbar():
    """set_layout_engine('none') raises here; freeze_layout must not."""
    fig, ax = plt.subplots(layout="constrained")
    mappable = ax.imshow([[0, 1], [2, 3]])
    fig.colorbar(mappable, ax=ax)
    fig.canvas.draw()

    plotting.freeze_layout(fig)
    fig.canvas.draw()  # must not raise
    plt.close(fig)


def test_freeze_layout_is_a_noop_without_an_engine():
    fig, ax = plt.subplots(layout="none")
    plotting.freeze_layout(fig)
    assert fig.get_layout_engine() is None
    plt.close(fig)


# ---------------------------------------------------------------------------
# draw_curve_label
# ---------------------------------------------------------------------------
def test_curve_label_follows_a_45_degree_line():
    fig, ax = plt.subplots(figsize=(4, 4))
    x = np.linspace(0, 1, 101)
    ax.plot(x, x)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.canvas.draw()

    txt = plotting.draw_curve_label(ax, x, x, "rising")
    assert txt.get_rotation() == pytest.approx(45.0, abs=1.0)
    plt.close(fig)


def test_curve_label_pins_to_at_x():
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 201)
    y = np.zeros_like(x)
    ax.plot(x, y)
    fig.canvas.draw()

    txt = plotting.draw_curve_label(ax, x, y, "flat", at_x=7.0)
    assert txt.xy[0] == pytest.approx(7.0, abs=0.05)
    plt.close(fig)


def test_curve_label_offset_moves_it_off_the_line():
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 201)
    y = np.zeros_like(x)
    ax.plot(x, y)
    fig.canvas.draw()

    centred = plotting.draw_curve_label(ax, x, y, "a", at_x=5.0)
    above = plotting.draw_curve_label(ax, x, y, "a", at_x=5.0, offset=12.0)
    below = plotting.draw_curve_label(ax, x, y, "a", at_x=5.0, offset=-12.0)

    assert above.get_position()[1] > centred.get_position()[1]
    assert below.get_position()[1] < centred.get_position()[1]
    plt.close(fig)


def test_curve_label_stays_upright_on_a_reversed_curve():
    """A van 't Hoff curve is stored high-T first, so x runs backwards."""
    fig, ax = plt.subplots(figsize=(4, 4))
    temperature = np.linspace(430.0, 1330.0, 200)
    x = 1000.0 / temperature          # decreasing
    y = -5000.0 / temperature + 8.0
    ax.plot(x, y)
    fig.canvas.draw()

    txt = plotting.draw_curve_label(ax, x, y, "reversed", at_x=1.5)
    # get_rotation() reports in [0, 360), so bring it back to (-180, 180] first
    angle = (txt.get_rotation() + 180.0) % 360.0 - 180.0
    assert abs(angle) <= 90.0, "label must not be upside down"
    plt.close(fig)


def test_curve_label_offset_is_up_screen_on_a_reversed_curve():
    fig, ax = plt.subplots()
    x = np.linspace(10, 0, 201)       # right-to-left
    y = np.zeros_like(x)
    ax.plot(x, y)
    fig.canvas.draw()

    centred = plotting.draw_curve_label(ax, x, y, "a", at_x=5.0)
    above = plotting.draw_curve_label(ax, x, y, "a", at_x=5.0, offset=12.0)
    assert above.get_position()[1] > centred.get_position()[1]
    plt.close(fig)


def test_curve_label_breaks_the_line_it_is_given():
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 201)
    y = np.zeros_like(x)
    (line,) = ax.plot(x, y)
    fig.canvas.draw()

    plotting.draw_curve_label(ax, x, y, "a long label here", line=line)

    gapped = np.isnan(line.get_xdata())
    assert gapped.any(), "the line should be broken around the label"
    assert not gapped.all(), "only a gap, not the whole curve"
    plt.close(fig)


def test_curve_label_leaves_the_line_alone_by_default():
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 201)
    y = np.zeros_like(x)
    (line,) = ax.plot(x, y)
    fig.canvas.draw()

    plotting.draw_curve_label(ax, x, y, "a long label here")
    assert not np.isnan(line.get_xdata()).any()
    plt.close(fig)


def test_curve_label_walks_inside_the_axes():
    """A label asked for the very end of a curve is moved in until it fits."""
    fig, ax = plt.subplots(figsize=(4, 4))
    x = np.linspace(0, 1, 101)
    y = np.zeros_like(x)
    ax.plot(x, y)
    ax.set_xlim(0, 1)
    fig.canvas.draw()

    txt = plotting.draw_curve_label(ax, x, y, "a wide label", at_fraction=1.0)
    box = txt.get_window_extent(renderer=fig.canvas.get_renderer())
    assert box.x1 <= ax.bbox.x1
    plt.close(fig)


@pytest.mark.parametrize(
    "x, y",
    [(np.zeros(5), np.zeros(4)), (np.zeros(1), np.zeros(1))],
)
def test_curve_label_rejects_bad_curves(x, y):
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        plotting.draw_curve_label(ax, x, y, "nope")
    plt.close(fig)
