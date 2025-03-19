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
from teradatamlwidgets.connection_teradataml import Connection
import ipywidgets
from IPython.display import clear_output, HTML,Javascript, display
import teradataml
from teradataml import get_connection, DataFrame
from teradataml import save_byom, retrieve_byom, load_example_data
from teradataml import configure, display_analytic_functions, execute_sql
from teradataml import DataRobotPredict, DataikuPredict, H2OPredict, ONNXPredict, PMMLPredict
from teradataml.analytics.json_parser.utils import func_type_json_version
from teradataml.common.constants import TeradataAnalyticFunctionInfo
from teradataml.common.utils import UtilFuncs
from teradataml.common.constants import TeradataConstants
from teradatamlwidgets.base_ui import _BaseUi
from teradataml.context.context import _get_current_databasename

class _UiImpl(_BaseUi):
    """
    Private class that implements teradatamlwidgets Interactive BYOM UI.
    """

    def __init__(
        self, 
        function = "DataRobotPredict", 
        byom_location = "", 
        data="", 
        model_id="", 
        model_table="", 
        default_database="", 
        connection = None):
        """
        DESCRIPTION:
            Constructor for private class that implements teradatamlwidgets Interactive BYOM UI.

        PARAMETERS:
            function: 
                Optional Argument. 
                Specifies the name of the function. 
                Default Value: "DataRobotPredict"
                Permitted Values: "DataRobotPredict", "H2OPredict", "DataikuPredict", ONNXPredict", "PMMLPredict"
                Types: str

            byom_location: 
                Optional Argument. 
                Specifies the BYOM location. 
                Types: str

            data: 
                Required Argument. 
                Specifies the input teradataml DataFrame that contains the data to be scored. 
                Types: Str or teradataml DataFrame

            model_table: 
                Optional Argument. 
                Specifies the name of the table to retrieve external model from. 
                Types: str

            model_id: 
                Optional Argument. 
                Specifies the unique model identifier of the model to be retrieved. 
                Types: str

            connection: 
                Optional Argument. 
                Specifies the specific connection; the specific connection. It can accept either 
                connection created using teradataml or another platform.

            default_database: 
                Optional Argument. 
                Specifies the default database. 
                Types: str

        RETURNS:
            Instance of the Private UI class.

        RAISES:
            None.
        """

        _BaseUi.__init__(self, connection=connection, default_database=default_database)
        

        # define a dictionary with names, so if tdml adds a similar function again
        # then we will just need to change only the dictionary
        self._function_dict = {}
        self._function_dict["DataRobotPredict"] = DataRobotPredict
        self._function_dict["DataikuPredict"] = DataikuPredict
        self._function_dict["H2OPredict"] = H2OPredict
        self._function_dict["ONNXPredict"] = ONNXPredict
        self._function_dict["PMMLPredict"] = PMMLPredict

        self._init_jsons()
        self._byom_location = byom_location
        self._data = data
        # Get the table name which is shown in the UI
        if isinstance(self._data, DataFrame):
            self._table_name = self._data._table_name
        else:
            self._table_name = self._data

        self._model_id = model_id
        self._model_table = model_table

        self._current_function = function
        
        self._login_info['username'] = ""
        self._login_info['password'] = ""
        if self._connection.is_logged_in():
            self._login_info['default_db'] = default_database if default_database else _get_current_databasename()
            self._login_info['val_location'] = "VAL"
            self._create_ui()
            self._open_ui()
            
    def _init_jsons(self):
        """
        Private function that loads the BYOM JSONs from teradataml

        PARAMETERS:
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._json_dict = {}
        directory_path = UtilFuncs._get_data_directory(
            dir_name="jsons", 
            func_type=TeradataAnalyticFunctionInfo.BYOM)
        for filename in os.listdir(directory_path):
            json_file_name = os.path.join(directory_path, filename)
            if not json_file_name.endswith(".json"):
                continue
            with open(json_file_name, 'r') as file:
                    data = file.read()
            in_db_json = json.loads(data)
            self._json_dict[in_db_json["function_name"]] = in_db_json   
    
    def _on_byom_install_location_changed(self):
        """
        Private function that sets the byom location to the correct value.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._byom_location = self._byom_install_location.value

    def _create_ui(self):      
        """
        Private function that creates the ipywidgets UI for BYOM Scoring.

        PARAMETERS:
        
        RAISES:
            None.

        RETURNS:
            None.
        """      
        self._byom_install_location = ipywidgets.Text(
            value=self._byom_location,
            placeholder='Type BYOM install location.',
            description='BYOM Install:',
            layout={'width': '600px'},
            disabled=False   
        )
        self._byom_install_location.observe(
            lambda x : self._on_byom_install_location_changed(), 
            names='value')

        param_widgets = []
        in_db_json = self._json_dict[self._current_function]
        self._params = {}
        # Iterate over input tables
        for input_table in in_db_json["input_tables"]: 
            param_name = input_table["name"]
            param_description = input_table["description"]
            param_datatype = input_table["datatype"]

            if param_name == "ModelTable":
                param_widget = ipywidgets.Text(
                    value=self._model_id,
                    placeholder='Type the model id to be used for scoring.',
                    description="ModelID",
                    layout={'width': '600px'},
                    style=dict(description_width='150px'), 
                    disabled=False   
                )
                param_widgets.append(param_widget)
                self._params["ModelID"] = {"datatype" : param_datatype, "widget" : param_widget}

            param_widget = ipywidgets.Text(
                    value=self._table_name if param_name=="InputTable" else self._model_table,
                    placeholder=param_description,
                    description=param_name,
                    layout={'width': '600px'},
                    style=dict(description_width='150px'), 
                    disabled=False   
            )
            param_widgets.append(param_widget)
            self._params[param_name] = {"datatype" : param_datatype, "widget" : param_widget}

            if param_name == "InputTable":
                # Register callback so we can update the column parameters
                param_widget.observe(
                    lambda x : self._on_inputtable_changed(x.owner.value), 
                    names='value')

        # Iterate over the arguments
        for argument_clause in in_db_json["argument_clauses"]: 
            param_name = argument_clause["name"]
            param_description = argument_clause["description"]
            param_datatype = argument_clause["datatype"]
            if param_datatype == "COLUMNS":
                param_widget = ipywidgets.SelectMultiple(
                    options=[''],
                    value=[''],
                    description=param_name,
                    tooltip = param_description,
                    disabled=False,
                    style=dict(description_width='150px'), 
                )
                param_widgets.append(param_widget)
                self._params[param_name] = {"datatype" : param_datatype, "widget" : param_widget}

            elif param_datatype == "BOOLEAN":
                param_default = argument_clause.get("defaultValue", False)
                param_widget = ipywidgets.Checkbox(
                    value=param_default,
                    description=param_name,
                    tooltip = param_description,
                    disabled=False,
                    layout={'width': '400px'},
                    indent=True
                )
                param_widgets.append(param_widget)
                self._params[param_name] = {"datatype" : param_datatype, "widget" : param_widget}

            elif "permittedValues" in argument_clause:
                param_default = argument_clause.get("defaultValue", "")
                param_widget = ipywidgets.Dropdown(
                    options= [''] + argument_clause["permittedValues"],
                    value=param_default,
                    description=param_name,
                    tooltip = param_description,
                    style=dict(description_width='150px'), 
                    disabled=False,
                )
                param_widgets.append(param_widget)
                self._params[param_name] = {"datatype" : param_datatype, "widget" : param_widget}
            elif argument_clause.get("allowsLists", False):
                # For allows list true then we use a textarea (multiple lines)
                param_default = argument_clause.get("defaultValue", "")
                param_widget = ipywidgets.Textarea(
                    value=param_default,
                    description=param_name,
                    tooltip = param_description,
                    style=dict(description_width='150px'), 
                    disabled=False,
                )
                param_widgets.append(param_widget)
                self._params[param_name] = {"datatype" : param_datatype, "widget" : param_widget}                
            else:
                # Anything else use a text widget
                param_default = argument_clause.get("defaultValue", "")
                param_widget = ipywidgets.Text(
                    value=param_default,
                    description=param_name,
                    tooltip = param_description,
                    style=dict(description_width='150px'), 
                    disabled=False,
                )
                param_widgets.append(param_widget)
                self._params[param_name] = {"datatype" : param_datatype, "widget" : param_widget}                

        
        
        self._execute = ipywidgets.Button(description="Execute", style = {'button_color' : '#4169E1', 'text_color' : 'white'})
        self._execute.on_click(lambda x : self._on_execute(show_query=False))
        
        self._show_query = ipywidgets.Button(description="Show Query")
        self._show_query.on_click(lambda x : self._on_execute(show_query=True))
        
        self._logout_button = ipywidgets.Button(
            description='Logout',
            disabled=False,
            tooltip='Log out of connection',
        )
        self._logout_button.on_click(lambda x : self._on_logout())


        self._functions = ipywidgets.Dropdown(
            options=list(self._json_dict.keys()),
            value=self._current_function,
            description='Function:',
            disabled=False,
        )
        self._functions.observe(lambda x : self._on_functions_changed(), names='value')


        self._buttons = ipywidgets.HBox([self._functions, self._execute, self._show_query, self._logout_button])


        self._function_ui = ipywidgets.VBox([self._buttons, self._byom_install_location] + param_widgets )
            
    def _open_ui(self):
        """
        Private function that opens the teradatamlwidgets BYOM UI 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._show_display(self._function_ui, True)
        # Update Input Table
        if self._params["InputTable"]["widget"].value:
            self._on_inputtable_changed(self._params["InputTable"]["widget"].value)

    def _on_functions_changed(self):
        """
        Private function that updates the UI when the function name is changed.

        PARAMETERS:
            widget:

        RAISES:
            None.
            
        RETURNS:
            None.
        """

        if self._current_function == self._functions.value:
            return
        self._current_function = self._functions.value

        self._create_function_ui()
        self._open_ui()

    def _change_case(self, str):
        """
        Private function that converts Upper case Cammel to slug format
        E.g. ModelType -> model_type

        PARAMETERS:
            str:
                The input string in upper case cammel
                Type: str

        RAISES:
            None.
            
        RETURN:
            The result is in lower case slug format
            Type: str
        """
        res = [str[0].lower()]
        for c in str[1:]:
            if c in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
                res.append('_')
                res.append(c.lower())
            else:
                res.append(c)
         
        return ''.join(res)

    def _on_execute(self, show_query = False):
        """
        Private function that is called when Execute or Show Query is clicked. It calls the BYOM function
        And then shows the ouput dataframe or query in the cell.

        PARAMETERS:
            show_query:
                Optional Argument
                If True will show the query otherwise shows the output dataframe
                Default Value: False
                Type: Bool

        RAISES:
            None.
            
        RETURN:
            None.
        """

        # Unique properties - these are added as kwargs to avoid having to hard code
        # meaning if new properties are added to the JSONs then they will show up in UI 
        # but ALSO get passed into the BYOM function
        model_table = self._params["ModelTable"]["widget"].value
        model_id = self._params["ModelID"]["widget"].value
        if not model_table or not model_id:
            self._show_dialog('<h2 style="color:red;">You need to specify the modeldata</h2>')
            return
        if not self._byom_location:
            self._show_dialog('<h2 style="color:red;">You need to specify the BYOM Install</h2>')
            return
        
        self._show_display(self._loading_bar, False)

        try:

            configure.byom_install_location = self._byom_location
            # Common Properties
            common_properties = ["InputTable", "Accumulate", "ModelOutputFields", 
            "OverwriteCachedModel", "ModelID", "ModelTable"]
            modeldata = retrieve_byom(model_id, table_name=model_table)
            newdata = DataFrame(self._params["InputTable"]["widget"].value)
            accumulate = list(self._params["Accumulate"]["widget"].value)
            model_output_fields = self._params["ModelOutputFields"]["widget"].value.split("\n") if self._params["ModelOutputFields"]["widget"].value else None
            overwrite_cached_models=self._params["OverwriteCachedModel"]["widget"].value

            # Unique properties - these are added as kwargs to avoid having to hard code
            # meaning if new properties are added to the JSONs then they will show up in UI 
            # but ALSO get passed into the BYOM function
            kawrgs = {}
            for param_name in self._params:
                if param_name in common_properties:
                    continue
                # Remap the names from JSON parameter names to actual names used in teradataml code
                function_param_name = self._change_case(param_name)
                kawrgs[function_param_name] = self._params[param_name]["widget"].value

            kawrgs["newdata"]=newdata
            kawrgs["modeldata"]=modeldata
            kawrgs["accumulate"]=accumulate
            kawrgs["model_output_fields"]=model_output_fields
            kawrgs["overwrite_cached_models"]=overwrite_cached_models

            # Get the function in the dictionary corresponding to current function
            byom_function = self._function_dict[self._current_function]
            # Call the function to get predicted result
            predict_output = byom_function(**kawrgs)

            # Get the output dataframe from prediction output
            self._output_dataframe = predict_output.result
            # Show dialog of head of output dataframe table            
            if show_query:
                markup = predict_output.show_query()
                markup = markup.replace("\n", '<br>')
                markup = '<h5>' + markup + '</h5>'
            else:
                markup = self._output_dataframe.to_pandas().head().to_html().replace("\n", ' ')
            self._show_dialog(markup)
        except Exception as e:
            self._show_dialog(str(e))

    def _on_inputtable_changed(self, value):
        """
        Private function that updates the parameters that are COLUMNS types when input table changes.

        PARAMETERS:
            value: 
                The name of the DataFrame
                Type: str

        RAISES:
            Exception.
            
        RETURNS:
            None.
        """
        
        try:
            column_values = self._connection.get_columns_of_dataset(value)
            for param_name in self._params:
                param = self._params[param_name]
                if param["datatype"] == "COLUMNS":
                    column_widget = param["widget"]
                    column_widget.options = [''] + column_values
        except Exception as e:
            # If the user has not typed a valid table
            return    
    
    def _get_output_dataframe(self):
        """
        Access the output dataframe of running BYOM function.

        PARAMETERS:
            None.

        RAISES:
            None.
            
        RETURNS: 
            The output dataframe, the type is based on the connection.
            Type: teradataml.DataFrame
        """
        return self._output_dataframe

