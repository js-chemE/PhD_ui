from os import PathLike
from pathlib import Path

import matplotlib.font_manager as fm


def load_fonts(fonts_dir: str | Path | PathLike[str]) -> None:
    """
    Recursively register all TTF/OTF fonts with Matplotlib.

    Parameters
    ----------
    fonts_dir : str or Path or PathLike[str]
        Directory to search recursively for ``.ttf``/``.otf`` font files.

    Raises
    ------
    FileNotFoundError
        If `fonts_dir` is not an existing directory.
    RuntimeError
        If no ``.ttf``/``.otf`` files are found under `fonts_dir`.
    """
    fonts_dir = Path(fonts_dir).expanduser().resolve()

    if not fonts_dir.is_dir():
        raise FileNotFoundError(f"Font directory not found: {fonts_dir}")

    font_files = list(fonts_dir.rglob("*.ttf")) + list(fonts_dir.rglob("*.otf"))

    if not font_files:
        raise RuntimeError(f"No font files found under {fonts_dir}")

    for font_path in font_files:
        fm.fontManager.addfont(str(font_path))
