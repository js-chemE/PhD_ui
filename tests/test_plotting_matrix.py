import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest
from matplotlib.patches import Rectangle

from phd_ui.colors.scheme import BLUE, RED
from phd_ui.plotting import Stripe, Term, draw_matrix, draw_matrix_equation


def test_block_edges_follow_rows_cols_and_alignment():
    fig, ax = plt.subplots()
    top = draw_matrix(ax, 1.0, 5.0, rows=3, cols=4, label="X", unit=2.0)
    assert (top.x0, top.y0, top.x1, top.y1) == pytest.approx((1.0, -1.0, 9.0, 5.0))
    assert top.width == pytest.approx(8.0) and top.height == pytest.approx(6.0)
    mid = draw_matrix(ax, 0.0, 0.0, rows=2, cols=2, align="center")
    assert (mid.y0, mid.y1) == pytest.approx((-1.0, 1.0))
    bottom = draw_matrix(ax, 0.0, 0.0, rows=2, cols=2, align="bottom")
    assert (bottom.y0, bottom.y1) == pytest.approx((0.0, 2.0))
    plt.close(fig)


def test_stripes_add_patches_and_labels():
    fig, ax = plt.subplots()
    before = len([p for p in ax.patches if isinstance(p, Rectangle)])
    draw_matrix(ax, 0, 0, 6, 2, "C", color=BLUE,
                stripes=[Stripe(0, 0.5, "$c_1$"), Stripe(1.5, 2, "$c_n$"), Stripe(0, 1, "row", axis="row", color=RED)])
    rects = [p for p in ax.patches if isinstance(p, Rectangle)]
    assert len(rects) - before == 4  # the block and three stripes
    assert {t.get_text() for t in ax.texts} == {"C", "$c_1$", "$c_n$", "row"}
    plt.close(fig)


def test_equation_lays_blocks_out_left_to_right_without_overlap():
    fig, ax = plt.subplots()
    eq = draw_matrix_equation(ax, [Term("X", 6, 10), "=", Term("C", 6, 1.5, color=BLUE),
                                   Term("S", 1.5, 10, color=RED), "+", Term("E", 6, 10)], gap=0.5)
    blocks = eq.blocks
    assert len(blocks) == 4
    assert [t.get_text() for t in eq.operators] == ["=", "+"]
    for left, right in zip(blocks, blocks[1:]):
        assert right.x0 > left.x1
    assert all(b.y1 == pytest.approx(0.0) for b in blocks)  # top-aligned by default
    assert all(len(b.artists) >= 2 for b in blocks)  # rectangle and symbol, so a reveal can toggle the block
    assert ax.get_aspect() == 1.0
    assert not ax.axison
    x0, x1 = ax.get_xlim()
    assert x0 < blocks[0].x0 and x1 > blocks[-1].x1
    plt.close(fig)


def test_wide_operator_takes_its_width():
    fig, ax = plt.subplots()
    narrow = draw_matrix_equation(ax, [Term("A", 2, 2), "=", Term("B", 2, 2)])
    wide = draw_matrix_equation(ax, [Term("A", 2, 2), (r"$\log\det($", 4.0), Term("B", 2, 2)])
    assert wide.blocks[1].x0 - wide.blocks[0].x1 == pytest.approx(narrow.blocks[1].x0 - narrow.blocks[0].x1 + 3.0)
    plt.close(fig)


def test_bad_alignment_raises():
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        draw_matrix(ax, 0, 0, 1, 1, align="middle")
    plt.close(fig)
