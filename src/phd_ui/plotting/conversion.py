import numpy as np

INCH2CM = 2.54

def cm_to_inches(cm: float | int | np.floating | np.integer | np.ndarray) -> float | int | np.floating | np.integer | np.ndarray:
    return cm / INCH2CM

def inches_to_cm(inches: float | int | np.floating | np.integer | np.ndarray) -> float | int | np.floating | np.integer | np.ndarray:
    return inches * INCH2CM