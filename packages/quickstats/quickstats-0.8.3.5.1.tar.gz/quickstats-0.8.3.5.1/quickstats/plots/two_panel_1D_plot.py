from typing import Dict, Optional, Union, List, Tuple
import pandas as pd
import numpy as np
from quickstats.plots import get_color_cycle, get_cmap

from quickstats.plots import AbstractPlot, StatPlotConfig
from quickstats.plots.core import get_rgba
from quickstats.plots.template import create_transform, handle_has_label
from quickstats.utils.common_utils import combine_dict

class TwoPanel1DPlot(AbstractPlot):

    STYLES = {
        'fill_between': {
             'alpha': 0.3,
             'hatch': None,
             'linewidth': 1.0
        },
        'ratio_frame':{
            'height_ratios': (1, 1),
            'hspace': 0.05           
        },
        
    }
    
    CONFIG = {
        'errorband_legend': True
    }
    
    def __init__(self, data_map:Union[pd.DataFrame, Dict[str, pd.DataFrame]],
                 label_map:Optional[Dict]=None,
                 styles_map:Optional[Dict]=None,
                 color_cycle=None,
                 color_cycle_lower=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None,
                 config:Optional[Dict]=None):
        
        self.data_map = data_map
        
        super().__init__(color_cycle=color_cycle,
                         label_map=label_map,
                         styles_map=styles_map,
                         styles=styles,
                         analysis_label_options=analysis_label_options,
                         config=config)
        if color_cycle_lower is not None:
            self.cmap_lower = get_cmap(color_cycle_lower)
        else:
            self.cmap_lower = None
        
    def get_default_legend_order(self):
        if not isinstance(self.data_map, dict):
            return []
        else:
            return list(self.data_map)
        
    def draw_single_data(self, ax, data:pd.DataFrame,
                         xattrib:str, yattrib:str,
                         yerrloattrib:Optional[str]=None,
                         yerrhiattrib:Optional[str]=None,
                         stat_configs:Optional[List[StatPlotConfig]]=None,
                         styles:Optional[Dict]=None,
                         label:Optional[str]=None):
        data = data.reset_index()
        x, y = data[xattrib].values, data[yattrib].values
        indices = np.argsort(x)
        x, y = x[indices], y[indices]
        draw_styles = combine_dict(self.styles['plot'], styles)
        fill_styles = combine_dict(self.styles['fill_between'])
            
        if (yerrloattrib is not None) and (yerrhiattrib is not None):
            yerrlo = data[yerrloattrib][indices]
            yerrhi = data[yerrhiattrib][indices]
            handle_fill = ax.fill_between(x, yerrlo, yerrhi,
                                          **fill_styles)
        else:
            handle_fill = None
        
        handle_plot = ax.plot(x, y, **draw_styles, label=label)
        if isinstance(handle_plot, list) and (len(handle_plot) == 1):
            handle_plot = handle_plot[0]

        if handle_fill and ('color' not in fill_styles):
            plot_color = handle_plot.get_color()
            fill_color = get_rgba(plot_color)
            handle_fill.set_color(fill_color)

        if self.config['errorband_legend'] and (handle_fill is not None):
            handles = (handle_plot, handle_fill)
        else:
            handles = handle_plot
        return handles
    
    def draw(self, xattrib:str, yattrib:str,
             targets_upper:Optional[List[str]],
             targets_lower:Optional[List[str]],
             yerrloattrib:Optional[str]=None,
             yerrhiattrib:Optional[str]=None,
             xlabel:Optional[str]=None,
             xmin:Optional[float]=None, xmax:Optional[float]=None,
             ylabel_upper:Optional[str]=None,
             ylabel_lower:Optional[str]=None,
             ymin_lower:Optional[float]=None,
             ymin_upper:Optional[float]=None,
             ymax_lower:Optional[float]=None,
             ymax_upper:Optional[float]=None,
             ypad_upper:Optional[float]=0.3,
             ypad_lower:Optional[float]=0.3,
             logx:bool=False,
             logy_upper:bool=False,
             logy_lower:bool=False):

        if not isinstance(self.data_map, dict):
            raise ValueError('invalid data format')

        if self.cmap_lower is not None:
            prop_cycle_lower = get_color_cycle(self.cmap_lower)
        else:
            prop_cycle_lower = None
        ax_upper, ax_lower = self.draw_frame(logx=logx, logy=logy_upper,
                                             logy_lower=logy_lower,
                                             prop_cycle_lower=prop_cycle_lower,
                                             ratio=True)

        if self.styles_map is None:
            styles_map = {k:None for k in self.data_map}
        else:
            styles_map = self.styles_map
            
        if self.label_map is None:
            label_map = {k:k for k in self.data_map}
        else:
            label_map = self.label_map
            
        
        for domain, ax, targets in [('upper', ax_upper, targets_upper),
                                    ('lower', ax_lower, targets_lower)]:
            handles = {}
            for target in targets:
                data = self.data_map[target]
                styles = styles_map.get(target, None)
                label = label_map.get(target, "")
                handle = self.draw_single_data(ax, data,
                                               xattrib=xattrib,
                                               yattrib=yattrib,
                                               yerrloattrib=yerrloattrib,
                                               yerrhiattrib=yerrhiattrib,
                                               styles=styles,
                                               label=label)
                handles[target] = handle
            self.update_legend_handles(handles, domain=domain)

        self.draw_axis_components(ax_upper, ylabel=ylabel_upper)
        ax_upper.tick_params(axis='x', labelbottom=False)
        self.draw_axis_components(ax_lower, xlabel=xlabel, ylabel=ylabel_lower)
        self.set_axis_range(ax_upper, xmin=xmin, xmax=xmax,
                            ymin=ymin_upper, ymax=ymax_upper, ypad=ypad_upper)
        self.set_axis_range(ax_lower, xmin=xmin, xmax=xmax,
                            ymin=ymin_lower, ymax=ymax_lower, ypad=ypad_lower)
        self.draw_legend(ax_upper, domains='upper')
        self.draw_legend(ax_lower, domains='lower', **self.styles['legend_lower'])
        return ax_upper, ax_lower
