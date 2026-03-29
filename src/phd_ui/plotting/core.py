import matplotlib.pyplot as plt
from ui.plotting.params_double import params_double
from ui.plotting.params_single import params_single
from matplotlib.axes import Axes
from typing import Tuple
import numpy as np

INCH2CM = 2.54

def cm_to_inches(cm: float | int | np.floating | np.integer | np.ndarray) -> float | int | np.floating | np.integer | np.ndarray:
    return cm / INCH2CM

def inches_to_cm(inches: float | int | np.floating | np.integer | np.ndarray) -> float | int | np.floating | np.integer | np.ndarray:
    return inches * INCH2CM

PARAMS = {
    "double": params_double,
    "single": params_single
}

FIGSIZE = {k : v["figure.figsize"] for k, v in PARAMS.items()}

def update_params(params: dict) -> None:
    plt.rcParams.update(params)


def update_params_string(params: str, **kwargs) -> None:
    params_dict = PARAMS[params]
    for k, v in kwargs:
        params_dict[k] = v
    update_params(params_dict)


def set_locators(
        ax : Axes,
        auto_minor_numbers: Tuple[int | None, int | None] = (2, 2),
        multiple_major: Tuple[float | int | None, float | int | None] = (None, None)
        ) -> None:
    from matplotlib.ticker import AutoMinorLocator
    from matplotlib.ticker import MultipleLocator
    if multiple_major[0] is not None:
        ax.axes.xaxis.set_major_locator(MultipleLocator(multiple_major[0])) # type: ignore
    if auto_minor_numbers[0] is not None:
        ax.axes.xaxis.set_minor_locator(AutoMinorLocator(auto_minor_numbers[0])) # type: ignore
    if multiple_major[1] is not None:
        ax.axes.yaxis.set_major_locator(MultipleLocator(multiple_major[1])) # type: ignore
    if auto_minor_numbers[1] is not None:
        ax.axes.yaxis.set_minor_locator(AutoMinorLocator(auto_minor_numbers[1])) # type: ignore
    
    #fix_right_ylabels(ax)


# def fix_right_ylabels(ax):
#     for label in ax.yaxis.get_ticklabels(which="both"):
#         if label.get_position()[0] > 0:  # right side
#             label.set_horizontalalignment("right")

def fix_right_ylabels(ax: Axes) -> None:
    """
    Right-align ytick labels on the right axis,
    while keeping outward padding consistent.
    """

    all_dx = [label.get_window_extent().bounds[2] for label in ax.yaxis.get_ticklabels()]
    min_dx = min(all_dx)
    max_dx = max(all_dx)
    delta_dx = max_dx - min_dx

    for label, tick in zip(ax.yaxis.get_ticklabels(), ax.yaxis.get_major_ticks()):
        pad = tick.get_pad()
        xloc = label.get_position()[0]

        #width = label.get_width()  # need to draw first to get the width
        
        if label.get_position()[0] > 0:  # right-side labels
            label.set_horizontalalignment("right")
            print(delta_dx)
            label.set_x(xloc + (1.5*pad) / ax.figure.dpi)  # shift outward

def right_align_yticks(ax, pad_points=6):
    """
    Right-align right-side y-tick labels with a fixed padding in points from the axis spine.
    """
    # Apply padding via tick_params (pad is in points)
    ax.tick_params(axis="y", which="major", pad=pad_points)
    ax.tick_params(axis="y", which="minor", pad=pad_points)
    
    # Right-align right-side labels
    for tick in ax.yaxis.get_major_ticks() + ax.yaxis.get_minor_ticks():
        right_label = tick.label2  # right-side label
        if right_label.get_text():  # if a label exists
            right_label.set_horizontalalignment("right")

def fix_right_ylabels_with_padding(ax, pad_pixels=6):
    """
    Right-align y-tick labels on the right side with a fixed pixel padding from the spine.
    """
    fig = ax.figure
    fig.canvas.draw()  # ensure text positions are computed

    for label in ax.yaxis.get_ticklabels():
        x, y = label.get_position()
        # check if this label is on the right
        if x > 0:  
            label.set_horizontalalignment("right")
            
            # convert pixels to axis units
            bbox = label.get_window_extent(renderer=fig.canvas.get_renderer())
            trans = ax.transAxes.inverted()
            # compute padding in axis units
            shift_axes = trans.transform([(bbox.x1 + pad_pixels, 0)])[0][0] - trans.transform([(bbox.x1, 0)])[0][0]
            
            label.set_x(x + shift_axes)
