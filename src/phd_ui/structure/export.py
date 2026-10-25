"""
One call to every file format: SVG, PNG, PDF for a still, GIF and SVG for a spin.

- **SVG** comes from ``phd_ui.sketch``: structured (named groups, atom and
  bond ids), small, the file to finish in Illustrator.
- **PNG and PDF** come from matplotlib (``plotting.draw_projection`` and
  ``plotting.save_figure``), so no browser or Cairo is needed.
- **GIF** of a spin from ``plotting.save_spin_gif``; the animated **SVG**
  from ``sketch.spin`` plays in a browser and in Obsidian.

All formats draw the same ``render`` output, so they agree.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from phd_ui.structure.look import Look
from phd_ui.structure.render import render
from phd_ui.structure.view import Projection

__all__ = ["export", "export_spin"]

_MM_PER_PT = 25.4 / 72


def _box(drawings: list, pad_mm: float, pm_per_mm: float) -> tuple[float, float, float, float]:
    xs0, ys0, xs1, ys1 = zip(*(d.bounds() for d in drawings))
    pad = pad_mm * pm_per_mm
    return min(xs0) - pad, min(ys0) - pad, max(xs1) + pad, max(ys1) + pad


def export(p: Projection, directory: str | Path, name: str, formats: Sequence[str] = ("svg", "png", "pdf"),
           look: Look | None = None, pm_per_mm: float = 11.0, pad_mm: float = 1.5, dpi: int = 300) -> list[Path]:
    """
    Write one view of a molecule in several formats, at its natural size.

    Parameters
    ----------
    p : Projection
        The view.
    directory : str or pathlib.Path
        Output folder, created if missing.
    name : str
        File stem.
    formats : sequence of str, optional
        Any of ``'svg'``, ``'png'``, ``'pdf'``.
    look : Look, optional
        Appearance.
    pm_per_mm : float, optional
        Drawing scale; sets the final size (methanol is about 30 mm at 11).
    pad_mm : float, optional
        Margin around the atoms.
    dpi : int, optional
        PNG resolution.

    Returns
    -------
    list of pathlib.Path
        The files written.
    """
    import matplotlib.pyplot as plt

    import phd_ui.sketch as sk

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    pm_per_pt = pm_per_mm * _MM_PER_PT
    x0, y0, x1, y1 = _box([render(p, look, pm_per_pt)], pad_mm, pm_per_mm)
    w_mm, h_mm = (x1 - x0) / pm_per_mm, (y1 - y0) / pm_per_mm
    out = []
    if "svg" in formats:
        scene = sk.Scene(w_mm, h_mm, pm_per_mm=pm_per_mm, title=name, source="phd_ui.structure.export")
        sk.molecule(scene.layer(name), p, -x0, y1, name=name, look=look)
        out.append(scene.save(directory, name))
    raster = [f for f in ("png", "pdf") if f in formats]
    if raster:
        from phd_ui.plotting.molecule import draw_projection

        rc = {"figure.constrained_layout.use": False, "savefig.bbox": None, "savefig.transparent": True}
        with plt.rc_context(rc):
            fig = plt.figure(figsize=(w_mm / 25.4, h_mm / 25.4))
            ax = fig.add_axes((0, 0, 1, 1))
            ax.set_xlim(x0, x1)
            ax.set_ylim(y0, y1)
            ax.set_aspect("equal")
            ax.axis("off")
            draw_projection(ax, p, look=look)
            for f in raster:
                path = directory / f"{name}.{f}"
                fig.savefig(path, dpi=dpi)
                out.append(path)
        plt.close(fig)
    return out


def export_spin(frames: list[Projection], directory: str | Path, name: str, formats: Sequence[str] = ("svg", "gif"),
                look: Look | None = None, pm_per_mm: float = 11.0, pad_mm: float = 1.5, period_s: float = 6.0,
                dpi: int = 150) -> list[Path]:
    """
    Write a turning molecule as animated SVG and/or GIF, sized to fit every frame.

    Parameters
    ----------
    frames : list of Projection
        From ``spin``.
    directory, name : str or pathlib.Path, str
        Output folder and stem.
    formats : sequence of str, optional
        ``'svg'`` (animated, SMIL) and/or ``'gif'``.
    look : Look, optional
        Appearance.
    pm_per_mm, pad_mm : float, optional
        Scale and margin, as in :func:`export`.
    period_s : float, optional
        Seconds per turn.
    dpi : int, optional
        GIF resolution.

    Returns
    -------
    list of pathlib.Path
        The files written.
    """
    import phd_ui.sketch as sk

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    x0, y0, x1, y1 = _box([render(f, look, pm_per_mm * _MM_PER_PT) for f in frames], pad_mm, pm_per_mm)
    w_mm, h_mm = (x1 - x0) / pm_per_mm, (y1 - y0) / pm_per_mm
    out = []
    if "svg" in formats:
        scene = sk.Scene(w_mm, h_mm, pm_per_mm=pm_per_mm, title=name, source="phd_ui.structure.export_spin")
        sk.spin(scene.layer(name), frames, -x0, y1, period_s=period_s, look=look)
        out.append(scene.save(directory, name))
    if "gif" in formats:
        from phd_ui.plotting.molecule import save_spin_gif

        out.append(Path(save_spin_gif(frames, directory / f"{name}.gif", period_s=period_s,
                                      size_cm=(w_mm / 10, h_mm / 10), dpi=dpi, look=look)))
    return out
