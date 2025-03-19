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


from teradatamlwidgets.auto_ml.UiImpl import _UiImpl


class Ui:
    """
    The teradatamlwidgets Interactive AutoML UI.
    """

    def __init__(
        self,  
        training_table, 
        predict_table=None,
        task="Classification", 
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
        default_database="", 
        connection=None):
        """
        DESCRIPTION:
            Constructor for teradatamlwidgets Interactive AutoML UI.

        PARAMETERS:
            training_table: 
                Required Argument. 
                Specifies the input teradataml DataFrame or string that contains the data which is used for training. 
                Types: str or teradataml.DataFrame
                
            predict_table: 
                Optional Argument. 
                Specifies the teradataml DataFrame or string that contains the data which is used for predictions.
                Types: str or teradataml.DataFrame
            
            task: 
                Optional Argument. 
                Specifies the name of the task.
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
                Permitted Values: 
                    * 0: prints the progress bar and leaderboard.
                    * 1: prints the execution steps of AutoML.
                    * 2: prints the intermediate data between the execution of each step of AutoML.
                Default Value: 0
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

        RETURNS:
            Instance of the UI class.

        RAISES:
            None.

        EXAMPLE:
        >>> from teradatamlwidgets.auto_ml.Ui import * 
        >>> ui=Ui(task="Classification", training_table="titanic_training", predict_table="titanic_testing")

        """
        
        self._ui_impl=_UiImpl(
                        training_table=training_table, 
                        predict_table=predict_table,
                        task=task, 
                        target_column=target_column, 
                        default_database=default_database, 
                        connection=connection, 
                        algorithms=algorithms, 
                        verbose=verbose, 
                        max_runtime_secs=max_runtime_secs, 
                        stopping_metric=stopping_metric, 
                        stopping_tolerance=stopping_tolerance, 
                        max_models=max_models, 
                        custom_config_file=custom_config_file,
                        rank=rank,
                        persist=persist)

    def get_prediction_dataframe(self):
        """
        DESCRIPTION:
            Function returns the predicted dataframe output.

        PARAMETERS:
            None

        RETURNS:
            teradataml.DataFrame 
        """
        return self._ui_impl._get_output_dataframe()

    def get_auto_ml(self):
        """
        DESCRIPTION:
            Function returns the teradataml AutoML instance.

        PARAMETERS:
            None

        RETURNS:
            teradataml.automl.AutoClassifier or teradataml.automl.AutoRegressor 
        """
        return self._ui_impl._get_auto_ml()  

    def get_leaderboard(self):
        """
        DESCRIPTION:
            Function returns the teradataml AutoML leaderboard.

        PARAMETERS:
            None

        RETURNS:
            Pandas DataFrame
        """
        return self.get_auto_ml().leaderboard()  

