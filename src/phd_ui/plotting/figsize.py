from pathlib import Path
from phd_ui.plotting.conversion import cm_to_inches
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

module_dir = Path(__file__).resolve().parent.parent
asset_dir = module_dir / "_assets"



def get_figsizes(in_metric: bool = True) -> dict[str, Tuple[float, float]]:
    import json
    figsize_path = asset_dir / "figsize.json"
    with open(figsize_path, "r") as f:
        figsize = json.load(f)
    if not in_metric:
        for key, value in figsize.items():
            figsize[key] = tuple(cm_to_inches(v) for v in value)
    return figsize

def get_figsize(key: str, in_metric: bool = True) -> Tuple[float, float]:
    try:
        figsize_dict = get_figsizes(in_metric=in_metric)
        return figsize_dict[key]
    except KeyError:
        logger.warning(f"Key '{key}' not found in figsize dictionary. Returning default figsize.")
        print(f"Key '{key}' not found in figsize dictionary. Returning default figsize.")
        print(f"Available keys: {list(get_figsizes(in_metric=in_metric).keys())}")
        return (6.4, 4.8)  # default matplotlib figsize