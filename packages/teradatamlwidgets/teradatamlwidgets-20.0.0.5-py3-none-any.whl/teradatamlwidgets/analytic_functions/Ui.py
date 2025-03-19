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
from teradatamlwidgets.analytic_functions.UiImpl import _UiImpl
from teradatamlwidgets.connection_teradataml import Connection


class Ui:
    """
    The teradatamlwidgets Interactive Analytic Function UI.
    """
    def __init__(
        self, 
        outputs=None, 
        connection=None, 
        function="", 
        inputs=None, 
        export_settings="", 
        default_database="", 
        val_location="",
        volatile=False,
        eda_mode=False):
        """
        DESCRIPTION:
            Constructor for teradatamlwidgets Interactive Analytic Function UI.

        PARAMETERS:
            outputs: 
                Optional Argument. 
                Specifies the output name(s) of the output table(s).
                Type: str

            connection: 
                Optional Argument. 
                Specifies the specific connection; could be teradataml based (i.e. TeradatamlConnection 
                instance) or another platform.
                Type: Connection

            function: 
                Optional Argument. 
                Specifies the name of the function, otherwise list of all functions will show.
                Type: str

            inputs: 
                Optional Argument. 
                Specifies the input tables desired allowing for selection in UI, otherwise user 
                must type in input table name or a teradataml DataFrame.
                Type: List of str or List of teradataml.DataFrame

            export_settings: 
                Optional Argument. 
                Specifies the filename user where the UI parameters will be saved and loaded from. 
                This allows you to avoid having to retype the UI parameters the next time you run the cell.
                Type: str

            default_database: 
                Optional Argument. 
                Specifies the default database.
                Type: str

            val_location: 
                Optional Argument. 
                Specifies the VAL location.
                Type: str

            volatile: 
                Optional Argument. 
                Specifies whether output table is volatile or not.
                Type: bool

            eda_mode: 
                Optional Argument. 
                Specifies whether to call the separate EDA UI or teradatamlwidgets based UI.
                Type: bool

        RETURNS:
            Instance of the UI class

        EXAMPLES:
            from teradatamlwidgets.analytic_functions.Ui import * 
            # EXAMPLE 1: Simple UI Call
            inputs = ["ibm_stock", "titanic"]
            outputs = ["Project_OutMovingAverage1"]
            ui = Ui(outputs=outputs, inputs=inputs)
            # EXAMPLE 2: Moving Average
            inputs = ["ibm_stock"]
            outputs = ["Project_OutMovingAverageTest"]
            ui = Ui(function= 'MovingAverage',
                    outputs=outputs, 
                    inputs=inputs,  
                    export_settings="MovingAverage.json")
        """

        # Error checking
        found_correct_version = False
        try:
            from teradataml.common.constants import TeradataAnalyticFunctionInfo
            found_correct_version = hasattr(TeradataAnalyticFunctionInfo, 'VAL')
        except ModuleNotFoundError as err:
            print("Error you do not have teradataml installed")
            return
        if not found_correct_version:
            #print("Error you do not have correct version of teradataml")
            pass
        try:
            import ipywidgets
        except ModuleNotFoundError as err:
            print("Error you do not have ipywidgets installed")
            return


        if not connection:
            connection = Connection()

        self._ui_impl = _UiImpl(connection, 
                        outputs,
                        function=function, 
                        inputs=inputs,  
                        export_settings=export_settings,
                        default_database=default_database,
                        val_location=val_location,
                        volatile=volatile,
                        eda_mode=eda_mode)
    
    def get_output_dataframe(self, output_index=0, output_name=""):
        """
        Access the output dataframe.

        PARAMETERS:
            output_index: 
                Optional Argument. 
                The index of the output to return, by default is set to 0, and will show the first output.
                Either output_index or output_name should be set.
                Default Value: 0
                Type: int
        
            output_name: 
                Optional Argument. 
                The name of the output to return.
                Either output_index or output_name should be set.
                Type: str
                Default Value: ""
                
        EXCEPTIONS:
            None.

        RETURNS: 
            The output dataframe
            Type: teradataml.DataFrame
        
        EXAMPLE:
            df = ui.get_output_dataframe(0)
        """
        return self._ui_impl._get_output_dataframe(output_index, output_name)


