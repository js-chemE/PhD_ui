import phd_ui.fonts as fonts
import phd_ui.plotting as plotting
import phd_ui.colors as colors

import matplotlib.pyplot as plt
from pathlib import Path

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__all__ = [
    "fonts",
    "plotting",
    "colors"
]

BASE_DIR = Path(__file__).resolve().parent
FONTS_DIR = BASE_DIR / "_assets" / "fonts"

def initialize():

    try:
        fonts.load_fonts(FONTS_DIR)
        logger.info(f"Successfully loaded fonts from {FONTS_DIR}")
    except Exception as e:
        logger.warning(f"Failed to load fonts from {FONTS_DIR}: {e}")

    try:
        plt.rcParams.update(plotting.PARAMS["single"])
        logger.info("Successfully set plotting parameters")
    except Exception as e:
        logger.warning(f"Failed to set plotting parameters: {e}")
