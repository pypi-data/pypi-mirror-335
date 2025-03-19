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
import json
import pprint
import sys
from teradatamlwidgets.teradata_analytic_lib.data_transformation import *
from teradatamlwidgets.teradata_analytic_lib.open_ended_query_generator import OpenEndedQueryGenerator
import ipywidgets as widgets
import IPython
from IPython.display import clear_output, HTML,Javascript, display
from teradatamlwidgets.teradata_analytic_lib.verifyTableColumns import *
from teradatamlwidgets.teradata_analytic_lib.valib_executor import *
from teradatamlwidgets.teradata_analytic_lib.vantage_version import *
import pandas as pd
from teradatamlwidgets.my_tags_input import *
from teradatamlwidgets.connection import *
from teradatamlwidgets.teradata_analytic_lib.uaf_json_converter import * 
import teradataml
from teradataml.analytics.json_parser.utils import func_type_json_version
from teradataml.common.constants import TeradataAnalyticFunctionInfo
from teradataml.common.utils import UtilFuncs
from teradataml.common.constants import TeradataConstants
from teradatamlwidgets.base_ui import _BaseUi
from teradataml import DataFrame
from teradataml.context.context import _get_current_databasename
import teradatamlwidgets.auto_ml.UiImpl as automl_ui_impl
from teradataml.common.constants import ValibConstants

