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
from collections import OrderedDict
from teradatamlwidgets.connection_teradataml import Connection
import ipywidgets
from IPython.display import clear_output, HTML,Javascript, display
from teradataml import get_connection, DataFrame
from teradataml.table_operators.Script import Script
from teradatasqlalchemy import *
from teradatamlwidgets.base_ui import _BaseUi
from teradataml.context.context import _get_current_databasename
from teradataml.dbutils.dbutils import set_session_param

class _UiImpl(_BaseUi):
    """
    Private class that implements teradatamlwidgets Interactive Script Ui.
    """

    def __init__(
                self, 
                search_path="", 
                default_database="", 
                connection = None,
                data=None,
                script_name=None,
                files_local_path=None,
                script_command=None,
                delimiter="\t",
                returns=None,
                auth=None,
                charset=None,
                quotechar=None,
                data_partition_column=None,
                data_hash_column=None,
                data_order_column=None,
                is_local_order=False,
                sort_ascending=True,
                nulls_first=True
                ):
        """
        Constructor for private class that implements teradatamlwidgets Interactive Script UI.

        PARAMETERS:

            search_path: 
                Required Argument. 
                Specifies the database search path for the SCRIPT execution.  
                Types: Str

            default_database: 
                Optional Argument. 
                Specifies the default database. 
                Types: str

            connection: 
                Optional Argument. 
                Specifies the specific connection; could be teradataml based (i.e. TeradatamlConnection instance) or another platform.

            data:
                Required Argument.
                Specifies a teradataml DataFrame containing the input data for the
                script.
                Types: teradataml DataFrame or str

            script_name:
                Optional Argument.
                Specifies the name of user script.
                User script should have at least permissions of mode 644.
                Types: str

            files_local_path:
                Optional Argument.
                Specifies the absolute local path where user script and all supporting.
                files like model files, input data file reside.
                Types: str

            script_command:
                Optional Argument.
                Specifies the command/script to run.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns.
                Default Value: "\t" (tab)
                Types: str of length 1 character
                Notes:
                    1) This argument cannot be same as "quotechar" argument.
                    2) This argument cannot be a newline character i.e., '\\n'.

            returns:
                Optional Argument.
                Specifies output column definition.
                Types: Dictionary specifying column name to teradatasqlalchemy type mapping.
                Default: None
                Note:
                    User can pass a dictionary (dict or OrderedDict) to the "returns" argument,
                    with the keys ordered to represent the order of the output columns.
                    Teradata recommends to use OrderedDict.

            auth:
                Optional Argument.
                Specifies an authorization to use when running the script.
                Types: str

            charset:
                Optional Argument.
                Specifies the character encoding for data.
                Permitted Values: utf-16, latin
                Types: str

            quotechar:
                Optional Argument.
                Specifies a character that forces all input and output of the script
                to be quoted using this specified character.
                Using this argument enables the Advanced SQL Engine to distinguish
                between NULL fields and empty strings. A string with length zero is
                quoted, while NULL fields are not.
                If this character is found in the data, it will be escaped by a second
                quote character.
                Types: character of length 1
                Notes:
                    1) This argument cannot be same as "delimiter" argument.
                    2) This argument cannot be a newline character i.e., '\\n'.

            data_partition_column:
                Optional Argument.
                Specifies Partition By columns for "data".
                Values to this argument can be provided as a list, if multiple
                columns are used for partition.
                Default Value: ANY
                Types: str OR list of Strings (str)
                Note:
                    1) "data_partition_column" cannot be specified along with
                       "data_hash_column".
                    2) "data_partition_column" cannot be specified along with
                       "is_local_order = True".

            data_hash_column:
                Optional Argument.
                Specifies the column to be used for hashing.
                The rows in the data are redistributed to AMPs based on the hash value of
                the column specified.
                The user-installed script file then runs once on each AMP.
                If there is no "data_partition_column", then the entire result set,
                delivered by the function, constitutes a single group or partition.
                Types: str
                Note:
                    "data_hash_column" cannot be specified along with
                    "data_partition_column", "is_local_order" and "data_order_column".
            
            data_order_column:
                Optional Argument.
                Specifies Order By columns for "data".
                Values to this argument can be provided as a list, if multiple
                columns are used for ordering. This argument is used with in both cases:
                "is_local_order = True" and "is_local_order = False".
                Types: str OR list of Strings (str)
                Note:
                    "data_order_column" cannot be specified along with "data_hash_column".


            is_local_order:
                Optional Argument.
                Specifies a boolean value to determine whether the input data is to be
                ordered locally or not. Order by specifies the order in which the
                values in a group, or partition, are sorted. Local Order By specifies
                orders qualified rows on each AMP in preparation to be input to a table
                function. This argument is ignored, if "data_order_column" is None. When
                set to True, data is ordered locally.
                Default Value: False
                Types: bool
                Note:
                    1) "is_local_order" cannot be specified along with "data_hash_column".
                    2) When "is_local_order" is set to True, "data_order_column" should be
                       specified, and the columns specified in "data_order_column" are
                       used for local ordering.

            sort_ascending:
                Optional Argument.
                Specifies a boolean value to determine if the result set is to be sorted
                on the "data_order_column" column in ascending or descending order.
                The sorting is ascending when this argument is set to True, and descending
                when set to False. This argument is ignored, if "data_order_column" is
                None.
                Default Value: True
                Types: bool

            nulls_first:
                Optional Argument.
                Specifies a boolean value to determine whether NULLS are listed first or
                last during ordering. This argument is ignored, if "data_order_column" is
                None. NULLS are listed first when this argument is set to True, and last
                when set to False.
                Default Value: True
                Types: bool

        RETURNS:
            Instance of the UI class.

        RAISES:
            None.

        EXAMPLE:
        from teradatamlwidgets.script.Ui import * 

        ui = Ui(search_path = "alice")

        """
        
        _BaseUi.__init__(self, default_database=default_database, connection=connection, search_path=search_path)
        
        self._script = None
        self._data=data
        self._script_name=script_name
        self._files_local_path=files_local_path
        self._script_command=script_command
        self._delimiter=delimiter
        self._returns=returns
        self._auth=auth
        self._charset=charset
        self._quotechar=quotechar
        self._data_partition_column=data_partition_column if data_partition_column else []
        self._data_hash_column=data_hash_column if data_hash_column else ""
        self._data_order_column=data_order_column if data_order_column else []
        self._is_local_order=is_local_order
        self._sort_ascending=sort_ascending
        self._nulls_first=nulls_first
        self._output_result = None
        
        self._login_info['search_path'] = search_path
            
        if self._connection.is_logged_in():
            self._create_ui()
            self._open_ui()

        
    def _on_add_out_column(self):
        """
        Private function that is called when user adds an output column.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._invalidate_script()
        out_column_name = self._output_column_name.value
        if not out_column_name:
            self._show_dialog(str(RuntimeError("Column name is not set")))
            return
        out_column_type = self._output_column_type.value
        if self._output_columns_ui.value:
            self._output_columns_ui.value = self._output_columns_ui.value + "\n"
        self._output_columns_ui.value = self._output_columns_ui.value + '"' + out_column_name + '"' + ":" + out_column_type
    
    def _on_remove_out_column(self):
        """
        Private function that is called when user removes an output column.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._invalidate_script()
        out_column_name = self._output_column_name.value
        if not out_column_name:
            self._show_dialog(str(RuntimeError("Column name is not set")))
            return
        value = self._output_columns_ui.value
        new_value = []
        found = False
        for line in value.split("\n"):
            if '"' + out_column_name + '"' in line:
                found = True
                continue
            new_value.append(line)
        if not found:
            self._show_dialog(str(RuntimeError("Column name is not found")))
            return
        self._output_columns_ui.value = "\n".join(new_value)

        
    def _create_ui(self):      
        """
        Private function that creates the ipywidgets UI for Script.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """   
        
        # Set Data Frames
        if not isinstance(self._data, DataFrame) and self._data:
            self._data = DataFrame(self._data)
        

        # Set Search Path for Script
        search_path = self._login_info['search_path']
        if not search_path:
            search_path = _get_current_databasename()
        set_session_param("searchuifdbpath", search_path)
        
        # Create Widget
        self._execute = ipywidgets.Button(description="Execute", style = {'button_color' : '#4169E1', 'text_color' : 'white'})
        self._execute.on_click(lambda x : self._on_execute())
        
        self._logout_button = ipywidgets.Button(
            description='Logout',
            disabled=False,
            tooltip='Log out of connection',
        )
        self._logout_button.on_click(lambda x : self._on_logout())
        
        self._buttons = ipywidgets.HBox([self._execute, self._logout_button])
        
        tabs = []
        param_widgets = []
        
        # Script
        self._script_command_ui = ipywidgets.Textarea(
                value=self._script_command,
                description='Command:',
                disabled=False,
                layout = {'width': '90%'},
            )
        self._script_command_ui.observe(lambda x : self._invalidate_script(), names='value')
        param_widgets.append(self._script_command_ui)
        
        
        self._script_name_ui = ipywidgets.Text(
                value=self._script_name,
                description='Name:',
                disabled=False,
                layout = {'width': '90%'},
            )    
        self._script_name_ui.observe(lambda x : self._invalidate_script(), names='value')
        param_widgets.append(self._script_name_ui)
        
        
        self._files_local_path_ui = ipywidgets.Text(
                value=self._files_local_path,
                description='Path:',
                disabled=False,
                layout = {'width': '90%'},
            )
        self._files_local_path_ui.observe(lambda x : self._invalidate_script(), names='value')
        param_widgets.append(self._files_local_path_ui)
        
        tabs.append(ipywidgets.VBox(param_widgets))
        param_widgets = []
        
        # Data
        columns = [""]
        if self._data:
            columns.extend(self._data.columns)
        self._data_partition_column_ui = ipywidgets.SelectMultiple(
                options = columns,
                value=self._data_partition_column,
                description='Partitions Columns:',
                disabled=False,
                style=dict(description_width='150px')
            )
        self._data_order_column_ui = ipywidgets.SelectMultiple(
                options = columns,
                value=self._data_order_column,
                description='Order Columns:',
                disabled=False,
                style=dict(description_width='150px')
            )
        
        self._data_hash_column_ui = ipywidgets.Dropdown(
                options = columns,
                value=self._data_hash_column,
                description='Hash Column:',
                disabled=False,
                style=dict(description_width='150px')
            )
        param_widgets.append(self._data_hash_column_ui)
        param_widgets.append(self._data_partition_column_ui)
        param_widgets.append(self._data_order_column_ui)
        
        
        tabs.append(ipywidgets.VBox(param_widgets))
        param_widgets = []
        
        # Output
        self._output_column_name = ipywidgets.Text(
                value='',
                description='Name:',
                disabled=False,
            )
        self._output_column_type = ipywidgets.Combobox(
                options = [
                    "BYTEINT", "SMALLINT", "INTEGER", "BIGINT", "DECIMAL", "FLOAT", "NUMBER",
                    "TIMESTAMP", "DATE", "TIME", "CHAR", "VARCHAR", "CLOB", "BYTE", 
                    "VARBYTE", "BLOB", "PERIOD_DATE", "PERIOD_TIME", "PERIOD_TIMESTAMP",
                    "INTERVAL_YEAR", "INTERVAL_YEAR_TO_MONTH", "INTERVAL_MONTH",
                    "INTERVAL_DAY", "INTERVAL_DAY_TO_HOUR", "INTERVAL_DAY_TO_MINUTE",
                    "INTERVAL_DAY_TO_SECOND", "INTERVAL_HOUR",
                    "INTERVAL_HOUR_TO_MINUTE", "INTERVAL_HOUR_TO_SECOND",
                    "INTERVAL_MINUTE", "INTERVAL_MINUTE_TO_SECOND", "INTERVAL_SECOND"
                ],
                value="",
                description='Type:',
                disabled=False,
                layout={'width': '250px'},
                style=dict(description_width='50px')
            )
        
        self._add_out_column = ipywidgets.Button(description="Add", style = {'button_color' : '#4169E1', 'text_color' : 'white'})
        self._remove_out_column = ipywidgets.Button(description="Remove", button_style='warning')
        
        self._add_out_column.on_click(lambda x : self._on_add_out_column())
        self._remove_out_column.on_click(lambda x : self._on_remove_out_column())
        param_widgets.append(ipywidgets.HBox([self._output_column_name, self._output_column_type, self._add_out_column, self._remove_out_column]))
        
        # Iterate over the returns to generate the text shown in the output columns UI
        output_columns = ""
        if self._returns:
            for column_name in self._returns:
                column_type = self._returns[column_name]
                column_type_str = column_type.__repr__()
                if output_columns != "":
                    output_columns += "\n"
                output_columns += '"' + column_name + '"' + ':' + column_type_str
        self._output_columns_ui = ipywidgets.Textarea(
                value=output_columns,
                disabled=True,
                layout = {'width': '95%', 'height' : '300px'},
            )
        param_widgets.append(self._output_columns_ui)
        
        tabs.append(ipywidgets.VBox(param_widgets))
        param_widgets = []
        
        # Files
        self._file_identifier = ipywidgets.Text(
                value='',
                description='ID:',
                disabled=False,
            )
        param_widgets.append(self._file_identifier)
        self._file_name = ipywidgets.Text(
                value='',
                description='Name:',
                disabled=False,
            )
        param_widgets.append(self._file_name)
        self._is_binary = ipywidgets.Checkbox(
            value=False,
            description='Binary',
            disabled=False,
        )
        param_widgets.append(self._is_binary)
        self._replace = ipywidgets.Checkbox(
            value=False,
            description='Replace',
            disabled=False,
        )
        param_widgets.append(self._replace)
        self._force = ipywidgets.Checkbox(
            value=False,
            description='Force',
            disabled=False,
        )
        param_widgets.append(self._force)
        self._install_file = ipywidgets.Button(description="Install", style = {'button_color' : '#4169E1', 'text_color' : 'white'})
        self._remove_file = ipywidgets.Button(description="Remove", button_style='warning')
        self._install_file.on_click(lambda x : self._on_install_file())
        self._remove_file.on_click(lambda x : self._on_remove_file())
        param_widgets.append(ipywidgets.HBox([self._install_file, self._remove_file]))
            
        tabs.append(ipywidgets.VBox(param_widgets))
        param_widgets = []
        
        # Details
        self._is_local_order_ui = ipywidgets.Checkbox(
            value=self._is_local_order,
            description='Local Order',
            disabled=False,
        )
        param_widgets.append(self._is_local_order_ui)
        self._sort_ascending_ui = ipywidgets.Checkbox(
            value=self._sort_ascending,
            description='Sort Ascending',
            disabled=False,
        )
        param_widgets.append(self._sort_ascending_ui)
        self._nulls_first_ui = ipywidgets.Checkbox(
            value=self._nulls_first,
            description='Nulls First',
            disabled=False,
        )
        param_widgets.append(self._nulls_first_ui)
        
        
        self._auth_ui = ipywidgets.Text(
                value=self._auth,
                description='Authority:',
                disabled=False,
            )
        self._auth_ui.observe(lambda x : self._invalidate_script(), names='value')
        param_widgets.append(self._auth_ui)
        
        self._delimiter_ui = ipywidgets.Text(
                value=self._delimiter,
                description='Delimiter:',
                disabled=False,
            )       
        self._delimiter_ui.observe(lambda x : self._invalidate_script(), names='value')
        param_widgets.append(self._delimiter_ui)
        
        self._quotechar_ui = ipywidgets.Text(
                value=self._quotechar,
                description='Quote:',
                disabled=False,
            )
        self._quotechar_ui.observe(lambda x : self._invalidate_script(), names='value')
        param_widgets.append(self._quotechar_ui)
        
        self._charset_ui = ipywidgets.Dropdown(
                options = ['', 'utf-16', 'latin'],
                value=self._charset,
                description='Char Set:',
                disabled=False
            )
        param_widgets.append(self._charset_ui)
        self._charset_ui.observe(lambda x : self._invalidate_script(), names='value')
        
        
        
        tabs.append(ipywidgets.VBox(param_widgets))
        param_widgets = []
              
        self._tabs = ipywidgets.Tab()
        self._tabs.children = tabs
        self._tabs.set_title(index=0,title="Script")
        self._tabs.set_title(index=1,title="Data")
        self._tabs.set_title(index=2,title="Output")
        self._tabs.set_title(index=3,title="Files")
        self._tabs.set_title(index=4,title="Details")
        
        
        self._main_ui = ipywidgets.VBox([self._buttons, self._tabs])

    def _invalidate_script(self):
        """
        Private function that invalidates the teradataml table operator Script instance.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """   
        self._script = None
        
    def _get_script(self):
        """
        Private function that invalidates the teradataml table operator Script instance.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            Type: teradataml.table_operators.Script
        """   
        kwargs = {}
        if self._data:
            kwargs["data"] = self._data
        kwargs["data_partition_column"] = list(self._data_partition_column_ui.value)
        kwargs["data_hash_column"] = self._data_hash_column_ui.value
        kwargs["data_order_column"] = list(self._data_order_column_ui.value)
        kwargs["is_local_order"] = self._is_local_order_ui.value
        kwargs["sort_ascending"] = self._sort_ascending_ui.value
        kwargs["nulls_first"] = self._nulls_first_ui.value
        
        # Data Parition Column should not be empty list
        if len(kwargs["data_partition_column"])==0:
            del kwargs["data_partition_column"]
        # Data Order Column should not be empty list
        if len(kwargs["data_order_column"])==0:
            del kwargs["data_order_column"]
        # Data Hash Column should not be emptry string
        if kwargs["data_hash_column"]=="":
            del kwargs["data_hash_column"]
        
        if self._script != None and self._data:
            self._script.set_data(**kwargs)
            return self._script
        
        if self._script_name_ui.value:
            kwargs["script_name"] = self._script_name_ui.value
        if self._files_local_path_ui.value:
            kwargs["files_local_path"] = self._files_local_path_ui.value
        kwargs["script_command"] = self._script_command_ui.value
        kwargs["delimiter"] = self._delimiter_ui.value
        kwargs["auth"] = self._auth_ui.value
        # auth should not be empty string
        if kwargs["auth"]=="":
            del kwargs["auth"]
        kwargs["charset"] = self._charset_ui.value
        # charset should not be empty string
        if kwargs["charset"]=="":
            del kwargs["charset"]
        kwargs["quotechar"] = self._quotechar_ui.value
        # quotechar should not be empty string
        if kwargs["quotechar"]=="":
            del kwargs["quotechar"]
        
        returns = OrderedDict({})
        lines = self._output_columns_ui.value.split("\n")
        for line in lines:
            if ":" not in line:
                continue
            column_name = line.split(":")[0].strip('"')
            column_type = line.split(":")[1]
            if "(" not in column_type:
                column_type += "()"
            returns[column_name] = eval(column_type)
        kwargs["returns"] = returns
        
        self._script = Script(**kwargs)
        return self._script
    
    def _on_install_file(self):
        """
        Private function that is called when the user installs a new file.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._widget_output.clear_output(wait=True)
        with self._widget_output:
            try:
                self._show_display(self._loading_bar)
                script = self._get_script()
                script.install_file(file_identifier=self._file_identifier.value, 
                                    file_name=self._file_name.value, 
                                    is_binary=self._is_binary.value, 
                                    replace=self._replace.value, 
                                    force_replace=self._force.value)
                self._show_dialog("File installed in Teradata Vantage Enterprise.")
            except Exception as e:
                self._show_error_message(e)          
        
    def _on_remove_file(self):
        """
        Private function that is called when the user removes a file.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._widget_output.clear_output(wait=True)
        with self._widget_output:
            try:
                self._show_display(self._loading_bar)
                script = self._get_script()
                script.remove_file(file_identifier=self._file_identifier.value, 
                                    force_remove=self._force.value)
                self._show_dialog("File removed from Teradata Vantage Enterprise.") 
            except Exception as e:
                self._show_error_message(e)
                
                
    def _on_execute(self):
        """
        Private function that is called when Execute button is pressed
        and will execute the script and show the output table in cell.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._widget_output.clear_output(wait=True)
        with self._widget_output:
            try:
                self._show_display(self._loading_bar)
                script = self._get_script()
                self._output_result = script.execute_script(output_style='TABLE')
                df = self._output_result.head().to_pandas()
                try:
                    markup = df.to_html().replace("\n", ' ')
                    self._show_dialog(markup)
                    return
                except Exception as e:
                    self._open_ui()
            except Exception as e:
                self._show_error_message(e)          
        
    def _open_ui(self):
        """
        Private function that opens the teradatamlwidgets Script Ui. 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._show_display(self._main_ui, True)
        
        

    def _get_output_dataframe(self):
        """
        DESCRIPTION:
            Function returns the Script dataframe output generated.

        PARAMETERS:
            None.

        RETURNS:
            teradataml.DataFrame 
        """
        return self._output_result

