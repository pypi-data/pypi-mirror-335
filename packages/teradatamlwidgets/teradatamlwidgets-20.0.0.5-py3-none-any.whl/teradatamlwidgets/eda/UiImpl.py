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
import copy
import IPython, inspect, itertools
from IPython.display import clear_output, HTML,Javascript, display
import teradataml
import pandas as pd
from teradataml.common.utils import UtilFuncs
from teradataml.common.constants import TeradataConstants
from teradataml import DataFrame
from teradatamlwidgets.base_ui import _BaseUi, _TDVBoxWidget
from teradatamlwidgets.custom_confirm_button import *
import time

class _UiImpl(_BaseUi):
    """
    Private class that implements teradatamlwidgets EDA UI.
    """
    def __init__(
        self, 
        df,
        html=None):
        """
        DESCRIPTION:
            Constructor for private class that implements teradatamlwidgets EDA UI.

        PARAMETERS:
            df: 
                Required Argument. 
                Specifies the name of the input table.
                Type: DataFrame
            html:
                The HTML contents of the table created for Data tab.
                Types: str
                

        RETURNS:
            Instance of the EDA UI Implementation.

        RAISES:
            None.
        """
        
        _BaseUi.__init__(self, default_database="", connection=None, widget_output=ipywidgets.Output())
        
        self._df = df
        self._eda_df_unique_name = df._table_name
        if self._eda_df_unique_name is None:
            self._eda_df_unique_name = self._df.show_query()

        self._show_data_table = html is None

        # This is the JSON we use for load/save
        self._eda_json = {}

        # Reset settings to defaults
        self._reset_settings()

        # Load any settings from file if exists
        self._load_settings()

        self.__df_ui = None
        self.__describe_ui = None
        self.__plot_ui = None
        self.__analyze_ui = None
        self.__persist_ui = None

        if html == None:
            self._df._generate_output_html()
            html = self._df.html

        if self._connection.is_logged_in():
            self._create_ui(html)
            self._open_ui()

    def _on_save_click(self):
        """
        DESCRIPTION:
            Private function that is called when the user clicks the Save button.

        PARAMETERS:
            None.

        RETURNS:
            None. 
        """
        self._save_button.description = "Saving..."
        time.sleep(1)
        if self.__analyze_ui is not None:
            for index in range(len(self._analyze_function_widgets)):
                ui = self._analyze_function_widgets[index]
                ui_impl = ui._ui_impl
                ui_impl._on_save()
        if self.__plot_ui is not None:
            ui_impl = self.__pui._ui_impl
            ui_impl._update_settings(self._eda_json["plot"])

        # Create a EDA json we can save
        # We do not save out the executed_settings
        eda_json = {}
        eda_json["plot"] = self._eda_json["plot"]
        eda_json["analytic_functions"] = []
        for analytic_function in self._eda_json["analytic_functions"]:
            function = {}
            function['export_settings'] = analytic_function['export_settings']
            function['input_tablename'] = analytic_function['input_tablename']
            function['output_tablename'] = analytic_function['output_tablename']
            eda_json["analytic_functions"].append(function)        

        # Load current EDA settings
        file_name = ".eda_settings.json"
        eda_settings = {}
        if os.path.exists(file_name):
            with open(file_name, 'r') as file:
                contents = file.read()
            eda_settings = json.loads(contents)
        
        # Save out the settings in the EDA settings
        eda_settings[self._eda_df_unique_name] = eda_json
        json_string = json.dumps(eda_settings, indent=4)
        with open(file_name, "w") as outfile:
            outfile.write(json_string)
        self._save_button.description = "Save"

    def _reset_settings(self):
        """
        DESCRIPTION:
            Private function that gets called if the user clicks the Reset button, to reset whole EDA UI to defaults.

        PARAMETERS:
            None.

        RETURNS:
            None. 
        """
        new_table_name = UtilFuncs._generate_temp_table_name(table_type = TeradataConstants.TERADATA_TABLE)  
        self._eda_json["analytic_functions"] = []
        self._eda_json["analytic_functions"].append({"export_settings" : {}, "input_tablename" : self._df._table_name, "output_tablename" : new_table_name})
        self._eda_json["plot"] = {}
        
    def _load_settings(self):
        """
        DESCRIPTION:
            Private function that loads the settings if previously saved otherwise resets to defaults.

        PARAMETERS:
            None.

        RETURNS:
            None. 
        """
        try:
            file_name = ".eda_settings.json"
            if not os.path.exists(file_name):
                return
            with open(file_name, 'r') as file:
                contents = file.read()
            eda_settings = json.loads(contents)
            self._eda_json = eda_settings[self._eda_df_unique_name]
        except:
            self._reset_settings();

    def _show_widgets(self, item, clear=True):
        """
        DESCRIPTION:
            Private function that displays a widget in the cell.

        PARAMETERS:
            item: 
                Required Argument.
                The widget you want to display.
                Types: ipywidget

            clear:
                Optional Argument.
                Clear the cell.
                Default Value: True
                Types: bool

        RETURNS:
            None. 
        """
        import IPython
        if clear:
            self._clear_output()
        with self._widget_output:
            IPython.display.display(item)

    def _clear_output(self):
        """
        DESCRIPTION:
            Private function to clear all the UIs including the Plot and Analyze widgets.

        PARAMETERS:
            None.

        RETURNS:
            None. 
        """
        self._widget_output.clear_output(wait=True)
        try:
            self.__plot_ui._widget_output.clear_output(wait=True)
        except:
            pass
        try:
            self.__analyze_ui._widget_output.clear_output(wait=True)
        except:
            pass

    def _create_ui(self, html=None):
        """
        DESCRIPTION:
            Private function that creates EDA UI, with Data, Visualize, Analyze, Describe, Persist tabs.

        PARAMETERS:
            html:
                The HTML contents of the table created for Data tab.
                Types: str

        RETURNS:
            None.
        """
        self._widget_output = ipywidgets.Output()
        self._main_panel = ipywidgets.HBox([])
        # Create our own VBox which doesn't display anything in the repr to make printing not
        # have the extraneous printing of ipywidgets
        self._main_vbox = _TDVBoxWidget([self._main_panel, self._widget_output])
        IPython.display.display(self._main_vbox)

        self._html_ui = ipywidgets.HTML(value=html)

        self.layout_border = ipywidgets.Layout(border_bottom='4px #4169E1 solid')
        data_button = ipywidgets.Button(
            description='Data',
            disabled=False,
            tooltip='Print DataFrame',
            style={'button_color' : 'transparent', 'font_weight' : 'bold'},
            layout=self.layout_border
        )
        data_button.on_click(lambda x: self._on_data_click())

        self._describe_button = ipywidgets.Button(
            description='Describe',
            disabled=False,
            style={'button_color' : 'transparent', 'font_weight' : 'bold'},
            tooltip='Describe DataFrame'
        )
        self._describe_button.on_click(lambda x: self._on_describe_click())

        plot_button = ipywidgets.Button(
            description='Visualize',
            disabled=False,
            style={'button_color' : 'transparent', 'font_weight' : 'bold'},
            tooltip='Visualize Data'
        )
        plot_button.on_click(lambda x: self._on_visualize_click())

        self._analyze_button = ipywidgets.Button(
            description='Analyze',
            disabled=False,
            style={'button_color' : 'transparent', 'font_weight' : 'bold'},
            tooltip='Analyze Data'
        )
        self._analyze_button.on_click(lambda x: self._on_analyze_click())


        persist_button = ipywidgets.Button(
            description='Persist',
            disabled=False,
            style={'button_color' : 'transparent', 'font_weight' : 'bold'},
            tooltip='Persist the DataFrame in a table'
        )
        persist_button.on_click(lambda x: self._on_persist_click())

        self._save_button = ipywidgets.Button(
            description = 'Save',
            disabled=False,
            style = {'button_color' : 'white', 'text_color' : '#4169E1'},
            layout= ipywidgets.Layout(border = 'solid #727d9c', width='115px'),
            tooltip='Save EDA settings'
        )
        self._save_button.on_click(lambda x: self._on_save_click())

        reset_button = ConfirmationButton(description='Reset')
        reset_button.on_click(lambda x: self._reset_eda())

        with open(os.path.join(self._folder, 'logo.png'), 'rb') as f:
            logo = f.read()
  
        teradata_logo = ipywidgets.Image(
            value=logo,
            format='png',
            width=95,
            height=400
        )

        # This allows tab to be underlined when selected
        self.__buttons = {"Data" : data_button, "Describe" : self._describe_button,"Visualize" : plot_button, "Analyze" : self._analyze_button, "Persist" : persist_button}
        self._eda_status_message_widget = ipywidgets.Label("", style = {'text_color' : '#4169E1'})
        self.__hbox = ipywidgets.HBox(list(self.__buttons.values()) + [self._save_button, reset_button, teradata_logo])

        self._function_status_message_widget = ipywidgets.HTML("")

        self.__df_ui = ipywidgets.VBox([self.__hbox])

    def _on_show_data_table(self):
        """
        DESCRIPTION:
            Private function is called when number of rows changes.

        PARAMETERS:
            None.

        RETURNS:
            None. 
        """
        num_rows = 10
        df = self._df.head(num_rows)
        df = df.to_pandas()
        df = df.reset_index()
        indent = "\t"
        dindent = indent + indent
        html = '<html><table class="dataframe">\n<tr>\n'
        columns_html = "</th><th>".join(df.columns.to_list())
        html += "<th>{0}</th>\n".format(columns_html)
        html += "</tr>\n"
        for row in df.values.tolist():
            row_html = ["{0}<td>{1}</td>\n".format(dindent,
                                                   cell) for cell in row]
            html += "{1}<tr>\n{0}{1}</tr>\n".format("".join(row_html), indent)
        html += "</table></html>"
        html = html.replace('<tr style="text-align: right;">', '<tr>')
        html = html.replace('class="dataframe"', 'style="table-layout:fixed; width:100%; border-collapse: collapse; border:none;"')
        html = html.replace('border="1"', '')
        html = html.replace('<th>', '<th style="border:none;text-align: left;">')
        html = html.replace('<td>', '<td style="border:none;">')
        html = html.replace('<tr>', '<tr style="border-bottom: 1px solid black; border-bottom-color: #dcdcdc;">')
        self._html_ui.value = html

    def _on_data_click(self):
        """
        DESCRIPTION:
            Private function that shows the coinciding widgets when Data is clicked.

        PARAMETERS:
            None.

        RETURNS:
            None. 
        """
        self._update_button_layout("Data")
        if self._show_data_table:
            self._on_show_data_table()
            vbox = ipywidgets.VBox([self.__hbox, self._html_ui])
            self._show_widgets(vbox)
        else:
            self._show_widgets(self.__df_ui)

    def _on_persist_click(self):
        """
        DESCRIPTION:
            Private function that shows the coinciding widgets when Persist is clicked.

        PARAMETERS:
            None.

        RETURNS:
            None.
        """
        self._update_button_layout("Persist")
        if self.__persist_ui is None:
            from teradatamlwidgets.persist.Ui import Ui
            self.__persist = Ui(df=self._df)
            self.__persist_ui = self.__persist._ui_impl.get_widget()
        vbox = ipywidgets.VBox([self.__hbox, self.__persist_ui])
        self._show_widgets(vbox)

    def _on_describe_click(self):
        """
        DESCRIPTION:
            Private function that shows the coinciding widgets when Describe is clicked.

        PARAMETERS:
            None.

        RETURNS:
            None. 
        """
        self._update_button_layout("Describe")
        if self.__describe_ui is None:
            from teradatamlwidgets.describe.Ui import Ui
            self.__describe = Ui(df=self._df)
            self.__describe_ui = self.__describe._ui_impl.get_widget()
        vbox = ipywidgets.VBox([self.__hbox, self.__describe_ui])
        self._show_widgets(vbox)

    def _update_button_layout(self, name):
        """
        DESCRIPTION:
            Private function that updates the layout so that the top-level arrangement looks more like a tab 
            (with styled blue color underline) which indicate what is selected.

        PARAMETERS:
            name: 
                Required Argument. 
                The key name from the dictionary self.__buttons (a button name).
                Type: str

        RETURNS:
            None.
        """
        for key in self.__buttons:
            if name != key:
                self.__buttons[key].layout = ipywidgets.Layout()
            else:
                self.__buttons[key].layout = ipywidgets.Layout(border_bottom='4px #4169E1 solid')

    def _on_visualize_click(self):
        """
        DESCRIPTION:
            Private function that shows the coinciding widgets when Visualize is clicked.

        PARAMETERS:
            None.

        RETURNS:
            None.
        """
        self._update_button_layout("Visualize")

        if self.__plot_ui is None:
            from teradatamlwidgets.plot.Ui import Ui
            self.__pui = Ui(df=self._df,
                            current_plot="Line",
                            color='green',
                            eda_mode=True,
                            **self._eda_json["plot"])

            self.__plot_ui = self.__pui._ui_impl._plot_ui
            
        vbox = ipywidgets.VBox([self.__hbox, self.__plot_ui])

        self._show_widgets(vbox)

    def _on_analyze_click(self):
        """
        DESCRIPTION:
            Private function that shows the coinciding widgets when Analyze is clicked.

        PARAMETERS:
            None.

        RETURNS:
            None.
        """
        self._update_button_layout("Analyze")

        if self.__analyze_ui is None:
            self._analyze_button.description = "Analyzing..."
            self._function_tabs = ipywidgets.Tab()
            self._make_analytic_tab_ui()
            self.__analyze_ui = self._function_tabs
            self._analyze_button.description = "Analyze"

        # Update all the tabs
        for index in range(len(self._function_tabs.children)):
            self._update_tab(index)
            
        vbox = ipywidgets.VBox([self.__hbox, self.__analyze_ui, self._function_status_message_widget])
        self._show_widgets(vbox)

    def _make_analytic_tab_ui(self):
        """
        DESCRIPTION:
            Private function that creates a tab for each function within Analytic UI.

        PARAMETERS:
            None.

        RETURNS:
            None.
        """

        children_function_tabs = []
        self._function_status_message_widget.value = "Opening Analytic Functions ..."
        self._analyze_function_widgets = []
        for current_function in self._eda_json["analytic_functions"]:
            # get all the infomration needed to create an analytic function UI
            input_tablename = current_function["input_tablename"]
            if input_tablename == self._df._table_name:
                input_df = self._df
            else:
                input_df = input_tablename     
            export_settings = current_function["export_settings"]
            output_tablename = current_function["output_tablename"]
            
            # Add the new analytic function
            function_ui = self._add_analytic_function(current_function, input_df, export_settings, output_tablename)

            # Keep track of all function widgets as we will add these as tabs
            children_function_tabs.append(function_ui)

            self._function_tabs.children = children_function_tabs

        self._function_tabs.children = children_function_tabs
        self._update_tab_names()
        self._function_status_message_widget.value = ""

        
    def _update_input_table_columns(self, update_index):
        """
        DESCRIPTION:
            Private function that updates the input columns for the next function.

        PARAMETERS:
            update_index: 
                The new index the selected tab should be set to.
                Type: int

        RETURNS:
            None.
        """
        # A function got executed so we need to update the columns in the UI for the next function
        if update_index<0 or update_index>=len(self._analyze_function_widgets):
            return
        try:
            ui = self._analyze_function_widgets[update_index]
            _ui_impl = ui._ui_impl
            _ui_impl._update_input_table_columns()
        except:
            # Input table is not available to update
            return

    def _update_tab_names(self):
        """
        DESCRIPTION:
            Private function that updates the tab names from Function to the function chosen.

        PARAMETERS:
            None.

        RETURNS:
            None.
        """
        self._function_status_message_widget.value = ""
        for i in range(len(self._function_tabs.children)):
            current_function = self._eda_json["analytic_functions"][i]
            # Save to get the function name
            ui = self._analyze_function_widgets[i]
            ui_impl = ui._ui_impl
            ui_impl._on_save()
            # if the function name exists in the json then the title will be set to that function name
            if "function_name" in current_function["export_settings"]:
                title = "{}. {}".format(i+1, current_function["export_settings"]["function_name"])
            else:
                # if it is a new tab then the name will be the tab-number. Function
                # this is because no function is chosen yet by user
                title = "{}. Function".format(i+1)
            self._function_tabs.set_title(index=i,title=title)

    def _execute_all_functions(self):
        """
        DESCRIPTION:
            Private function that executes multiple functions across tabs. 

        PARAMETERS:
            None.

        RETURNS:
            None.
        """

        number_functions_to_execute = self._function_tabs.selected_index + 1
        
        self._function_status_message_widget.value = ""
        try:
            something_executed = False
            for index in range(number_functions_to_execute):
                ui = self._analyze_function_widgets[index]
                ui_impl = ui._ui_impl
                
                # Save the settings (i.e. the values in UI will get saved into "settings"
                ui_impl._on_save()

                if not something_executed:
                    # Check to see if we should execute
                    current_function = self._eda_json["analytic_functions"][index]
                    if "executed_settings" in current_function:
                        if current_function["executed_settings"] == current_function["export_settings"]:
                            # No need to execute as nothing changed and we already executed
                            try:
                                ui_impl._show_execution_results()
                                continue
                            except:
                                # We must execute again as table isnt available
                                something_executed = False
                something_executed = True
                # message to show which function is currently being executed
                self._function_status_message_widget.value = "Executing " + self._function_tabs.titles[index]
                ui_impl._execute_query()
                self._function_status_message_widget.value = ""
                # Keep a copy of the settings that were executed
                # THis is used to not execute again if we did so already
                current_function["executed_settings"] = copy.deepcopy(current_function["export_settings"])



        except Exception as e:
            self._function_status_message_widget.value = "<p style='color:red;'>Error in executing " + self._function_tabs.titles[index] + " " + str(e) + "</p>"

    def _reset_eda(self):
        """
        DESCRIPTION:
            Private function that resets the entire EDA UI, clearing any saved parameters in the tabs. 

        PARAMETERS:
            None.

        RETURNS:
            None.
        """
        # used when user saves their work i.e. creates multiple tabs in Analyze, but then want to clear and start from scratch
        try:
            self._function_status_message_widget.value = "Reseting EDA"
            self._reset_settings()
            self._function_status_message_widget.value = ""
            self.__plot_ui = None
            self.__analyze_ui = None
            self._on_data_click()

        except Exception as e:
            self._function_status_message_widget.value = "You cannot reset"

    def _add_analytic_function(self, new_function = None, input = None, export_settings = None, output_tablename = None):
        """
        DESCRIPTION:
            Private function that adds an Analytic Function tab. All parameters should be set to None with new Analytic tab creation.

        PARAMETERS:
            new_function: 
                The function selected for the new analytic tab.
                Type: str
            input: 
                The input table name.
                Type: str
            export_settings: 
                The saved parameters.
                Type: dict
            output_tablename: 
                The output table name.
                Type: str

        RETURNS:
            None.
        """
        from teradatamlwidgets.analytic_functions.Ui import Ui

        self._function_status_message_widget.value = "Adding new pipeline step..."
         
        need_update = True
        # When new_function is None this is when the user clicked the "Add pipeline"
        if new_function == None:
            # Add after selected tab
            selected_index = self._function_tabs.selected_index + 1
            # Get the prior function as we need to get its output as the new functions input
            input = self._eda_json["analytic_functions"][self._function_tabs.selected_index]["output_tablename"]
            # Create an empty settings and temp output table
            export_settings = {}
            output_tablename = UtilFuncs._generate_temp_table_name(table_type = TeradataConstants.TERADATA_TABLE)  
            # Create settings for the new function
            new_function = {"export_settings" : export_settings, "input_tablename" : input, "output_tablename" : output_tablename}
            # Add the settings of new function to the EDA json
            self._eda_json["analytic_functions"].insert(selected_index, new_function)
        else:
            # This case is called when we first show the function and we always add to the end
            selected_index = len(self._function_tabs.children)
            need_update = False

        if selected_index == 0:
            inputs = [self._df]
        else:
            inputs = [input]
            inputs.append(self._df)

        # Create the new analytic function UI
        ui = Ui(inputs=inputs, export_settings=export_settings, outputs=[output_tablename], eda_mode=True)            
        # add the ui to the list of analytic function widgets
        self._analyze_function_widgets.insert(selected_index, ui)
        _ui_impl = ui._ui_impl
        _ui_impl._eda_widget_output = self._widget_output          
        function_ui = _ui_impl._function_ui
        # Informs the Analytic Function UI about EDA status message so it can post messages 
        _ui_impl._set_eda_message_widget(self._function_status_message_widget)
        # Get a callback when the current function changes, as we need to update the tab name
        _ui_impl._current_function.observe(lambda x : self._update_tab_names(), names='value')
        # Get a callback when we execute, so we can update the input table for the next analytic function
        _ui_impl._execute.on_click(lambda x : self._update_input_table_columns(selected_index+1))
        
        _ui_impl._add.on_click(lambda x : self._add_analytic_function())
        _ui_impl._remove.on_click(lambda x : self._remove_analytic_function())
        _ui_impl._execute.on_click(lambda x : self._execute_all_functions())
        _ui_impl._move_later.on_click(lambda x : self._move_function(later = True))
        _ui_impl._move_earlier.on_click(lambda x : self._move_function(later = False))

        if not need_update:
            self._function_status_message_widget.value = ""
            return function_ui

        # Add the new analytic function UI to tab
        current_function_tabs = list(self._function_tabs.children)
        current_function_tabs.insert(selected_index, function_ui)
        self._function_tabs.children = current_function_tabs

        self._update_tab_names()

        # Need to adjust the output table names
        self._update_tab(selected_index + 1)

        self._function_status_message_widget.value = ""

        if need_update:
            # Change the tab to the new tab we added
            self._function_tabs.selected_index = selected_index


    def _remove_analytic_function(self):
        """
        DESCRIPTION:
            Private function that removes an Analytic Function tab. 

        PARAMETERS:
            None.

        RETURNS:
            None.
        """
        if len(self._function_tabs.children) == 1:
            self._function_status_message_widget.value = "<p style='color:red;'> You must have at least 1 function always </p>"
            return
        self._function_status_message_widget.value = "Removing step from pipeline..."
   
        selected_index = self._function_tabs.selected_index
        # Remove from EDA json
        self._eda_json["analytic_functions"].remove(self._eda_json["analytic_functions"][selected_index])
        # Remove from analytic function list
        self._analyze_function_widgets.remove(self._analyze_function_widgets[selected_index])
        # Remove from tab
        current_function_tabs = list(self._function_tabs.children)
        current_function_tabs.remove(self._function_tabs.children[selected_index])
        self._function_tabs.children = current_function_tabs
        
        # Need to adjust the output table names
        self._update_tab(selected_index)

        self._function_status_message_widget.value = ""
        
    def _update_tab(self, update_index):
        """
        DESCRIPTION:
            Private function that is called when any tab is changed, i.e. tab is added, removed, or moved. 

        PARAMETERS:
            update_index: 
                The new index the selected tab should be set to.
                Type: int

        RETURNS:
            None.
        """
        prior_index = update_index - 1
        if update_index < 0 or update_index >= len(self._eda_json["analytic_functions"]):
            return
 
        # Save the function we need to update so we get all its values in our EDA json
        ui = self._analyze_function_widgets[update_index]
        ui_impl = ui._ui_impl
        ui_impl._on_save()

        if prior_index == -1:
            # The fist function will always get input from the EDA source
            updated_input_tablename = ""
        else:
            # Get the updated input from the prior function - it will be its output table
            updated_input_tablename = self._eda_json["analytic_functions"][prior_index]["output_tablename"]

        # Update all our inputs accordingly in the config JSON
        current_function = self._eda_json["analytic_functions"][update_index]

        original_tablename = current_function["input_tablename"]

        # Update all input tables 
        if 'required_input' in current_function['export_settings']:
            for required_input in current_function['export_settings']['required_input']:
                required_input['value'] = updated_input_tablename

        current_function["input_tablename"] = updated_input_tablename

        if update_index == 0:
            inputs = [self._df]
        else:
            inputs = [updated_input_tablename, self._df]

        # Update the UI analytic function to know about the new updated input
        ui_impl._update_input_table_names(inputs)

        # If we have previously executed, then we should remove settings since it has been changed
        if "executed_settings" in current_function:
            del current_function["executed_settings"]
        
        # We could force the entire ui to reload but this is slow
        # ui_impl._on_load()

        self._update_tab_names()


    def _move_function(self, later):
        """
        DESCRIPTION:
            Private function that is called if the move to left or move to right buttons arte clicked. 

        PARAMETERS:
            later: 
                If later is set to true, then it means the tab needs to move to the right, to later in pipeline.
                If later is set to false, it means selected tab needs to move to left, to previously in pipeline.
                Type: bool

        RETURNS:
            None.
        """
        current_index = self._function_tabs.selected_index
        if not later:
            current_index -= 1

        if current_index == len(self._analyze_function_widgets) - 1:
            return
        self._function_status_message_widget.value = "Moving function to later in pipeline..."
        # switch the analytic function UI 
        self._analyze_function_widgets[current_index], self._analyze_function_widgets[current_index + 1] = self._analyze_function_widgets[current_index + 1], self._analyze_function_widgets[current_index]
        # switch the eda json settings
        self._eda_json["analytic_functions"][current_index], self._eda_json["analytic_functions"][current_index + 1] = self._eda_json["analytic_functions"][current_index + 1], self._eda_json["analytic_functions"][current_index]
        # switch tabs
        current_function_tabs = list(self._function_tabs.children)
        current_function_tabs[current_index], current_function_tabs[current_index + 1] = current_function_tabs[current_index + 1], current_function_tabs[current_index]
        self._function_tabs.children = current_function_tabs
        self._update_tab_names()

        self._update_tab(current_index)
        self._update_tab(current_index + 1)
        self._update_tab(current_index + 2)

        self._function_status_message_widget.value = ""

                
    def _open_ui(self):
        """
        DESCRIPTION:
            Private function that opens the teradatamlwidgets EDA UI. 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._show_widgets(self.__df_ui)
        self._on_data_click()

    def get_widget(self):
        """
        DESCRIPTION:
            Private function that returns the EDA UI. 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            Instance of EDA UI.
        """
        return self.__df_ui
        
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
                Type: str
                Default Value: ""
                
        EXCEPTIONS:
            None.

        RETURNS: 
            teradataml.DataFrame
        
        EXAMPLE:
            df = ui.get_output_dataframe(0)
        """
        if self.__analyze_ui is None:
            return None
        if len(self._analyze_function_widgets) == 0:
            return None
        return self._analyze_function_widgets[-1].get_output_dataframe(output_index=output_index)
        
    def display_ui(self):
        """
        DESCRIPTION:
            Function that displays the teradatamlwidgets EDA UI. 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        IPython.display.display(self._main_vbox)
        self._open_ui()

