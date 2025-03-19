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


from teradatamlwidgets.eda.UiImpl import _UiImpl


class Ui:
    """
    The teradatamlwidgets Interactive EDA UI.
    """

    def __init__(
        self, 
        df,
        html=None):
        """
        DESCRIPTION:
            Constructor for teradatamlwidgets EDA UI.

        PARAMETERS:
            df: 
                Required Argument. 
                Specifies the name of the input table.
                Type: DataFrame
            html:
                String with HTML tags.
                Types: str
                

        RETURNS:
            Instance of the EDA UI Implementation.

        RAISES:
            None.
        """
        
        
        self._ui_impl=_UiImpl(df=df, html=html)

    def display_ui(self):
        """
        Displays the UI.

        PARAMETERS:
            None.
                
        RAISES:
            None.

        RETURNS: 
            None
        
        EXAMPLE:
            ui.display_ui()
        """
        self._ui_impl.display_ui()

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
                
        RAISES:
            None.

        RETURNS: 
            teradataml.DataFrame
        
        EXAMPLE:
            df = ui.get_output_dataframe(0)
        """
        return self._ui_impl._get_output_dataframe(output_index, output_name)
