from phd_ui.renaming.renaming import Renaming
import os

MODULE_DIR = os.path.dirname(__file__)
CONFIG_DIR = os.path.join(MODULE_DIR, r"../_assets")

MAIN_RENAMING = Renaming(
    filepath = os.path.join(CONFIG_DIR, "_renaming.xlsx"),
)

__all__ = ["Renaming", "MAIN_RENAMING"]