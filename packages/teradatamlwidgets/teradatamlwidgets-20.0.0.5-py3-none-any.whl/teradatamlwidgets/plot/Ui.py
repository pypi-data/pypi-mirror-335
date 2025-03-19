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

import os
import sys
import ipywidgets as widgets
import IPython
from IPython.display import clear_output, HTML, Javascript, display
from teradataml import * 
from teradatamlwidgets.plot.PlotImpl import *
from teradatamlwidgets.plot.UiImpl import _UiImpl

class Ui:
    """
    The teradatamlwidgets Interactive Plot UI.
    """

    def __init__(self, 
                current_plot="Line", 
                table_name="", 
                df=None, 
                connection=None, 
                default_database="", 
                eda_mode=False, 
                **kwargs):
        """
        DESCRIPTION:
            Constructor for teradatamlwidgets Interactive Plot UI.

        PARAMETERS:
            df: 
                Required Argument.
                Specifies the teradataml DataFrame containing the data.
                Type: teradataml.DataFrame

            current_plot:
                Optional Argument. 
                Specifies the type of plot, there is regardless a drop down to choose from.
                Type: str

            connection: 
                Optional Argument. 
                Specifies the specific connection; could be teradataml based (i.e. TeradatamlConnection instance) 
                or another platform.
                Type: Connection

            default_database: 
                Optional Argument. 
                Specifies the default database.
                Type: str

            eda_mode:
                Optional Argument. 
                Specifies whether to call the separate EDA UI or teradatamlwidgets based UI.
                Type: bool

        RETURNS:
            Instance of the UI class

        EXAMPLES:
            ui = Ui(current_plot = "Bar")
        """
        
        self._ui_impl = _UiImpl(
                        current_plot=current_plot, 
                        table_name=table_name,  
                        df=df,
                        connection=connection,
                        default_database=default_database,
                        eda_mode = eda_mode,
                        **kwargs)
    
