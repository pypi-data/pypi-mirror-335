from typing import List, Dict, Optional, Union

import numpy as np

from matplotlib.colors import ListedColormap, LinearSegmentedColormap

import quickstats
from quickstats import DescriptiveEnum

from .colors import (
    register_colors, register_cmaps,
    plot_color_gradients, get_cmap,
    get_rgba, get_cmap_rgba,
    get_color_cycle
)

__all__ = ["ErrorDisplayFormat", "PlotFormat",
           "reload_styles", "use_style",
           "register_colors", "register_cmaps",
           "plot_color_gradients", "get_cmap",
           "get_rgba", "get_cmap_rgba", "get_color_cycle"]

class ErrorDisplayFormat(DescriptiveEnum):
    ERRORBAR = (0, "Error bar", "errorbar")
    FILL     = (1, "Fill interpolated error range across bins", "fill_between")
    SHADE    = (2, "Shade error range in each bin", "bar")
    
    def __new__(cls, value:int, description:str="", artist:str=""):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.artist = artist
        return obj
    
class PlotFormat(DescriptiveEnum):
    ERRORBAR = (0, "Error bar", "errorbar")
    HIST     = (1, "Histogram", "hist")
                
    def __new__(cls, value:int, description:str="", artist:str=""):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.artist = artist
        return obj

def reload_styles():
    from matplotlib import style
    style.core.USER_LIBRARY_PATHS.append(quickstats.stylesheet_path)
    style.core.reload_library()

def use_style(name:str='quick_default'):
    from matplotlib import style
    style.use(name)