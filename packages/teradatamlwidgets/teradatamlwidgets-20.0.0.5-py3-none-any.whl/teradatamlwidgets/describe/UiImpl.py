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
import json
import ipywidgets
from IPython.display import clear_output, HTML,Javascript, display
import teradataml
import pandas as pd
from teradataml import DataFrame, ColumnSummary, CategoricalSummary, GetFutileColumns
from teradatamlwidgets.base_ui import _BaseUi


class _UiImpl(_BaseUi):
    """
    Private class that implements teradatamlwidgets Describe UI.
    """
    def __init__(
        self, 
        df):
        """
        DESCRIPTION:
            Constructor for private class that implements teradatamlwidgets Describe UI.

        PARAMETERS:
            df: 
                Required Argument. 
                Specifies the name of the input table.
                Type: DataFrame
                

        RETURNS:
            Instance of the Decribe UI Implementation.

        RAISES:
            None.
        """
        
        _BaseUi.__init__(self, default_database="", connection=None)
        
        self._df = df
        self._categorical_summary_obj = None

        if self._connection.is_logged_in():
            self._create_ui()
            self._open_ui()

    def _on_tab_change(self):
        """
        DESCRIPTION:
            Calls each tab only after it has been clicked, that way the loading time for the tabs is reduced.

        PARAMETERS:
            None.  

        RETURNS:
            None.

        RAISES:
            None.
        """
        selected_index = self._describe_ui.selected_index
        current_tab = self._describe_ui.children[selected_index]
        if current_tab.value != "Evaluating...":
            return

        if self._describe_ui.titles[selected_index] == "Column statistics":
            df = self._df.describe()
            html_value = df.to_pandas().to_html(index=False)
        
        elif self._describe_ui.titles[selected_index] == "Column types":
            # Generate the HTML for the types tables.
            columns_types_html = """
                                      <table class="dataframe">
                                        <tr>
                                            <th>COLUMN NAME</th>
                                            <th>Python TYPE</th>
                                            <th>Teradata TYPE</th>
                                        </tr>
                                        {}
                                      </table>
                                        """
            rows_html = ["<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                col, types[0], types[1]) for col, types in self._df._column_types.items()]
            html_value = columns_types_html.format(chr(10).join(rows_html))
            
        elif self._describe_ui.titles[selected_index] == "Column summary":
            column_summary_df = ColumnSummary(data=self._df, target_columns=self._df.columns).result.to_pandas()
            column_summary = column_summary_df.to_html(index=False)
            html_value = column_summary

        elif self._describe_ui.titles[selected_index] == "Categorical summary":
            if self._categorical_summary_obj is None:
                self._categorical_summary_obj = CategoricalSummary(data=self._df, target_columns=self._categorical_columns)
            categorical_summary_df = self._categorical_summary_obj.result.to_pandas()
            categorical_summary = categorical_summary_df.to_html(index=False)
            html_value = categorical_summary
            
        elif self._describe_ui.titles[selected_index] == "Futile columns":
            # Futile Summary
            if self._categorical_summary_obj is None:
                self._categorical_summary_obj = CategoricalSummary(data=self._df, target_columns=self._categorical_columns)
            
            futile_summary_obj = GetFutileColumns(data=self._df, object=self._categorical_summary_obj, category_summary_column="ColumnName", threshold_value=0.7)
            futile_summary_df = futile_summary_obj.result.to_pandas()
            futile_summary = futile_summary_df.to_html(index=False)
            html_value = futile_summary

        elif self._describe_ui.titles[selected_index] == "Source query":
            qhtml = """<code>{}</code>""".format(self._df.show_query())
            html_value = qhtml

        # Remove default styling
        html_value = html_value.replace('<tr style="text-align: right;">', '<tr>')
        html_value = html_value.replace('class="dataframe"', 'style="width:100%; border-collapse: collapse; border:none;"')
        html_value = html_value.replace('border="1"', '')
        html_value = html_value.replace('<th>', '<th style="min-width:250px;border:none;text-align: left;">')
        html_value = html_value.replace('<td>', '<td style="border:none;">')
        html_value = html_value.replace('<tr>', '<tr style="min-width:250px;border-bottom: 1px solid black; border-bottom-color: #dcdcdc;">')
        
            
        current_tab.value = html_value


    def _create_ui(self):      
        """
        DESCRIPTION:
            Private function that creates the ipywidgets UI for Describe.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """         
        
        children = []
        titles = []

        # Shape
        shape_html = """<html>
                          <table style="border:none; width:100%; table-layout: fixed; border-collapse: collapse;">
                            <tr style="border-bottom: 1px solid black; border-bottom-color: #dcdcdc;">
                                <td style="border:none;"><b>Rows</b></td>
                                <td style="border:none;"><b>Columns</b></td>
                                <td style="border:none;"><b>Size</b></td>
                            </tr>
                            <tr style="border-bottom: 1px solid black; border-bottom-color: #dcdcdc;">
                                <td style="border:none;">{}</td>
                                <td style="border:none;">{}</td>
                                <td style="border:none;">{}</td>
                            </tr>
                          </table>
                       </html>""".format(
            str(self._df.shape[0]), str(self._df.shape[1]), str(self._df.size))

        shape_html = ipywidgets.HTML(value=shape_html)
        children.append(shape_html)
        titles.append("Shape and size")

        children.append(ipywidgets.HTML(value="Evaluating..."))
        titles.append("Column statistics")

        children.append(ipywidgets.HTML(value="Evaluating..."))
        titles.append("Column types")

        children.append(ipywidgets.HTML(value="Evaluating..."))
        titles.append("Column summary")

        self._categorical_columns = []
        for col, d_type in self._df._column_names_and_types:
            if d_type in ['str']:
                self._categorical_columns.append(col)

        # Categorical Summary
        if len(self._categorical_columns) != 0:
            
            children.append(ipywidgets.HTML(value="Evaluating..."))
            titles.append("Categorical summary")

            children.append(ipywidgets.HTML(value="Evaluating..."))
            titles.append("Futile columns")

        # Query
        children.append(ipywidgets.HTML(value="Evaluating..."))
        titles.append("Source query")
    

        self._describe_ui = ipywidgets.Tab()
        self._describe_ui.children = children
        self._describe_ui.titles = titles

        self._describe_ui.observe(lambda x : self._on_tab_change(), names='selected_index')

        
    def _open_ui(self):
        """
        DESCRIPTION:
            Private function that opens the teradatamlwidgets Describe UI. 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._show_display(self._describe_ui, False)

    def get_widget(self):
        """
        DESCRIPTION:
            Private function that returns the Describe UI so that it can be called in EDA. 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            Instance of Describe UI.
        """
        return self._describe_ui
        
        
    


