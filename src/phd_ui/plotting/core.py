import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from typing import Tuple
from phd_ui.plotting.params import BASE_PARAMS 
from phd_ui.plotting.figsize import get_figsizes
import numpy as np

from matplotlib.ticker import AutoMinorLocator, MultipleLocator


FIGSIZE = get_figsizes(in_metric=False)

PARAMS = {key: {**BASE_PARAMS, "figure.figsize": FIGSIZE[key]} for key in FIGSIZE.keys()}

def update_params(params: dict) -> None:
    plt.rcParams.update(params)


def update_params_string(params: str, **kwargs) -> None:
    params_dict = PARAMS[params]
    for k, v in kwargs.items():
        params_dict[k] = v
    update_params(params_dict)


def set_locators(ax: plt.Axes, *, minor_x: int = 2, minor_y: int = 2, major_x: int | float | None = None, major_y: int | float | None = None):
    if major_x is not None:
        ax.xaxis.set_major_locator(MultipleLocator(major_x))
    if major_y is not None:
        ax.yaxis.set_major_locator(MultipleLocator(major_y))
    if minor_x is not None and ax.get_xscale() == "linear":
        ax.xaxis.set_minor_locator(AutoMinorLocator(minor_x))
    if minor_y is not None and ax.get_yscale() == "linear":
        ax.yaxis.set_minor_locator(AutoMinorLocator(minor_y))
    

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
