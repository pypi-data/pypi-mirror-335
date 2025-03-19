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
from teradataml.common.utils import UtilFuncs
from teradataml.automl import AutoML, AutoRegressor, AutoClassifier
from teradatamlwidgets.base_ui import _BaseUi
from teradataml.context.context import _get_current_databasename


class _UiImpl(_BaseUi):
    """
    Private class that implements teradatamlwidgets Interactive AutoML UI.
    """
    def __init__(
        self, 
        training_table,  
        predict_table=None,
        task = "Classification",
        target_column=None, 
        algorithms=None, 
        verbose=0, 
        max_runtime_secs=None, 
        stopping_metric=None, 
        stopping_tolerance=None, 
        max_models=None, 
        custom_config_file=None,
        rank=1,
        persist=False,
        widget_output=False,
        default_database="", 
        connection = None,
        analytic_function_ui = None):
        """
        DESCRIPTION:
            Constructor for private class that implements teradatamlwidgets Interactive AutoML UI.

        PARAMETERS:
            training_table: 
                Required Argument. 
                Specifies the input teradataml DataFrame or string that contains the data which is used for training. 
                Types: Str or teradataml DataFrame
                
            predict_table: 
                Optional Argument. 
                Specifies the teradataml DataFrame or string that contains the data which is used for predictions.
                Types: str or teradataml.DataFrame

            task: 
                Optional Argument. 
                Specifies the name of the task:.
                Permitted Values: "Classification", "Regression". 
                Types: str

            algorithms:
                Optional Argument.
                Specifies the model algorithms to be used in model training phase.
                By default, all 5 models are used for training for regression and binary
                classification problem, while only 3 models are used for multi-class.
                Permitted Values: "glm", "svm", "knn", "decision_forest", "xgboost"
                Types: str OR list of str

            verbose:
                Optional Argument.
                Specifies the detailed execution steps based on verbose level.
                Default Value: 0
                Permitted Values: 
                    * 0: prints the progress bar and leaderboard.
                    * 1: prints the execution steps of AutoML.
                    * 2: prints the intermediate data between the execution of each step of AutoML.
                Types: int

            max_runtime_secs:
                Optional Arugment.
                Specifies the time limit in seconds for model training.
                Types: int

            stopping_metric:
                Required, when "stopping_tolerance" is set, otherwise optional.
                Specifies the stopping metrics for stopping tolerance in model training.
                Permitted Values: 
                    * For task type "Regression": "R2", "MAE", "MSE", "MSLE", 
                                                  "RMSE", "RMSLE"
                    * For task type "Classification": 'MICRO-F1','MACRO-F1',
                                                      'MICRO-RECALL','MACRO-RECALL',
                                                      'MICRO-PRECISION', 'MACRO-PRECISION',
                                                      'WEIGHTED-PRECISION','WEIGHTED-RECALL',
                                                      'WEIGHTED-F1', 'ACCURACY'
                Types: str

            stopping_tolerance:
                Required, when "stopping_metric" is set, otherwise optional.
                Specifies the stopping tolerance for stopping metrics in model training.
                Types: float
                
            max_models:
                Optional Argument.
                Specifies the maximum number of models to be trained.
                Types: int

            custom_config_file:
                Optional Argument.
                Specifies the path of JSON file in case of custom run.
                Types: str
                
            rank:
                Optional Argument.
                Specifies the rank of the model in the leaderboard to be used for prediction.
                Default Value: 1
                Types: int

            target_column:
                Required Arugment.
                Specifies target column of dataset.
                Types: str

            persist:
                Optional Argument.
                Specifies whether to persist the interim results of the
                functions in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool

            connection: 
                Optional Argument. 
                Specifies the specific connection; could be teradataml based (i.e. TeradatamlConnection instance) or another platform.

            default_database: 
                Optional Argument. 
                Specifies the default database. 
                Types: str

            widget_output:
                Optional Argument
                Specifies an ipywidget that this Ui should be embedded into, otherwise will create its own output
                Default Value: None
                Types: ipywidgets.Output

            analytic_function_ui:
                Optional Argument
                Specifies the Analytic Function UI that the AutoML UI will be placed inside 
                otherwise AutoML UI will show as a standalone widget. 
                Default Value: None
                Types: auto_ml._UiImpl
                

        RETURNS:
            Instance of the UI Implementation.

        RAISES:
            None.
        """
        
        _BaseUi.__init__(self, default_database=default_database, connection=connection, widget_output=widget_output)
        
        self._analytic_function_ui = analytic_function_ui
        self._fit_completed = False
        self._predicted_output = None
        self._automl_obj = None
        self._include = algorithms if algorithms != None else []
        self._target_column = target_column if target_column != None else ""
        self._verbose = verbose
        self._max_runtime = max_runtime_secs if max_runtime_secs != None else 0
        self._stopping_metric = stopping_metric if stopping_metric != None else ""
        self._stopping_tolerance = stopping_tolerance if stopping_tolerance != None else 0.0
        self._custom_config_file = custom_config_file
        self._rank = rank
        self._max_models = max_models
        self._persist = persist
        self._embedded_mode = widget_output != False
        self._allow_logout = self._embedded_mode

        self._training_table = training_table
        self._predict_table = predict_table
        
        self._current_task = task
        
        if self._connection.is_logged_in():
            self._login_info['default_db'] = default_database if default_database else _get_current_databasename()
            self._create_ui()
            self._open_ui()

    def _update_auto_ml(self):
        """
        DESCRIPTION:
            Updates the AutoML instance with the lastest values from the UI.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        try:
            kwargs = {}
            if self._persist_ui.value:
                kwargs['persist'] = True
            if self._include_ui.value:
                kwargs['include'] = list(self._include_ui.value)
            if self._verbose_ui.value != 0:
                kwargs['verbose'] = self._verbose_ui.value
            if self._max_runtime_ui.value != 0:
                kwargs['max_runtime_secs'] = self._max_runtime_ui.value
            if self._stopping_metric_ui.value:
                kwargs['stopping_metric'] = self._stopping_metric_ui.value
            if self._stopping_tolerance_ui.value != 0.0:
                kwargs['stopping_tolerance'] = self._stopping_tolerance_ui.value
            if self._custom_config_file:
                kwargs['custom_config_file'] = self._custom_config_file
            if self._max_models_ui.value != 0:
                kwargs['max_models'] = self._max_models_ui.value
            if self._tasks.value == "Classification":
                self._automl_obj = AutoClassifier(**kwargs)
            elif self._tasks.value == "Regression":
                self._automl_obj = AutoRegressor(**kwargs)
            self._predicted_output = None
            self._fit_completed = False
        except Exception as e:
            self._automl_obj = None
            self._show_error_message(e)

    def _verify_automl_exists(self):
        """
        DESCRIPTION:
            Private function that checks if AutoML instance is available otherwise returns exception.

        PARAMETERS:
            None.
        
        RAISES:
            RuntimeError.

        RETURNS:
            None.
        """
        if self._automl_obj == None:
            raise RuntimeError("No Auto ML instance available")

    def _verify_fitting_completed(self):
        """
        DESCRIPTION:
            Private function that checks if fitting has happened otherwise returns exception.

        PARAMETERS:
            None.
        
        RAISES:
            RuntimeError.

        RETURNS:
            None.
        """
        if not self._fit_completed:
            raise RuntimeError("Not fitted yet")
    
    def _on_fit(self):
        """
        DESCRIPTION:
            Private function that is called when Fit button is pressed
            and will do the fit on the teradataml AutoML instance.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._verify_automl_exists()
        if not self._embedded_mode:
            self._widget_output.clear_output(wait=True)
        with self._widget_output:
            try:
                self._automl_obj.fit(self._training_table, self._target_column_ui.value)
                self._fit_completed = True
                self._show_dialog("Completed Fitting", False)
            except Exception as e:
                self._fit_completed = False
                self._show_error_message(e)
        self._predicted_output = None
        
    def _on_prediction(self):
        """
        DESCRIPTION:
            Private function that is called when Predict Execute button is pressed
            and will do the predict on the teradataml AutoML instance and show. 
            the predicted table in the cell

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        try:
            self._verify_automl_exists()
            self._verify_fitting_completed()
            
            if not self._embedded_mode:
                self._widget_output.clear_output(wait=True)
            with self._widget_output:
                try:
                    schema_name = UtilFuncs._extract_db_name(self._predict_table._table_name) if self._predict_table._table_name else ''
                    table_name = UtilFuncs._extract_table_name(self._predict_table._table_name) if self._predict_table._table_name else ''
                    # Use Constructor passed prediction dataframe or UI specified dataframe
                    if schema_name == self._predict_schema_name.value and table_name == self._predict_table_name.value:
                        df = self._predict_table
                    else:
                        if self._predict_schema_name.value:
                            qualified_name = UtilFuncs._in_schema(
                                self._predict_schema_name.value, 
                                self._predict_table_name.value)
                        else:
                            qualified_name = self._predict_table_name.value
                        df = DataFrame(qualified_name)
                    self._predicted_output = self._automl_obj.predict(df, self._rank_ui.value)
                except Exception as e:
                    self._predicted_output = None
                    self._show_error_message(e)
                    return
            
            try:
                self._show_dialog("Completed Prediction", False)
                return
            except:
                with self._widget_output:
                    print(str(e))
            # Clear the progress bar
            self._show_display(self._task_ui)
        except Exception as e:
            self._predicted_output = None
            self._show_error_message(e)

    def _on_load(self):
        """
        DESCRIPTION:
            Private function that is called when Load button is pressed
            and will load the automl instance from a table.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        try:
            
            self._verify_automl_exists()
            if not self._embedded_mode:
                self._widget_output.clear_output(wait=True)
            with self._widget_output:
                try:
                    print("Start Loading")
                    self._predicted_output = None
                    schema_name = self._load_schema_name.value
                    table_name = self._load_table_name.value
                    if schema_name:
                        qualified_name = UtilFuncs._in_schema(schema_name, table_name)
                    else:
                        qualified_name = table_name
                    self._automl_obj.load(qualified_name)
                    self._fit_completed = True
                except Exception as e:
                    self._fit_completed = False
                    self._show_error_message(e)
                    return
            try:
                self._show_dialog("Completed Loading", False)
                return
            except:
                with self._widget_output:
                    print(str(e))
            # Clear the progress bar
            self._show_display(self._task_ui)
        except Exception as e:
            self._show_error_message(e)


    def _on_deploy(self):
        """
        DESCRIPTION:
            Private function that is called when Deploy button is pressed
            and will do the deploy to a table.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        try:
            self._verify_automl_exists()
            self._verify_fitting_completed()
            
            if not self._embedded_mode:
                self._widget_output.clear_output(wait=True)
            with self._widget_output:
                try:
                    print("Start Deploy")
                    schema_name = self._deploy_schema_name.value
                    table_name = self._deploy_table_name.value
                    if schema_name:
                        qualified_name = UtilFuncs._in_schema(schema_name, table_name)
                    else:
                        qualified_name = table_name
                    ranks = None
                    if self._ranks.value:
                        ranks = self._ranks.value.split(',')
                        ranks = [int(value) for value in ranks]
                    self._automl_obj.deploy(qualified_name, top_n=self._top_n.value, ranks=ranks)
                except Exception as e:
                    self._show_error_message(e)
                    return
            try:
                self._show_dialog("Completed Deployment", False)
                return
            except:
                with self._widget_output:
                    print(str(e))
            # Clear the progress bar
            self._show_display(self._task_ui)
        except Exception as e:
            self._show_error_message(e)

       
    def _on_leaderboard(self):
        """
        DESCRIPTION:
            Private function that is called when Leaderboard button is pressed
            and will show the leaderboard table in the cell.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        try:
            self._verify_automl_exists()
            self._verify_fitting_completed()
                
            # Display output dataframe
            df = self._automl_obj.leaderboard().head()
            try:
                markup = df.to_html().replace("\n", ' ')
                self._show_dialog(markup)
                return
            except:
                with self._widget_output:
                    print(str(e))

            # Clear the progress bar
            self._show_display(self._task_ui)
            
        except Exception as e:
            self._predicted_output = None
            self._show_error_message(e)

    def _save(self, dictionary):
        """
        DESCRIPTION:
            Private function that saves latest values in UI into dictionary

        PARAMETERS:
            dictionary:
                Specifies the dictionary where the ui values should be stored
                Types: dict
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        dictionary['tasks'] = self._tasks.value
        dictionary['include'] = self._include_ui.value
        dictionary['max_runtime'] = self._max_runtime_ui.value
        dictionary['max_models'] = self._max_models_ui.value
        dictionary['stopping_tolerance'] = self._stopping_tolerance_ui.value
        dictionary['persist'] = self._persist_ui.value
        dictionary['verbose'] = self._verbose_ui.value
        dictionary['max_runtime_secs'] = self._max_runtime_ui.value
        dictionary['stopping_metric'] = self._stopping_metric_ui.value

    def _load(self, dictionary):
        """
        DESCRIPTION:
            Private function Load latest values into UI from dictionary

        PARAMETERS:
            dictionary:
                Specifies the dictionary where the ui values should be loaded from
                Types: dict
        
        RAISES:
            None.

        RETURNS:
            None.
        """ 
        if 'tasks' in dictionary:
            self._tasks.value = dictionary['tasks']
        if 'include' in dictionary:
            self._include_ui.value = dictionary['include']
        if 'max_runtime' in dictionary:
            self._max_runtime_ui.value = dictionary['max_runtime']
        if 'max_models' in dictionary:
            self._max_models_ui.value = dictionary['max_models']
        if 'stopping_tolerance' in dictionary:
            self._stopping_tolerance_ui.value = dictionary['stopping_tolerance']
        if 'persist' in dictionary:
            self._persist_ui.value = dictionary['persist']
        if 'verbose' in dictionary:
            self._verbose_ui.value = dictionary['verbose']
        if 'max_runtime_secs' in dictionary:
            self._max_runtime_ui.value = dictionary['max_runtime_secs']
        if 'stopping_metric' in dictionary:
            self._stopping_metric_ui.value = dictionary['stopping_metric']
        
    def _update_training_table(self, training_table, predict_table):
        """
        DESCRIPTION:
            Private function that we update the training and predict tables

        PARAMETERS:
            training_table: 
                Required Argument. 
                Specifies the input teradataml DataFrame or string that contains the data which is used for training. 
                Types: Str or teradataml DataFrame
                
            predict_table: 
                Required Argument. 
                Specifies the teradataml DataFrame or string that contains the data which is used for predictions.
                Types: str or teradataml.DataFrame
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        self._training_table = training_table
        self._predict_table = predict_table
        try:
            if not isinstance(self._training_table, DataFrame):
                self._training_table = DataFrame(self._training_table)
            if self._predict_table == None:
                self._predict_table = self._training_table
            if not isinstance(self._predict_table, DataFrame):
                self._predict_table = DataFrame(self._predict_table)
        except:
            self._training_table = None
            self._predict_table = None        


    def _create_ui(self):      
        """
        DESCRIPTION:
            Private function that creates the ipywidgets UI for AutoML.

        PARAMETERS:
        
        RAISES:
            None.

        RETURNS:
            None.
        """         
        
        # Set DataFrame's
        self._update_training_table(self._training_table, self._predict_table)
            
        tabs = []
        param_widgets = []
        
        self._tasks = ipywidgets.Dropdown(
            options=["Classification", "Regression"],
            value=self._current_task,
            layout = {'width': '120px'},
            tooltip="Specifies the task type, whether to apply regression or classification on the provided dataset",
            disabled=False,
        )
        self._tasks.observe(lambda x : self._on_tasks_changed(), names='value')
        param_widgets.append(self._tasks)

        self._include_ui = ipywidgets.SelectMultiple(
            options=["glm", "svm", "knn", "decision_forest", "xgboost"],
            value=self._include,
            description='Algorithms:',
            tooltip="Specifies the model algorithms to be used for model training phase",
            disabled=False
        )
        self._include_ui.observe(lambda x : self._update_auto_ml(), names='value')
        
        param_widgets.append(self._include_ui)
        
        self._max_runtime_ui = ipywidgets.BoundedIntText(
            value=self._max_runtime,
            min=0,
            max=100000,
            step=1,
            description='Max Runtime:',
            tooltip="Specifies the time limit in seconds for model training",
            disabled=False,
            style=dict(description_width='150px')
        )
        
        self._max_runtime_ui.observe(lambda x : self._update_auto_ml(), names='value')
        
        self._max_models_ui = ipywidgets.BoundedIntText(
            value=self._max_models,
            min=0,
            max=20,
            step=1,
            description='Max Models:',
            tooltip="Specifies the maximum number of models to be trained",
            disabled=False
        )

        param_widgets.append(ipywidgets.HBox([self._max_runtime_ui, self._max_models_ui]))
        
        self._stopping_metric_ui = ipywidgets.Dropdown(
                options = self._get_stopping_metric_options(),
                value=self._stopping_metric,
                description='Stopping Metric:',
                tooltip="Specifies the stopping metrics for stopping tolerance in model training",
                disabled=False,
                style=dict(description_width='150px')
            )
        self._stopping_metric_ui.observe(lambda x : self._update_auto_ml(), names='value')

        
        self._stopping_tolerance_ui = ipywidgets.BoundedFloatText(
            value=self._stopping_tolerance,
            min=0,
            max=10000.0,
            step=0.01,
            description='Stopping Tolerance:',
            tooltip="Specifies the stopping tolerance for stopping metrics in model training",
            disabled=False,
            style=dict(description_width='150px')
        )
        self._stopping_tolerance_ui.observe(lambda x : self._update_auto_ml(), names='value')


        param_widgets.append(ipywidgets.HBox([self._stopping_metric_ui, self._stopping_tolerance_ui]))
        
        self._verbose_ui = ipywidgets.Dropdown(
            options=[('Progress Bar and Leaderboard', 0), ('Execution Steps', 1), ('Intermediate Steps', 2)],
            value=self._verbose,
            tooltip="Specifies the detailed execution steps based on verbose level",
            description='Verbose:',
        )
        self._verbose_ui.observe(lambda x : self._update_auto_ml(), names='value')
        
        self._persist_ui = ipywidgets.Checkbox(
            value=self._persist,
            tooltip="Specifies whether to persist the interim results of the functions in a table or not",
            description='Persist',
        )
        self._persist_ui.observe(lambda x : self._update_auto_ml(), names='value')


        param_widgets.append(ipywidgets.HBox([self._verbose_ui, self._persist_ui]))
        
        columns = [""]
        if self._training_table is None:
            columns = []
        else:
            columns.extend(self._training_table.columns)
        self._target_column_ui = ipywidgets.Combobox(
                options = columns,
                value=self._stopping_metric,
                description='Target Column:',
                tooltip="Specifies target column of dataset",
                disabled=False,
                style=dict(description_width='150px')
            )
       
        training_execute = ipywidgets.Button(description="Fit", 
            style= dict(description_width='150px', button_color='#4169E1', text_color='white'))
        training_execute.on_click(lambda x : self._on_fit())
 
        self._leadership_board = ipywidgets.Button(
            description='Leader Board',
            disabled=False,
            tooltip='Show the Leadership board',
            style=dict(description_width='150px')
        )
        self._leadership_board.on_click(lambda x : self._on_leaderboard())
    
        param_widgets.append(ipywidgets.HBox([self._target_column_ui, training_execute, self._leadership_board]))
        
        tabs.append(ipywidgets.VBox(param_widgets))
        param_widgets = []
        
        # Prediction Tab
        self._rank_ui = ipywidgets.BoundedIntText(
            value=self._rank,
            min=1,
            max=20,
            step=1,
            description='Rank:',
            tooltip="Specifies the rank of the model in the leaderboard to be used for prediction",
            layout = {'width': '80%'},
            disabled=False
        )
        param_widgets.append(self._rank_ui)
        
        predict_db_name = ''
        predict_table_name = ''
        if self._predict_table is not None:
            predict_db_name = UtilFuncs._extract_db_name(self._predict_table._table_name) if self._predict_table._table_name else ''
            predict_table_name = UtilFuncs._extract_table_name(self._predict_table._table_name) if self._predict_table._table_name else ''
        self._predict_schema_name = ipywidgets.Text(
            value=predict_db_name,
            placeholder='Specify Schema',
            description='Schema:',
            layout = {'width': '80%'},
            disabled=False
        )
        param_widgets.append(self._predict_schema_name)
        self._predict_table_name = ipywidgets.Text(
            value=predict_table_name,
            placeholder='Specify Table',
            layout = {'width': '80%'},
            description='Table:',
            disabled=False
        )
        param_widgets.append(self._predict_table_name)
        predict_execute = ipywidgets.Button(description="Execute", 
            style= dict(description_width='150px', button_color='#4169E1', text_color='white'))
        predict_execute.on_click(lambda x : self._on_prediction())
        param_widgets.append(predict_execute)
        
        tabs.append(ipywidgets.VBox(param_widgets))
        param_widgets = []

        # Load
        self._load_schema_name = ipywidgets.Text(
            value='',
            placeholder='Specify Schema',
            description='Schema:',
            layout = {'width': '80%'},
            disabled=False
        )
        param_widgets.append(self._load_schema_name)
        self._load_table_name = ipywidgets.Text(
            value='',
            placeholder='Specify Table',
            layout = {'width': '80%'},
            description='Table:',
            disabled=False
        )
        param_widgets.append(self._load_table_name)
        load_executue = ipywidgets.Button(description="Load", 
            style= dict(description_width='150px', button_color='#4169E1', text_color='white'))
        load_executue.on_click(lambda x : self._on_load())
        param_widgets.append(load_executue)
        tabs.append(ipywidgets.VBox(param_widgets))
        param_widgets = []

        # Deploy
        self._deploy_schema_name = ipywidgets.Text(
            value='',
            placeholder='Specify Schema',
            description='Schema:',
            layout = {'width': '80%'},
            disabled=False
        )
        param_widgets.append(self._deploy_schema_name)
        self._deploy_table_name = ipywidgets.Text(
            value='',
            placeholder='Specify Table',
            layout = {'width': '80%'},
            description='Table:',
            disabled=False
        )
        param_widgets.append(self._deploy_table_name)
        self._top_n = ipywidgets.BoundedIntText(
            value=3,
            min=1,
            max=100,
            step=1,
            description='Top N:',
            tooltip="Specifies the top n models to be saved. If 'ranks' is provided, then 'top_n' is ignored",
            layout = {'width': '80%'},
            disabled=False
        )
        param_widgets.append(self._top_n)
        self._ranks = ipywidgets.Text(
            value='',
            placeholder='Enter comma seperated values e.g. 1, 3, 5',
            description='Ranks:',
            layout = {'width': '80%'},
            tooltip="Specifies the ranks for the models to be saved. If 'ranks' is provided, then 'top_n' is ignored",
            disabled=False
        )

        param_widgets.append(self._ranks)
        deploy_executue = ipywidgets.Button(description="Deploy", 
            style= dict(description_width='150px', button_color='#4169E1', text_color='white'))
        deploy_executue.on_click(lambda x : self._on_deploy())
        param_widgets.append(deploy_executue)
        tabs.append(ipywidgets.VBox(param_widgets))
        param_widgets = []

              
        self._tabs = ipywidgets.Tab()
        self._tabs.children = tabs
        self._tabs.set_title(index=0,title="Initialize")
        self._tabs.set_title(index=1,title="Prediction")
        self._tabs.set_title(index=2,title="Load")
        self._tabs.set_title(index=3,title="Deploy")
        
        if self._allow_logout:
            self._logout_button = ipywidgets.Button(
                description='Logout',
                disabled=False,
                tooltip='Log out of connection',
            )
            self._logout_button.on_click(lambda x : self._on_logout())
            self._task_ui = ipywidgets.VBox([self._logout_button, self._tabs])
        else:
            self._task_ui = self._tabs
        
        self._update_auto_ml()
        
    def _open_ui(self):
        """
        DESCRIPTION:
            Private function that opens the teradatamlwidgets AutoML UI. 

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """
        if not self._embedded_mode:
            self._show_display(self._task_ui, True)
        pass
        
    def _on_tasks_changed(self):
        """
        DESCRIPTION:
            Private function that is called when Algorithm button is changed
            and it will update the UI.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            None.
        """

        if self._current_task == self._tasks.value:
            return
        self._current_task = self._tasks.value

        # Update Options in stopping metric
        value = self._stopping_metric_ui.value
        self._stopping_metric_ui.value = ''
        self._stopping_metric_ui.options = self._get_stopping_metric_options()
        
        if value in self._stopping_metric_ui.options:
            self._stopping_metric_ui.value = value
        
    def _get_stopping_metric_options(self):
        """
        DESCRIPTION:
            Private function that returns the stopping metric permitted values
            based on the current task : regression or classification.

        PARAMETERS:
            None.
        
        RAISES:
            None.

        RETURNS:
            Type: list of str
        """
        if self._current_task == "Classification":
            return ['','MICRO-F1','MACRO-F1',
                  'MICRO-RECALL','MACRO-RECALL',
                  'MICRO-PRECISION', 'MACRO-PRECISION',
                  'WEIGHTED-PRECISION','WEIGHTED-RECALL',
                  'WEIGHTED-F1', 'ACCURACY']
        else:
            return ['',"R2", "MAE", "MSE", "MSLE", "RMSE", "RMSLE"]


    def _get_auto_ml(self):
        """
        DESCRIPTION:
            Function returns the AutoML generated.

        PARAMETERS:
            None

        RETURNS:
            teradataml.automl.AutoClassifier or teradataml.automl.AutoRegressor 
        """
        return self._automl_obj  

    def _get_output_dataframe(self):
        """
        DESCRIPTION:
            Function returns the predicted dataframe output generated.

        PARAMETERS:
            None

        RETURNS:
            teradataml.DataFrame 
        """
        return self._predicted_output

    def _show_dialog(self, html, clear=True):
        """
        Private function that shows a HTML message in the cell with a close button.

        PARAMETERS:
            html:
                String with HTML tags.
                Types: str
            clear:
                Specifies whether UI should be cleared.
                Type: bool

        RAISES:
            None.
            
        RETURNS:
            None.
        """
        # If AutoML is to be called within the Analytic Function UI, then show dialog accordingly 
        if self._analytic_function_ui:
            self._analytic_function_ui._show_dialog(html)
        # Otherwise AutoML UI will show as a standalone widget
        else:
            super()._show_dialog(html, clear)