class _UiImpl(_BaseUi):
    """
    Private class that implements teradatamlwidgets Interactive Analytic Function UI.
    """

    def __init__(
        self, 
        connection, 
        outputs, 
        function="", 
        inputs=None, 
        export_settings="", 
        default_database="",
        val_location="", 
        volatile=False,
        eda_mode=False):
        """
        DESCRIPTION:
            Constructor for private class that implements teradatamlwidgets Interactive Analytic Function UI.
        
        PARAMETERS:
            outputs: 
                Optional Argument. 
                Specifies the output name of the output table.

            connection: 
                Optional Argument. 
                Specifies the specific connection; could be teradataml based (i.e. TeradatamlConnection 
                instance) or another platform.

            function: 
                Optional Argument. 
                Specifies the name of the function, otherwise list of all functions will show.

            inputs: 
                Optional Argument. 
                Specifies the input tables desired allowing for selection in UI, otherwise user 
                must type in input table name or a teradataml DataFrame.

            export_settings: 
                Optional Argument. 
                Specifies the filename or JSON user where the UI parameters will be saved and loaded from. 
                This allows you to avoid having to retype the UI parameters the next time you run the cell.

            default_database: 
                Optional Argument. 
                Specifies the default database.

            val_location: 
                Optional Argument. 
                Specifies the VAL location.

            volatile: 
                Optional Argument. 
                Specifies whether table is volatile or not.

        RETURNS:
            Instance of the Private UI class.
        """

        # EDA Mode support
        self._eda_mode = eda_mode
        self._eda_widget_output = None
        widget_output = None
        if self._eda_mode:
            widget_output = widgets.Output()

        _BaseUi.__init__(self, default_database=default_database, connection=connection, val_location=val_location, widget_output=widget_output)
        

        # AutoML UI, not created until requested by user
        self._automl_ui = None
        
        if self._eda_mode:
            if outputs is None:
                outputs = []

        self._volatile = volatile
        self._table_widgets = {}
        
        ipywidgets_version = widgets.__version__.split(".")
        ipywidgets_version = int(ipywidgets_version[0])*100 + int(ipywidgets_version[1])*10 + int(ipywidgets_version[2])
        # Check ipywidgets version 804 and above that has Tag UI widget otherwise we have to create our own Tag UI
        _UiImpl._tag_widget_available = ipywidgets_version >= 804
        _UiImpl._TagsInput = MyTagsInput if not _UiImpl._tag_widget_available else widgets.TagsInput

        # If old version then it won't have combobox
        if not hasattr(widgets, "Combobox") or not _UiImpl._tag_widget_available:
            widgets.Combobox = widgets.Dropdown

        # Keep the input table names and database names so UI can display them
        self._input_table_names = []
        self._input_db_names = []
        self._input_dfs = {}
        self._input_tablename_to_query = {}
        self._update_input_table_names(inputs)

        # Output processing
        if outputs == None:
            outputs = []
        if len(outputs) == 0:
            new_table_name = UtilFuncs._generate_temp_table_name(table_type = TeradataConstants.TERADATA_TABLE)
            outputs.append(new_table_name)

        # Keep the output table names and database names so UI can display them
        self._output_table_names = []
        self._output_db_names = []
        for output in outputs:
            self._output_table_names.append(UtilFuncs._extract_table_name(output))
            self._output_db_names.append(UtilFuncs._extract_db_name(output))

        self._function = function
        self._connection = connection
        self._inputs = inputs
        self._outputs = outputs
        self._login_ui = None
        self._function_ui = None
        self._login_info = {}
        self._export_settings = export_settings
        self._eda_status_widget = None
        
        if self._connection.is_logged_in():
            self._login_info['default_db'] = default_database if default_database else _get_current_databasename()
            self._login_info['val_location'] = val_location if val_location else self._connection.get_connection_setting(inputs[0], 'val_location')
            self._create_ui()
            self._open_ui()
            
    def _show_dialog(self, html):
        """
        Private function that shows a HTML message in the cell with a close button.

        PARAMETERS:
            html:
                String with HTML tags.
                Types: str

        RAISES:
            None.
            
        RETURNS:
            None.
        """
        if not self._eda_mode:
            html = widgets.HTML(value=html)
            close_button = widgets.Button(description="Close")
            close_button.on_click(lambda x : self._show_display(self._function_ui, True))
            container = widgets.VBox([html, close_button])
            self._show_display(container, True)
        else:
            self.html.value = html
            self.html.layout.visibility = "visible"

    def _get_function_json_path(self, function_category, version):  
        """
        Private function that gets the file path for the function.

        PARAMETERS:
            function_category:
                The category of the function.
                Permitted values: "VAL", "SQLE", "UAF".
                Types: str

            version:
                The version number of Teradata.
                Types: str
        RAISES:
            None.
            
        RETURNS:
            Returns the path to the function JSON.
            Type: str
        """
        if function_category == "VAL":
           return os.path.join(self._folder, function_category) 
        if function_category == "SQLE" or function_category == "UAF":
           func_type = TeradataAnalyticFunctionInfo.FASTPATH if function_category == "SQLE" else TeradataAnalyticFunctionInfo.UAF
           directory = UtilFuncs._get_data_directory(dir_name="jsons", func_type=func_type)
           path = os.path.join(directory, version) 
           # Check if path exists
           if os.path.exists(path):
                return path
           else:
                # Path doesnt exist so maybe the version doesnt exist so lets try 17.20
                path = os.path.join(directory, "17.20")
                return path 

    def _update_input_table_names(self, inputs):
        """
        Private function that updates the input table names when a change is made, for example if the tab is moved, added or removed.

        PARAMETERS:
            inputs:
                The list of all input names.
                Types: lst
        RAISES:
            None.
            
        RETURNS:
            None.
        """
        # Update the table inputs
        self._inputs = inputs
        prior_input_table_names = self._input_table_names
        # Establish the input table and database names which are used in UI
        self._input_table_names = []
        self._input_db_names = []
        self._input_dfs = {}
        self._input_tablename_to_query = {}
        # Iterate over all new inputs
        input_index = 0
        for input in inputs:
            # If the input is a DataFrame then cache the columns to avoid 
            # recomputing them for the selection menu widgets
            columns = None
            df = None
            query = None
            if isinstance(input, DataFrame):
                columns = input.columns
                df = input
                input = df._table_name
                if input is None:
                    query = df.show_query()
            # Extract the table and database name
            try:
                table_name = UtilFuncs._extract_table_name(input)
                db_name = UtilFuncs._extract_db_name(input)
            except:
                table_name = "QUERY INPUT"
                if input_index > 0:
                    table_name += str(input_index)
                db_name = "{QUERY}"
            # Add to our lists
            self._input_table_names.append(table_name)
            self._input_db_names.append(db_name)
            full_name = '"{}"."{}"'.format(db_name, table_name)
            if df is not None:
                self._input_dfs[full_name] = df
            if query is not None:
                self._input_tablename_to_query[full_name] = query
            
            # If we have columns then cache to avoid recomputing
            if columns is not None:
                _UiImpl._table_columns_map[table_name] = columns

            input_index += 1

        # Update any created widgets that reference the tables
        for name in self._table_widgets:
            table_widget = self._table_widgets[name]
            # Find which index this table is from the prior input table names
            try:
                index = prior_input_table_names.index(table_widget.value)
            except ValueError:
                # If not in the prior inputs then just use the output from the last function
                index = 0
            table_widget.value = self._input_table_names[index]
        # Update AutoML its training table
        if self._automl_ui is not None:
            self._automl_ui._update_training_table(self._inputs[0], self._inputs[0])


    def _create_ui(self):
        """
        Private function that creates the ipywidgets UI for Analytic Functions.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """      
        self._version = get_vantage_version(  self._connection  )
        self._functions = []
        self._functionJsonFilePaths = {}
        self._function_types = {"SQLE" : [], "VAL" : [], "UAF" : []}
        self._ui_name_to_func_name = {}
        self._func_name_to_ui_name = {}
        self._ui_name_to_categories = {"AutoML" : 
                                       ["All", 
                                        "Model Scoring",  "Model Evaluation", 
                                        "Model Training", "Model Scoring/Prediction"]}
        self._function_categories = []
        self._search_json_directory("SQLE")
        self._search_json_directory("VAL")
        self._search_json_directory("UAF")
        self._functions.sort()
        self._functions = [""] + self._functions

        self._establish_val_function_categories()

        self._create_function_ui()

    def _open_ui(self):
        """
        Private function that opens the teradatamlwidgets Analytic Function UI. 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        if self._export_settings:
            # When UI first comes up load the user settings JSON if it was provided
            self._on_load()

    def _search_json_directory(self, function_category):
        """
        Private function that searches the JSON directories for each function
        and loads the JSON.

        PARAMETERS:
            function_category:
                The category of the function.
                Permitted values: "VAL", "SQLE", "UAF".
                Types: str
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        try:
            directory_path = self._get_function_json_path(function_category, self._version) 
            directory = os.listdir(directory_path)
            for filename in directory:
                json_file_path = os.path.join(directory_path, filename)
                if not os.path.isfile(json_file_path):
                    continue
                if not json_file_path.endswith(".json"):
                    continue
                name = filename.replace(".json", "")
                self._functions.append(name)
                self._functionJsonFilePaths[name] = json_file_path  
                
                self._establish_json_function_categories(function_category, name)    
        except Exception as e:
            with self._widget_output:
                print(e)

    def _on_keyword_changed(self):
        """
        Private function called when UI function category toggle is changes
        and then the functions available in UI will be filtered.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._function_toolbar.children = []
        self._current_function.close()
        self._current_function = widgets.Combobox(
            placeholder='Select a function ...',
            options=self._functions,
            ensure_option=True,
            disabled=False,
            layout = {'width': '80%'}
        )  
        # Clear the function
        self._current_function.value = ""
        self._tabs.children = []
        self._function_description.value = ""

        available_functions = []
        for ui_name in self._ui_name_to_categories:
            function_categories = self._ui_name_to_categories[ui_name]
            if self._function_categories_ui.value in function_categories:
                available_functions.append(ui_name)

        available_functions.sort()
        
        self._current_function.options = available_functions
        
        self._function_toolbar.children = [self._current_function, 
                                           self._function_categories_ui]
        self._current_function.observe(lambda x : self._on_current_function(), names='value')
        self._on_current_function()

    def _create_function_ui(self):
        """
        Private function creates the main UI for the current function.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._show_display(self._loading_bar, True)

        self._config_json = None
        if self._function_ui:
            self._function_ui.close()

        self._current_function = widgets.Combobox(
            placeholder='Select a function ...',
            options=self._functions,
            layout = {'width': '90%'},
            ensure_option=True,
            disabled=False
        )  
        self._current_function.observe(lambda x : self._on_current_function(), names='value')
        
        self._execute = widgets.Button(description="Execute", style = {'button_color' : '#4169E1', 'text_color' : 'white'}, tooltip='Execute function for output DataFrame')
        if not self._eda_mode:
            self._execute.on_click(lambda x : self._on_execute())
        
        self._query = widgets.Button(description="Query", style = {'button_color' : '#4169E1', 'text_color' : 'white'}, tooltip='See query details')
        self._query.on_click(lambda x : self._on_query())

        border_layout = widgets.Layout(border = 'solid #727d9c')
        self._reset = widgets.Button(description="Reset", style = {'button_color' : 'white', 'text_color' : '#4169E1'}, layout= border_layout, tooltip='Reset function to default values')
        self._reset.on_click(lambda x : self._on_reset())

        self._main_toolbar = [self._execute, self._query, self._reset]

        if self._eda_mode:
            self._add = widgets.Button(description = "Add to pipeline", style = {'button_color' : '#4169E1', 'text_color' : 'white'}, tooltip='Pipeline add new function')
            self._remove = widgets.Button(description = "Remove from pipeline", style = {'button_color' : '#4169E1', 'text_color' : 'white'}, tooltip='Pipeline remove function')
            self._move_later = widgets.Button(description = "Move >>", style = {'button_color' : '#4169E1', 'text_color' : 'white'}, tooltip='Move the function later in the pipeline')
            self._move_earlier = widgets.Button(description = "Move <<", style = {'button_color' : '#4169E1', 'text_color' : 'white'}, tooltip='Move the function earlier in the pipeline')
            self._main_toolbar.extend([self._add, self._remove, self._move_later, self._move_earlier])

        if not self._eda_mode and self._export_settings:
            self._load = widgets.Button(description="Load", style = {'button_color' : 'white', 'text_color' : '#4169E1'}, layout= border_layout, tooltip='Load in saved parameters')
            self._load.on_click(lambda x : self._on_load())
            self._main_toolbar.append(self._load)

            self._save = widgets.Button(description="Save", style = {'button_color' : 'white', 'text_color' : '#4169E1'}, layout= border_layout, tooltip='Save out values for parameters')
            self._save.on_click(lambda x : self._on_save())
            self._main_toolbar.append(self._save)

        if not self._eda_mode and self._connection.can_log_out():
            self._logout = widgets.Button(description="Log Out")
            self._logout.on_click(lambda x : self._on_logout())
            self._main_toolbar.append(self._logout)

        self._function_description  = widgets.HTML(value= '<style>p{word-wrap: break-word; max-height:200px}</style> <p></p>')
        self._line_divider = widgets.HTML("<hr>")

        self._tabs = widgets.Tab()
        self._tabs.children = []
        
        # Create Function Category UI
        self._function_categories.sort()
        self._function_categories = ["All", "SQLE", "VAL", "UAF"] + self._function_categories
        self._function_categories_ui = widgets.Dropdown(
            value="All",
            options=self._function_categories,
            disabled=False,
            layout = {'width': '30%'},
            description='Category:'
        )          
        self._function_categories_ui.observe(lambda x : self._on_keyword_changed(), names='value')
        
        self._function_toolbar = widgets.HBox([self._current_function, self._function_categories_ui])

        function_widgets = [
            self._function_toolbar,
            self._function_description, 
            self._tabs,
            widgets.HBox(self._main_toolbar),
            self._line_divider
            ]

        if self._eda_mode:
            self.html = widgets.HTML()
            # Hide it by Default
            self.html.layout.visibility = "hidden"
            function_widgets.append(self.html)

        self._function_ui = widgets.VBox(function_widgets)

        self._show_display(self._function_ui, True)
        self._on_keyword_changed()
        self._current_function.value = self._function
        # Disable buttons when no function is selected
        self._execute.disabled = self._current_function.value == ""
        self._query.disabled = self._current_function.value == ""
        self._reset.disabled = self._current_function.value == ""
        
    def _on_current_function(self):
        """
        Private function called when UI function menu is changed and UI will be updated to new function.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        if self._eda_status_widget is not None:
            self._eda_status_widget.value = "Loading function UI..."
        self._change_function()
        if self._eda_status_widget is not None:
            self._eda_status_widget.value = ""

    def _set_eda_message_widget(self, status_widget):
        """
        Private function called in EDA that allows us to set a message for users to see.

        PARAMETERS:
            status_widget:
                The message itself that we want to show to users.
                Type: str
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._eda_status_widget = status_widget

    def _change_function(self, file_settings_json = {}):
        """
        Private function called when current function UI should be refreshed.

        PARAMETERS:
            file_settings_json:
                Optional argument.
                The user defined JSON that is used for load and saving the UI parameters values.
                Type: dict of str and values
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        if self._eda_mode:
            self.html.layout.visibility = "hidden"

        self._show_display(self._loading_bar, True)

        # Disable buttons when no function is selected
        self._execute.disabled = self._current_function.value == ""
        self._query.disabled = self._current_function.value == ""
        self._reset.disabled = self._current_function.value == ""

        is_auto_ml = self._current_function.value == "AutoML"

        for item in self._main_toolbar:
            item.disabled = is_auto_ml
        # Show/Hide the AutoML widget
        if is_auto_ml:
            if self._eda_mode:
                # EDA mode and AutoML should show allow the pipeline buttons to be available
                for item in [self._add, self._remove, self._move_later, self._move_earlier]:
                    item.disabled = False
                self._export_settings["function_name"] = "AutoML"
                self._in_db_json['function_name'] = "AutoML"
            self._show_automl_widget()
            self._show_display(self._function_ui)
            return
        
        func_name = self._ui_name_to_func_name.get(self._current_function.value, '')
        if func_name == "":
            self._show_display(self._function_ui)
            return
        json_file_name = self._functionJsonFilePaths[func_name]
        with open(json_file_name, 'r') as file:
            data = file.read()

        self._in_db_json = json.loads(data)
             
        # If this is UAF then we need to convert to IN DB format
        if "function_type" not in self._in_db_json:
            self._in_db_json = uaf_to_indb(self._in_db_json)

        self._config_json = {}
        self._config_json['function'] = load_json(self._in_db_json, self._input_table_names)
        # For EDA setup the input tables appropriately
        if self._eda_mode:
            # Iterate over all required inputs
            required_inputs = self._config_json['function']['required_input']
            for index in range(len(required_inputs)):
                required_input = required_inputs[index]
                if len(required_inputs)>1 and index==0:
                    # Use the second input which is the original DataFrame EDA Source
                    required_input['value'] = self._input_table_names[1]
                else:   
                    # Otherwise use the input which is the output from the prior function 
                    required_input['value'] = self._input_table_names[0]

        # Load any user changes they saved last time
        if file_settings_json:
            self._load_user_json_settings(file_settings_json)

        self._config_json['function']['inputschemas'] = {}
        # Keep association of parameters that are columns to the tables they represent
        input_index = 0
        input_table_map = {}
        for input in self._config_json["function"]["required_input"]:
            # Making lowercase as JSONs sometimes have mistakes
            name = input['name'].lower()
            input_table_map[name] = input_index
            if len(input.get("alternateNames", []))>0:
                for alternative_name in input["alternateNames"]:
                    input_table_map[alternative_name.lower()] = input_index
            input["column_param_ui"] = []
        for arg in self._config_json["function"]["arguments"]:
            datatype = arg['datatype']
            if datatype == "COLUMNS":
                target_table = arg["targetTable"][0].lower()
                arg['target_input_index'] = input_table_map[target_table]
       

        self._function_description.value = '<style>p{max-width: 100%; overflow-y:scroll; max-height:150px;}</style> <p>'+self._in_db_json['long_description']+'</p>'

        self._param_widgets = {}
        self._table_widgets = {}
        required_ui = self._create_param_ui(required=True)
        optional_ui = self._create_param_ui(required=False)

        # Update the table and columns controls
        self._update_input_table_columns()

        self._tabs.children = [required_ui, optional_ui]
        self._tabs.set_title(index=0,title="Required")
        self._tabs.set_title(index=1,title="Optional")
        
        self._show_display(self._function_ui)

    def _update_input_table_columns(self):
        """
        Private function called when we need to update the columns of the input table, if the tabs have been changed.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        # Update the table and columns widgets
        for input in self._config_json["function"]["required_input"]:
            self._update_input_tables(input)
            self._update_input_columns(input)

    def _on_value_changed(self, change):
        """
        Private function called when UI representing function parameter is changed
        and we so can update the JSON to reflect the UI change.

        PARAMETERS:
            change:
                The parameter dict that has information of the JSON and UI that should be updated.
                Type: dict
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        input = change['owner'].json
        input['value'] = change['owner'].value

    def _on_table_changed(self, change):
        """
        Private function called when table UI is changed
        and we so can update the JSON to reflect the UI change.

        PARAMETERS:
            change:
                The parameter dict that has information of the JSON and UI that should be updated.
                Type: dict
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        table_name = change['owner'].value
        input = change['owner'].json
        input['value'] = table_name
        self._update_input_columns(input)

    def _on_data_partition_option_changed(self, change):
        """
        Private function called when data parition option UI is changed
        and we so can update the JSON to reflect the UI change.

        PARAMETERS:
            change:
                The parameter dict that has information of the JSON and UI that should be updated.
                Type: dict
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        input = change['owner'].json
        # Dictionary used to convert UI fiendly name to actual parition/hash name used in query
        # This is used when the user interface changes and we need to update the value of the change
        _uiname_to_databyname = {"None" : "None", "Partition": "PartitionByKey", "Hash" : "HashByKey", "Dimension" : "Dimension"}
        input['kind'] = _uiname_to_databyname[change['owner'].value]
        input['partion_hash_ui'].layout.display = "none" if input['kind'] == "None" else "inline"
    
    def _on_data_by_changed(self, change):
        """
        Private function called when "data parition by" UI is changed
        and we so can update the JSON to reflect the UI change.

        PARAMETERS:
            change:
                The parameter dict that has information of the JSON and UI that should be updated.
                Type: dict
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        value = change['owner'].value
        change['owner'].json['partitionAttributes'] = value
    
    def _on_order_by_changed(self, change):
        """
        Private function called when "data order by" UI is changed
        and we so can update the JSON to reflect the UI change.

        PARAMETERS:
            change:
                The parameter dict that has information of the JSON and UI that should be updated.
                Type: dict
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        columns = change['owner'].value
        column_direction = change['owner'].direction
        change['owner'].json['orderByColumn'] = columns
        change['owner'].json['orderByColumnDirection'] = column_direction

    def _update_input_tables(self, input):
        """
        Private function called when input table UI should be refreshed with options
        of which tables are selectable.
        
        PARAMETERS:
            input:
                The parameter dict that has information of the JSON and UI that is used for the refresh.
                Type: dict
        
        RAISES:
            None.

        RETURNS:
            None.
        """

        # Fix bug where if we change options then the value gets lost
        # So first we keep copy of current value
        original_value = input['table_ui'].value
        # Then we update options
        input['table_ui'].options = self._input_table_names
        # Then we reset back the table value
        try:
            input['table_ui'].value = original_value
        except:
            pass

    # Cache of the table's columns to avoid calling DataFrame over ana over again 
    # for thr same table which is slow
    _table_columns_map = {}

    def _update_columns(self, control, dataset_name):
        """
        Private function called to refresh the column UI pulldown with the columns
        that are permitted values be selected based on dataset.
        
        PARAMETERS:
            control:
                The column UI.
                Type: ipywidget

            dataset_name:
                The name of the DataFrame.
                Type: Str
        
        RAISES:
            None.

        RETURNS:
            None.
        """

        try:
            if dataset_name in _UiImpl._table_columns_map:
                columns = _UiImpl._table_columns_map[dataset_name]
            else:
                columns = self._connection.get_columns_of_dataset(dataset_name)
                _UiImpl._table_columns_map[dataset_name] = columns
        except:
            _UiImpl._table_columns_map[dataset_name] = []
            # No columns are available
            columns = []

        if hasattr(control, 'allowed_tags'):
            control.allowed_tags = columns.copy()
        if hasattr(control, 'set_allowed_tags'):
            control.set_allowed_tags(columns.copy())
        if hasattr(control, 'options'):
            # Fix bug where if we change options then the value gets lost
            # So first we keep copy of current value
            original_value = control.value
            # Then we update options
            control.options = columns.copy()
            # Then we reset back the table value
            try:
                control.value = original_value
            except:
                pass

    def _update_input_columns(self, input):
        """
        Private function called to refresh the Input column UI which will update
        the column UI and data partion UI.
        
        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """

        dataset_name = input.get('value','')
        if "data_by_ui" in input:
            self._update_columns(input['data_by_ui'], dataset_name)
        if "order_by_ui" in input:
            self._update_columns(input['order_by_ui'], dataset_name)
        # update associated parameters that represent this table
        for column_param_ui in input["column_param_ui"]:
            self._update_columns(column_param_ui, dataset_name)

    def _create_partition_hash_by_ui(self, input, input_items):
        """
        Private function that creates the parition / hash UI.
        
        PARAMETERS:
            input:
                The parameter dict that has information of the JSON and UI that is used for the refresh.
                Type: dict

            input_items:
                The list of ipywidgets that get created for the partition hash UI are appended to this list.
                Type: list ipywidgets

        RAISES:
            None.

        RETURNS:
            None.
        """

        options = ['None', 'Partition', 'Hash']
        if 'Dimension' in input['inputKindChoices']:
            options.append('Dimension')
        data_partition_option = widgets.Dropdown(description="Data Partition Option", options=options, style=dict(description_width='150px'), layout={'width': '90%'})
        data_partition_option.json = input

        # Dictionary used to convert parition/hash actual name used in query to UI fiendly name 
        # This is used when we create the parition UI
        _databyname_to_uiname = {"None" : "None", "PartitionByKey": "Partition", "HashByKey" : "Hash", "Dimension" : "Dimension"}

        data_partition_option.value = _databyname_to_uiname.get(input['kind'], "None")
        data_partition_option.observe(lambda x : self._on_data_partition_option_changed(x), names='value')
        
        partition_value = input['partitionAttributes']
        input['data_by_ui'] = MyTagsInput(value=partition_value, allow_duplicates=False, style=dict(description_width='150px'), layout={'width': '400px'})
        input['data_by_ui'].json = input
        input['data_by_ui'].observe(lambda x : self._on_data_by_changed(x), names='value')
        
        order_by_values = []
        direction_values = []
        for i in range(len(input['orderByColumn'])):
            direction = "ASC"
            if 'orderByColumnDirection' in input and i < len(input['orderByColumnDirection']):
                direction = input['orderByColumnDirection'][i]
            direction_values.append(direction)
            order_by_values.append(input['orderByColumn'][i])   
        input['order_by_ui'] = MyTagsInput(value=order_by_values, allow_duplicates=False, style=dict(description_width='150px'), layout={'width': '600px'}, has_direction=True, direction=direction_values)
        input['order_by_ui'].json = input
        input['order_by_ui'].observe(lambda x : self._on_order_by_changed(x), names='value')
        
        input['partion_hash_ui'] = widgets.VBox([widgets.Label("Data By"), input['data_by_ui'] , widgets.Label("Order By"), input['order_by_ui'] ])
        input['partion_hash_ui'].layout.display = "none" if input['kind'] == "None" else "inline"
        input_items.append(widgets.VBox([data_partition_option, widgets.HBox([widgets.Label("", layout={'width': '150px'}), input['partion_hash_ui'] ])]))
        
    def _set_uaf_visibility(self, input):
        """
        Private function that sets the visibility for the UAF UI controls based on if 
        it is Matrix, Series, GenSeries or ART.
        
        PARAMETERS:
            input:
                The parameter dict that has information of the JSON and UI that is used for the refresh.
                Type: dict

        RAISES:
            None.

        RETURNS:
            None.
        """

        input_uaf = input["uaf_ui"]
        uaf_type = input_uaf['uaf_type'].value

        # Setting display to None will show it without affecting the description width
        input_uaf['is_row_sequence'].layout.display = None if uaf_type!='ART' and uaf_type!='GENSERIES' and uaf_type!='' else "none"
        input_uaf['row_axis_name'].layout.display = None if uaf_type!='ART' and uaf_type!='GENSERIES' and uaf_type!='' else "none"
    
        input_uaf['is_col_sequence'].layout.display = None if uaf_type=='MATRIX' else "none"
        input_uaf['column_axis_name'].layout.display = None if uaf_type=='MATRIX' else "none"
    
        input_uaf['id_name'].layout.display = None if uaf_type!='ART' and uaf_type!='GENSERIES' and uaf_type!='' else "none"
        input_uaf['id_sequence'].layout.display = None if uaf_type!='GENSERIES' and uaf_type!='' else "none"

        input_uaf['payload_fields'].layout.display = None if uaf_type!='ART' and uaf_type!='GENSERIES' and uaf_type!='' else "none"
        input_uaf['payload_content'].layout.display = None if uaf_type!='ART' and uaf_type!='GENSERIES' and uaf_type!='' else "none"
        
        input_uaf['payload_start_value'].layout.display = None if uaf_type=='GENSERIES' else "none"
        input_uaf['payload_offset_value'].layout.display = None if uaf_type=='GENSERIES' else "none"
        input_uaf['payload_num_entries'].layout.display = None if uaf_type=='GENSERIES' else "none"
    
        input_uaf['layer'].layout.display = None if uaf_type!='GENSERIES' and uaf_type!='' else "none"

        input_uaf['time_duration'].layout.display = None if uaf_type=='SERIES' else "none"
        input_uaf['time_type'].layout.display = None if uaf_type=='SERIES' else "none"
        input_uaf['time_zero'].layout.display = None if uaf_type=='SERIES' else "none"
        input_uaf['seq_zero'].layout.display = None if uaf_type=='SERIES' else "none"

        input_uaf['where'].layout.display = None if uaf_type!='GENSERIES' and uaf_type!='' else "none"

    def _on_uaf_type_changed(self, change):
        """
        Private function called when the UI changes the UAF type
        and we so can update the JSON to reflect the UI change.

        PARAMETERS:
            change:
                The parameter dict that has information of the JSON and UI that should be updated.
                Type: dict
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        input = change['owner'].json
        input["uafType"] = change['owner'].value
        self._set_uaf_visibility(input)

    def _on_is_row_sequence_changed(self, change):
        """
        Private function called when the UAF "row sequence" UI is changed
        and we so can update the JSON to reflect the UI change.

        PARAMETERS:
            change:
                The parameter dict that has information of the JSON and UI that should be updated.
                Type: dict
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        input = change['owner'].json
        input["uaf"]['is_row_sequence'] = change['owner'].value
    
    def _on_uaf_property_changed(self, param_name, change, split = False):
        """
        Private function called when the any UAF parameter UI is changed
        and we so can update the JSON to reflect the UI change.

        PARAMETERS:
            change:
                The parameter dict that has information of the JSON and UI that should be updated.
                Type: dict

            split:
                Optional Argument
                Split the value into a list which is for UI elements that allow you 
                to enter a set of values.
                Default Value: False
                Type: Bool

        
        RAISES:
            None.

        RETURNS:
            None.
        """
        input = change['owner'].json
        input["uaf"][param_name] = change['owner'].value.split(" ") if split else change['owner'].value

    def _create_uaf_ui(self, input, input_items):
        """
        Private function that creates the UAF UI.
        
        PARAMETERS:
            input:
                The parameter dict that has information of the JSON and UI that is used for the refresh.
                Type: dict

            input_items:
                The list of ipywidgets that get created for the partition hash UI are appended to this list.
                Type: list ipywidgets

        RAISES:
            None.

        RETURNS:
            None.
        """

        items = []

        options = ['']
        if 'SERIES' in input['uaf']['requiredUafKind']:
            options.append('SERIES')
        if 'MATRIX' in input['uaf']['requiredUafKind']:
            options.append('MATRIX')
        if 'ART' in input['uaf']['requiredUafKind']:
            options.append('ART')
        if 'GENSERIES' in input['uaf']['requiredUafKind']:
            options.append('GENSERIES')
        
        input_uaf = {}
        input["uaf_ui"] = input_uaf
        input_uaf = input["uaf_ui"]

        #print('row_axis_name=', input['uaf']['row_axis_name'])
        
        param_name = 'uaf_type'
        input_uaf[param_name] = widgets.Dropdown(description="UAF Type", options=options, style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input.get('uafType', '')
        input_uaf[param_name].observe(lambda x : self._on_uaf_type_changed(x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'is_row_sequence'
        input_uaf[param_name] = widgets.Dropdown(description="Row", options=["TIMECODE", "SEQUENCE"], style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_is_row_sequence_changed(x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'row_axis_name'
        input_uaf[param_name] = widgets.Text(description="Row Axis Name", style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('row_axis_name', x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'is_col_sequence'
        input_uaf[param_name] = widgets.Dropdown(description="Column", options=["TIMECODE", "SEQUENCE"], style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('is_col_sequence', x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'column_axis_name'
        input_uaf[param_name] = widgets.Text(description="Column Axis Name", style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('column_axis_name', x), names='value')
        items.append(input_uaf[param_name])

        #items.append(widgets.Label("ID"))
        param_name = 'id_name'
        #value = input['uaf'][param_name]
        input_uaf[param_name] = widgets.Textarea(description= "ID", style=dict(description_width='150px'), layout={'width': '90%'})

        
        input_uaf[param_name].json = input
        input_uaf[param_name].value = " ".join(input['uaf'][param_name])
        #if type(value) == str:
        #    if value == "":
        #        value = []
        #    else:
        #        value = [value]
        #input_uaf[param_name].value = value
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('id_name', x, True), names='value')
        items.append(input_uaf[param_name])

        param_name = 'id_sequence'
        input_uaf[param_name] = widgets.Textarea(description="Sequence", style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = " ".join(input['uaf'][param_name])
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('id_sequence', x, True), names='value')
        items.append(input_uaf[param_name])

        param_name = 'payload_fields'
        input_uaf[param_name] = widgets.Textarea(description="Payload Fields", style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = " ".join(input['uaf'][param_name])
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('payload_fields', x, True), names='value')
        items.append(input_uaf[param_name])

        param_name = 'payload_content'
        options = ["", "REAL", "COMPLEX", "AMPL_PHASE", "AMPL_PHASE_RADIANS", "AMPL_PHASE_DEGREES", "MULTIVAR_REAL", "MULTIVAR_COMPLEX", "MULTIVAR_ANYTYPE", "MULTIVAR_AMPL_PHASE", "MULTIVAR_AMPL_PHASE_RADIANS", "MULTIVAR_AMPL_PHASE_DEGREES"]
        input_uaf[param_name] = widgets.Dropdown(description="Payload Content", options=options, style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('payload_content', x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'payload_start_value'
        input_uaf[param_name] = widgets.Text(description="Payload Start", style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('payload_start_value', x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'payload_offset_value'
        input_uaf[param_name] = widgets.Text(description="Payload Offset", style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('payload_offset_value', x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'payload_num_entries'
        input_uaf[param_name] = widgets.Text(description="Payload #Entries", style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('payload_num_entries', x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'layer'
        input_uaf[param_name] = widgets.Text(description="Layer", style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('layer', x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'time_duration'
        options = ["", "CAL_YEARS", "CAL_MONTHS", "CAL_DAYS", "WEEKS", "DAYS", "HOURS", "MINUTES", "SECONDS", "MILLISECONDS", "MICROSECONDS"]
        input_uaf[param_name] = widgets.Dropdown(description="Interval", options=options, style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('time_duration', x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'time_type'
        options = ["", "float", "integer"]
        input_uaf[param_name] = widgets.Dropdown(description="Interval Type", options=options, style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('time_type', x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'time_zero'
        options = ["", "DATE", "TIMESTAMP", "TIMESTAMP WITH TIME ZONE"]
        input_uaf[param_name] = widgets.Dropdown(description="Zero", options=options, style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('time_zero', x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'seq_zero'
        input_uaf[param_name] = widgets.Text(description="Sequence Zero", style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('seq_zero', x), names='value')
        items.append(input_uaf[param_name])

        param_name = 'where'
        input_uaf[param_name] = widgets.Text(description="WHERE", style=dict(description_width='150px'), layout={'width': '90%'})
        input_uaf[param_name].json = input
        input_uaf[param_name].value = input['uaf'][param_name]
        input_uaf[param_name].observe(lambda x : self._on_uaf_property_changed('where', x), names='value')
        items.append(input_uaf[param_name])

        # Hide show
        self._set_uaf_visibility(input)

        input_items.append(widgets.VBox(items))
        
    def _camel_case_split(s):
        """
        Private function that splits a string in camel case to words.
        E.g. "OptionType" -> "Option Type". 
        
        PARAMETERS:
            s:
                Input string in upper case cammel format.
                Type: str
        RAISES:
            None.

        RETURNS:
            Reformated string with spaces.
            Type: str.
        """
        # use map to add an underscore before each uppercase letter
        modified_string = list(map(lambda x: '_' + x if x.isupper() else x, s))
        # join the modified string and split it at the underscores
        split_string = ''.join(modified_string).split('_')
        # remove any empty strings from the list
        split_string = list(filter(lambda x: x != '', split_string))
        return " ".join(split_string)
    
    def _create_param_ui(self, required):
        """
        Private function that creates the function UI. 
        
        PARAMETERS:
            required:
                When True will create the required parameter UI otherwise the optional UI parameters.
                Type: bool
        RAISES:
            None.

        RETURNS:
            None.
        """
        items = []
        is_uaf = self._in_db_json.get("function_type", "") == "uaf"

        if required:
            self._volatile_ui = widgets.Checkbox(value=self._volatile, description='Volatile', tooltip='Click if you want the output table to be Volatile')
            items.append(self._volatile_ui)
        
        for input in self._config_json["function"]["required_input"]:
            isRequired = input.get('isRequired', False)
            name = input['name']
            value = input.get('value', '')
            description = input.get("description", "")
            
            if isRequired != required:
                continue
            
            input_items = []
            options=[str(value)]
            if self._eda_mode:
                # EDA mode allow any table to be enterered not just inputs given in constructor
                # As EDA allows functions to be moved around and thus have different input tables at different times
                options = []
            table = widgets.Combobox(description="Table", value=str(value), options=options, style=dict(description_width='150px'), layout={'width': '90%'})
            table.tooltip = description

            self._table_widgets[name] = table
            table.json = input
            table.observe(lambda x : self._on_table_changed(x), names='value')
            input_items.append(table)
            input['table_ui'] = table

            if len(input.get('inputKindChoices', []))>1:
                self._create_partition_hash_by_ui(input, input_items)
            elif input.get('uafType', ''):
                self._create_uaf_ui(input, input_items)

            # Add Group (Accordian) parent UI for these items
            accordion = widgets.Accordion()
            accordion.children = [widgets.VBox(input_items)]
            accordion.set_title(index=0,title=name)
            items.append(accordion)

        for arg in self._config_json["function"]["arguments"]:
            isRequired = arg.get('isRequired', False)
            if isRequired != required:
                continue
            name = arg['name']
            if not is_uaf:
                name = _UiImpl._camel_case_split(name)
            # TODO User datatype to create the appropriate widget
            datatype = arg['datatype']
            value = arg.get('value', arg.get('defaultValue', ''))
            description = arg.get("description", "")

            item = None
            if arg.get('allowsLists', False):
                if type(value) == str:
                    if value == '':
                        value = []
                if type(value) != list:
                        value = str(value).split(",")
                control = _UiImpl._TagsInput(value=value, tooltip=description, allow_duplicates=True, style=dict(description_width='150px'), layout={'width': '90%'})
                item = widgets.HBox([widgets.Label(name, layout=widgets.Layout(width="170px", display="flex", justify_content="flex-end")), control])
            elif datatype=="GROUPSTART" or datatype=="GROUPEND":
                # Ignore UAF Group start and End
                continue
            elif datatype=="COLUMNS":
                # Single COLUMN
                options=[str(value)]
                if self._eda_mode:
                    # EDA mode allow any table to be enterered not just inputs given in constructor
                    # As EDA allows functions to be moved around and thus have different input tables at different times
                    options = []
                control = widgets.Combobox(description=name, value=str(value), options=options, style=dict(description_width='150px'), layout={'width': '90%'})
            elif datatype=="BOOLEAN":
                if type(value) == str:
                    value = value.lower() == "true"
                control = widgets.Checkbox(description=name, value=value, style=dict(description_width='150px'))
            elif datatype=="DOUBLE PRECISION" and _UiImpl._isValidFloat(value):
                control = widgets.BoundedFloatText(description=name, value=value, style=dict(description_width='150px'))
                lowerBound = arg.get('lowerBound', '')
                if lowerBound:
                    control.min = float(lowerBound)
                upperBound = arg.get('upperBound', '')
                if upperBound:
                    control.max = float(upperBound)
                if lowerBound and upperBound:
                    if lowerBound.lower() == "infinity" or float(lowerBound) < -1000.0:
                        step = 0.001
                    elif upperBound.lower() == "infinity" or float(upperBound) > 1000.0:
                        step = 0.001
                    else:
                        step = (float(upperBound)-float(lowerBound))/10000.0;
                    if step<0.001:
                        step = 0.001
                    step = round(step, 4);
                    control.step = step
            elif datatype=="INTEGER" and _UiImpl._isValidInteger(value):
                control = widgets.BoundedFloatText(description=name, value=value, style=dict(description_width='150px'))
                lowerBound = arg.get('lowerBound', '')
                if lowerBound:
                    control.min = float(lowerBound)
                upperBound = arg.get('upperBound', '')
                if upperBound:
                    control.max = float(upperBound)
                control.step = 1
            elif datatype=="STRING" and "permittedValues" in arg and len(arg["permittedValues"])>0:
                control = widgets.Combobox(description=name, value=value, options=[str(value)], style=dict(description_width='150px'))
                if "" not in arg['permittedValues']:
                    arg['permittedValues'] = [""] + arg['permittedValues']
                control.options = arg['permittedValues']
                control.ensure_option = True
            else:
                # Just treat as string textfield
                control = widgets.Text(description=name, value=str(value), style=dict(description_width='150px'), layout={'width': '90%'})

            items.append(control if item==None else item)
            self._param_widgets[name] = control

            # Keep association of table and column parameters so when table is changes the columns can be updated
            if datatype == "COLUMNS":
                target_input_index = arg["target_input_index"]
                input = self._config_json["function"]["required_input"][target_input_index]
                input["column_param_ui"].append(control)

            # Show Tool Tip with description of parameter
            control.tooltip = description

            # Register callback when value changed of parameter widget
            control.json = arg
            control.observe(lambda x : self._on_value_changed(x), names='value')

        return widgets.VBox(items)
  
    def _on_execute(self):
        """
        Private function that is called when the execute button is pressed
        and will execute the query and show the resulting table in the cell.
        
        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        try:
            self._show_error_message("Executing the function...")
            self._execute_query()
        except Exception as e:
            self._show_error_message(e)

    def _on_query(self):
        """
        Private function that is called when the query button is pressed
        and will show the query in the cell.
        
        PARAMETERS:
            None.
            
        RAISES:
            None.

        RETURNS:
            None.
        """
        if not self._config_json:
            return
        try:
            dss_function = self._config_json.get('function', None)
            
            input_table_names, output_table_names, inputtables, inputschemas = self._update_input_tables_in_json()

            for output in self._output_table_names:
                dataset_name = output
                index = self._output_table_names.index(dataset_name)
                outputDatabaseName, outputTable = self._output_db_names[index], self._output_table_names[index]
            
            if dss_function and 'function_type' in dss_function and dss_function['function_type'] == "valib":
                json_contents = json.loads(dss_function["json_contents"])
                query = valib_execution(json_contents, dss_function, valib_query_wrapper=None)
            else:
                sql_generator = OpenEndedQueryGenerator(outputTable, self._config_json, outputDatabaseName=outputDatabaseName)
                query = sql_generator.create_query()
                query = self._update_volatile_query(query)
                for table_name in self._input_tablename_to_query:
                    query = query.replace(table_name, "({})".format(self._input_tablename_to_query[table_name]))
            if not query:
                return
            output_value = '''
                require(
                    ["base/js/dialog"], 
                    function(dialog) {
                        dialog.modal({
                            title: "Query",
                            body: $("<div></div>").append('__BODY__'),
                            buttons: {
                                "OK": {
                                }}
                        });
                    }
                );'''

            query = query.replace("'", '"')
            query = query.replace('\n', '<br>')
            query_string = "<b>QUERY:</b>"+ '<br>' + query
            output_value = output_value.replace("__BODY__", query_string)
            if _BaseUi.show_native_dialog:
                self._show_dialog(query_string)
                return
            else:
                display(Javascript(output_value))

        except Exception as e:
            self._show_error_message(e)

    def _update_volatile_query(self, query):
        """
        Private function that modified the query to create a volatile table.
        
        PARAMETERS:
            query:
                Original query that creates the table.
                Type: str
            
        RAISES:
            None.

        RETURNS:
            Modified query that creates a volatile table if the voltaile UI setting is enabled.
        """
        if self._volatile_ui.value:
            if "CREATE TABLE" in query:
                query = query.replace("CREATE TABLE", "CREATE VOLATILE TABLE")
                query = query.replace(";", " ON COMMIT PRESERVE ROWS;")
            else:
                query = query.replace("FUNCTION INTO", "FUNCTION INTO VOLATILE")
        return query

    def _update_input_tables_in_json(self):
        """
        Private function that updates the inout tables in the JSON passed to 
        the OpenEndedQueryGenerator which is used to execute the query. 
        
        PARAMETERS:
            None.
            
        RAISES:
            None.

        RETURNS:
            None.
        """
        input_table_names = []
        output_table_names = []
        inputtables = {}
        inputschemas = {}
        # Gather the inputs (get table and schema from datasets)
        required_inputs = self._config_json["function"]["required_input"]
        for required_input in required_inputs:
            dataset_name = ""
            if "value" in required_input:
                dataset_name = required_input["value"]
            if not self._eda_mode and dataset_name == "":
                if ("isRequired" in required_input) and required_input["isRequired"]:
                    raise RuntimeError("Input is missing - " + required_input["name"])
                # No input set by user, so keep empty
                input_table_names.append({})
                continue
            try:
                index = self._input_table_names.index(dataset_name)
            except:
                if self._eda_mode:
                    # EDA Mode we can add new datasets dynamically
                    self._input_table_names.append(UtilFuncs._extract_table_name(dataset_name))
                    self._input_db_names.append(UtilFuncs._extract_db_name(dataset_name))
                    index = self._input_table_names.index(dataset_name)

            schema, full_table_name = self._input_db_names[index], self._input_table_names[index]
            if not schema:
                schema = self._login_info['default_db']
            table_map = {}
            table_map["name"] = full_table_name
            table_map["table"] = full_table_name
            table_map["schema"] = schema
            inputtables[dataset_name] = full_table_name
            inputschemas[full_table_name] = schema
            input_table_names.append(table_map)
        self._config_json["function"]["input_table_names"] = input_table_names
        self._config_json["function"]["inputtables"] = inputtables
        self._config_json["function"]["inputschemas"] = inputschemas

        return input_table_names, output_table_names, inputtables, inputschemas
    
    def _execute_query(self):
        """
        Private function that executes the query by calling the OpenEndedQueryGenerator
        and then show the resulting table in the cell.
        
        PARAMETERS:
            None.
            
        RAISES:
            None.

        RETURNS:
            None.
        """
        if not self._config_json:
            raise Exception("No function selected")

        self._show_display(self._loading_bar, False)

        input_table_names, output_table_names, inputtables, inputschemas = self._update_input_tables_in_json()

        # Gather the outputs (get table and schema from datasets)
        for output in self._output_table_names:
            table_map = {}
            dataset_name = output
            index = self._output_table_names.index(dataset_name)
            outputDatabaseName, outputTable = self._output_db_names[index], self._output_table_names[index]
            if not outputDatabaseName:
                outputDatabaseName = self._login_info['default_db']
            table_map["name"] = outputTable
            table_map["table"] = outputTable
            table_map["schema"] = outputDatabaseName
            output_table_names.append(table_map)
        self._config_json["function"]["output_table_names"] = output_table_names

        # Main output is first schema and table
        outputDatabaseName = output_table_names[0]['schema']
        outputTable = output_table_names[0]["table"]

        # Gather connection properties
        autocommit = self._connection.get_connection_setting(self._inputs[0], "autocommitMode", True)
        pre_query = None
        post_query = None
        if not autocommit:
            pre_query = ["BEGIN TRANSACTION;"]
            post_query = ["END TRANSACTION;"]
            tmode = self._connection.get_connection_setting(self._inputs[0], "TMODE", "")
            if tmode == 'ANSI':
                pre_query = [";"]
                post_query = ["COMMIT WORK;"]

        # Setup the Executor
        self._connection.setup_executor(self._inputs[0], autocommit, pre_query, post_query)

        # Drop Outputs
        for output in output_table_names:
            drop_query = "DROP TABLE {outputTablename};".format(outputTablename=verifyQualifiedTableName(output['schema'], output['table']))
            try:
                self._connection.execute(drop_query)
            except:
                pass

        dss_function = self._config_json.get('function', None)
        if dss_function and 'function_type' in dss_function and dss_function['function_type'] == "valib":
            # Queries must be resolved for VAL
            input_table_index = 0
            for input_table in dss_function["input_table_names"]:
                table_name = input_table["table"]
                schema_name = input_table["schema"]
                full_name = '"{}"."{}"'.format(schema_name, table_name)
                if full_name in self._input_tablename_to_query:
                    input_df = self._input_dfs[full_name]
                    try:
                        shape = input_df.shape
                    except:
                        # Table has already been resolved
                        pass
                    input_table["table"] = UtilFuncs._extract_table_name(input_df._table_name)
                    input_table["schema"] = UtilFuncs._extract_db_name(input_df._table_name)
                input_table_index += 1

            # VALIB     
            dss_function["val_location"] = self._login_info['val_location']
            json_contents = json.loads(dss_function["json_contents"])
            valib_execution(json_contents, dss_function, dropIfExists=dss_function.get('dropIfExists', False), valib_query_wrapper = self._connection)
        else:        
            # SQLE/UAF    
            sql_generator = OpenEndedQueryGenerator(outputTable, self._config_json, verbose=True, outputDatabaseName=outputDatabaseName)
            query = sql_generator.create_query()
            query = self._update_volatile_query(query)
            for table_name in self._input_tablename_to_query:
                query = query.replace(table_name, "({})".format(self._input_tablename_to_query[table_name]))
            self._connection.execute(query)

        # Set schema
        index = 0
        for output in self._outputs:
            self._connection.set_schema_from_vantage(dataset=output, schema=output_table_names[0]['schema'], table=output_table_names[0]['table'])
            index += 1

        # Now shows results of execution
        self._show_execution_results()


    def _show_execution_results(self):
        """
        Private function called when we want to display the output dataframe after executing the function.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        # Display output dataframe
        df = self._get_pandas_dataframe().head()
        df = df.round(4)

        try:
            df = df.reset_index()
            indent = "\t"
            dindent = indent + indent
            html = '<html><table width:100% !important; style="table-layout:fixed; border-collapse:collapse !important; border: none;">\n<tr>\n'
            columns_html = "</th><th style='width:200px; text-align: left;border: none;'>".join(df.columns.to_list())
            html += "<th style='width:200px; text-align: left;border: none;'>{0}</th>\n".format(columns_html)
            html += "</tr>\n"
            for row in df.values.tolist():
                row_html = ["{0}<td style='width:200px;border: none;'>{1}</td>\n".format(dindent,
                                                       cell) for cell in row]
                html += "{1}<tr style='width:200px; border-bottom: 1px solid black; border-bottom-color: #dcdcdc;'>\n{0}{1}</tr>\n".format("".join(row_html), indent)
            html += "</table></html>"
            self._show_dialog(html)
            self.xxx = html
            return
        except:
            with self._widget_output:
                print(str(e))
        # Clear the progress bar
        self._show_display(self._function_ui)

    def _get_output_dataframe(self, output_index=0, output_name=""):
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
                Type: Str
                Default Value: ""
                
        EXCEPTIONS:
            None.

        RETURNS: 
            The output dataframe.
        """
        if self._current_function.value == "AutoML":
            return self._automl._get_output_dataframe()
        
        if output_name and output_name in self._outputs:
            # Work out the index based on the output name in JSON
            if "output_tables" in self._in_db_json:
                index = 0
                for output_table in self._in_db_json["output_tables"]:
                    if name == output_table["name"]:
                        output_index = index
                        break
                    index += 1
        schema, table_name = self._output_db_names[output_index], self._output_table_names[output_index]
        return self._connection.get_output_dataframe(verifyQualifiedTableName(schema, table_name), table_name)

    def _get_pandas_dataframe(self, output_index=0):
        """
        Access the output Pandas table used when displaying the output table in UI.

        PARAMETERS:
            output_index: 
                Optional Argument. 
                The index of the output to return, by default is set to 0, and will show the first output.
                Default Value: 0
                Type: int

        EXCEPTIONS:
            None.

        RETURNS: 
            The output dataframe.
            Type: teradataml.DataFrame
        """
        schema, table_name = self._output_db_names[output_index], self._output_table_names[output_index]
        df = self._connection.get_output_dataframe(verifyQualifiedTableName(schema, table_name), table_name)
        _UiImpl._table_columns_map[table_name] = df.columns
        return df.to_pandas()

    def _on_reset(self):
        """
        Private function that is called when the Reset button is pressed
        and will reset the parameters in UI back to the default values.
        
        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        if not self._config_json:
            return
        self._change_function()

    def _on_load(self):
        """
        Private function that is called when the Load button is pressed
        and will update the parameters in to the user specified JSON file passed in constructor.
        
        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        #if not self._config_json:
        #    return

        if isinstance(self._export_settings, dict):
            if len(self._export_settings) == 0:
                return
            dictionary = self._export_settings
        else:
            if not os.path.exists(self._export_settings):
                return
            with open(self._export_settings, 'r') as file:
                data = file.read()
            dictionary = json.loads(data)
        func_name = dictionary["function_name"]
        ui_name = self._func_name_to_ui_name.get(func_name, func_name)
        self._current_function.value = ui_name
        self._change_function(file_settings_json=dictionary)
        if func_name == "AutoML" and "arguments" in dictionary:
            self._get_automl_ui()._load(dictionary["arguments"])

    def _load_user_json_settings(self, dictionary):
        """
        Private function that is called when the updates the parameter UI based on 
        a dictionary of values loaded from the JSON the user specified in the constructor.
        
        PARAMETERS:
            dictionary:
                json of the values stored in the user specified JSON file.

        RAISES:
            None.

        RETURNS:
            None.
        """
        input_index = 0
        for input in self._config_json["function"]["required_input"]:
            input_values = dictionary["required_input"][input_index]
            input['value'] = input_values['value']
            if 'schema' in input_values:
                input['schema'] = input_values['schema']
            if 'partitionAttributes' in input_values:
                input['partitionAttributes'] = input_values['partitionAttributes']
            if 'orderByColumn' in input_values:
                input['orderByColumn'] = input_values['orderByColumn']
            if 'orderByColumnDirection' in input_values:
                input['orderByColumnDirection'] = input_values['orderByColumnDirection']
            if 'kind' in input_values:
                input['kind'] = input_values['kind']
            if 'uaf' in input_values:
                input['uaf'] = input_values['uaf']
            if 'uafType' in input_values:
                input['uafType'] = input_values['uafType']
            input_index += 1
        for arg in self._config_json["function"]["arguments"]:
            name = arg['name']
            if name in dictionary["arguments"]:
                arg['value'] = dictionary["arguments"][name]

    def _on_save(self):      
        """
        Private function that is called when the Save button is pressed
        and will save the parameters in UI to the user specified JSON file passed in constructor.
        
        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """

        # If AutoML then save its settings
        if self._current_function.value == "AutoML":
            if isinstance(self._export_settings, dict):
                dictionary = self._export_settings
            else:
                dictionary = {}
            dictionary["required_input"] = []
            dictionary["arguments"] = {}
            dictionary["function_name"] = self._in_db_json['function_name']
            self._get_automl_ui()._save(dictionary["arguments"])
            return

        elif not self._config_json:
            return

        if isinstance(self._export_settings, dict):
            dictionary = self._export_settings
        else:
            dictionary = {}
        dictionary["required_input"] = []
        dictionary["arguments"] = {}
        dictionary["function_name"] = self._in_db_json['function_name']
        for input in self._config_json["function"]["required_input"]:
            input_values = {}
            input_values['value'] = input['value']
            if 'schema' in input:
                input_values['schema'] = input['schema']
            if 'partitionAttributes' in input:
                input_values['partitionAttributes'] = input['partitionAttributes']
            if 'orderByColumn' in input:
                input_values['orderByColumn'] = input['orderByColumn']
            if 'orderByColumnDirection' in input:
                input_values['orderByColumnDirection'] = input['orderByColumnDirection']
            if 'kind' in input:
                input_values['kind'] = input['kind']
            if 'uaf' in input:
                input_values['uaf'] = input['uaf']
            if 'uafType' in input:
                input_values['uafType'] = input['uafType']
            dictionary["required_input"].append(input_values)
            
        for arg in self._config_json["function"]["arguments"]:
            name = arg['name']
            if "value" in arg:
                dictionary["arguments"][name] = arg['value']

        if not isinstance(self._export_settings, dict):
            json_object = json.dumps(dictionary, indent=4)
            with open(self._export_settings, "w") as outfile:
                outfile.write(json_object)

        output_value = """
            require(
                ["base/js/dialog"], 
                function(dialog) {
                    dialog.modal({
                        title: 'Confirmation',
                        body: 'Saved',
                        buttons: {
                            'OK': {
                            }}
                    });
                }
            );
        """
        # Linux has no popup dialog
        # Do not show the save dialog in the EDA mode
        if not self._eda_mode and _BaseUi.show_native_dialog:
            display(Javascript(output_value))

    def _isValidFloat(x):
        """
        Private function is a utility method to check if the value can be safely cast to a float.
        
        PARAMETERS:
            x:
                Type: str, int, float

        RAISES:
            None.

        RETURNS:
            None.
        """
        try:
            f = float(x)
            return True
        except:
            return False

    def _isValidInteger(x):
        """
        Private function is a utility method to check if the value can be safely cast to a int.
        
        PARAMETERS:
            x:
                Type: str, int, float

        RAISES:
            None.

        RETURNS:
            None.
        """
        try:
            i = int(x)
            return True
        except:
            return False

    def _establish_val_function_categories(self):
        """
        DESCRIPTION:
            Private function builds the VAL function categories based on VAL function map.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        # Gather the category names for VAL
        for detailed_category, functions in ValibConstants.CATEGORY_VAL_FUNCS_MAP.value.items():
            for function in functions:
                ui_name = _UiImpl._camel_case_split(function)
                ui_name = ui_name.replace("P C A", "Principal Component Analysis")
                ui_name = ui_name.replace("K S ", "KS") 
                #ui_name = ui_name.replace("Bin Code", "Binning")
                if ui_name in self._ui_name_to_categories:
                    self._ui_name_to_categories[ui_name].append(detailed_category)
                if detailed_category and detailed_category not in self._function_categories:
                    self._function_categories.append(detailed_category)

    def _establish_json_function_categories(self, function_category, name):
        """
        DESCRIPTION:
            Private function builds the function categories based on inDB JSON.

        PARAMETERS:
            function_category
                The category of the function.
                Permitted values: "VAL", "SQLE", "UAF".
                Types: str

            name 
                The function name.
                Types: str
        
        RAISES:
            None.

        RETURNS:
            None.
        """

        # Clean up name
        ui_name = self._cleanup_function_name(function_category, name)
        # Add "All" categories 
        self._ui_name_to_categories[ui_name] = ["All"]
        # Add function category (SQLE/UAF/VAL)
        self._ui_name_to_categories[ui_name].append(function_category)
        # And if the JSON has a category also add it 
        detailed_category = ""
        # Open the In-DB JSON 
        json_file_name = self._functionJsonFilePaths[name]
        with open(json_file_name, 'r') as file:
            data = file.read()
        self._in_db_json = json.loads(data)
        if "function_category" in self._in_db_json:
            detailed_category = self._in_db_json["function_category"]
        elif "FunctionCategory" in self._in_db_json:
            detailed_category = self._in_db_json["FunctionCategory"]
        if detailed_category and detailed_category not in self._function_categories:
            self._function_categories.append(detailed_category)
        if detailed_category:
            self._ui_name_to_categories[ui_name].append(detailed_category)

    def _cleanup_function_name(self, function_category, name):
        """
        DESCRIPTION:
            Private function returns nicer UI name for a function.
            E.g. removes "TD_" or "VAL" from name.

        PARAMETERS:
            function_category
                The category of the function.
                Permitted values: "VAL", "SQLE", "UAF".
                Types: str

            name 
                The function name.
                Types: str
        
        RAISES:
            None.

        RETURNS:
            The UI name.
        """

        # Clean up name
        if function_category == "VAL":
            ui_name = name.replace(" VAL", "")
        else:
            ui_name = name.replace("TD_", "")
        self._function_types[function_category].append(ui_name)

        # Create mapping from UI name to/from function name 
        self._ui_name_to_func_name[ui_name] = name
        self._func_name_to_ui_name[name] = ui_name

        return ui_name

    def _get_automl_ui(self):
        """
        DESCRIPTION:
            Private function that gets the AutoML widget so that it can be displayed as a function option and populate in the UI.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        if not self._automl_ui:
            self._automl_ui = automl_ui_impl._UiImpl(training_table = self._inputs[0], widget_output = self._widget_output, analytic_function_ui = self)
            self._automl_ui._task_ui.layout.display = 'none'
            if self._eda_mode:
                # EDA Mode the AutoML should output messages to the EDA's widget output
                self._automl_ui._widget_output = self._eda_widget_output
        return self._automl_ui

    def _show_automl_widget(self):
        """
        DESCRIPTION:
            Private function that shows ot hides the AutoML widget.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """

        automl_ui = self._get_automl_ui()
        self._function_description.value = '<style>p{max-width: 100%;}</style> <p>Automated Machine Learning (AutoML) represents a method for streamlining the entire process of machine learning pipeline in automated way. It encompasses various distinct phases of the machine learning pipeline</p>'
        self._tabs.children = automl_ui._tabs.children
        self._tabs.set_title(index=0,title="Initialize")
        self._tabs.set_title(index=1,title="Prediction")
        self._tabs.set_title(index=2,title="Load")
        self._tabs.set_title(index=3,title="Deploy")


