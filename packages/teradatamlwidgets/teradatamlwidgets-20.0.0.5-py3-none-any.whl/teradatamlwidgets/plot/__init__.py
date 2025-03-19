# -*- coding: utf-8 -*-
'''
Copyright © 2024 by Teradata.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Primary Owner: Saroop Samra (saroop.samra@teradata.com)
Secondary Owner: 
'''

import IPython
from IPython.display import clear_output, HTML, Javascript, display
from teradatamlwidgets.plot.Ui import *

def ShowPlots(plots, nrows=None, ncols=None, grid=None):
    """
    DESCRIPTION:
        Shows plot for multiple teradatamlwidgets in a subplot layout.

    PARAMETERS:
        plots: 
            Specifies the plots to be combined.
            Type: list of teradatamlwidgets.plot.Ui instances

        nrows:
            Optional Argument. 
            Required when grid argument is not provided.
            SSpecifies the number of coumns to have in combined plot.
            Type: int

        ncols:
            Optional Argument. 
            Optional Argument. Required when ncols argument is provided.
            Specifies the number of rows to have in combined plot.
            Type: int

        grid: 
            Optional Argument. Required when nrows and ncols arguments are not provided. 
            Specifies the grid to place the subplots.
            In grids dictionary, the key is a pair x and y subplot location and the value is the pair relative width cell and relative height cell representing the sublot size in units.

    RETURNS:
        None

    EXAMPLES:
        ShowPlots(plots, nrows=2, ncols=2)
        ShowPlots(plots, grid = {(1, 1): (1, 1), (1, 2): (1, 1), (2, 1): (1, 2)})
    """
    clear_output()
    fig, axes = subplots(nrows=nrows, ncols=ncols, grid=grid)
    index = 0
    for ui_plot in plots:
        ui_plot = ui_plot._ui_impl
        current_plot = ui_plot._get_current_plot()
        plot = current_plot._do_plot(ui_plot._get_base_args(), show=False, ax=axes[index], figure=fig)
        index += 1
    plot.show()