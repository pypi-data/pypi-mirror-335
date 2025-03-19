## Teradata Widgets

teradatamlwidgets makes available to Python users a user interface to a collection of analytic functions and plot functions that reside on Teradata Vantage. This package provides Data Scientists and Teradata users a simple UI experience within a Jupyter Notebook to perform analytics and visualization on Teradata Vantage with no SQL coding and limited python coding required.

For documentation and tutorial notebooks please visit [Documentation](https://docs.teradata.com/r/Teradataml-Widgets/March-2024).

For Teradata customer support, please visit [Teradata Support](https://support.teradata.com/csm).

Copyright 2024, Teradata. All Rights Reserved.

### Table of Contents
* [Release Notes](#release-notes)
* [Installation and Requirements](#installation-and-requirements)
* [Using the Teradata Widgets Package](#using-the-teradata-python-package)
* [Documentation](#documentation)
* [License](#license)

## Release Notes:
#### teradatamlwidgets 20.0.0.5
* ##### New Features/Functionality
  * Exploratory Data Analysis UI
  * BYOM Scoring
  * Login UI
  * AutoML
  * Script Table Operator
  * Describe
  * Persist
* ###### New APIs:
  * `teradatamlwidgets.eda.Ui()`
  * `teradatamlwidgets.byom_functions.Ui()`
  * `teradatamlwidgets.login.Ui()`
  * `teradatamlwidgets.auto_ml.Ui()`
  * `teradatamlwidgets.script.Ui()`
  * `teradatamlwidgets.describe.Ui()`
  * `teradatamlwidgets.persist.Ui()`
  * Added support for notebook utilities.
    * `tdnb.text()` to create text widget.
    * `tdnb.dropdown()` to create dropdown widget.
    * `tdnb.multi_select()` to create multiselect widget.
    * `tdnb.get()` to get the value of widget.
    * `tdnb.get_all()` to get all the values of widgets in current session.
    * `tdnb.remove()` to remove the widget.
    * `tdnb.remove_all()` to remove all the widgets in current session.
    * `tdnb.run_notebook()` to run a notebook from another notebook.
    * `tdnb.exit()` to exit the notebook with a message.

* ##### Bug Fixes
  * Fully qualified table names are now correctly recognized.

#### teradatamlwidgets 20.0.0.4
* ##### New Features/Functionality
  * None
* ###### New APIs:
  * None
* ##### Bug Fixes
  * Fixed list of SQLE functions

#### teradatamlwidgets 20.0.0.3
* ##### New Features/Functionality
  * None
* ###### New APIs:
  * None
* ##### Bug Fixes
  * Using native dialog boxes
  * Parameter name change for Plot (color).

#### teradatamlwidgets 20.0.0.2
* ##### New Features/Functionality
  * Updated documentation
* ###### New APIs:
  * None
* ##### Bug Fixes
  * Initialized default database

#### teradatamlwidgets 20.0.0.1
* ##### New Features/Functionality
  * Updated documentation
* ###### New APIs:
  * None
* ##### Bug Fixes
  * None

#### teradatamlwidgets 20.0.0.0
* ##### New Features/Functionality
* ###### New APIs:
    * Analytic functions
      * `teradatamlwidgets.analytic_functions.Ui()`
      * `teradatamlwidgets.analytic_functions.get_output_dataframe()`
    * Plotting
      * `teradatamlwidgets.plot.ShowPlots()`
* ##### Bug Fixes
  * None


## Installation and Requirements

### Package Requirements:
* Python 3.5 or later

Note: 32-bit Python is not supported.

### Minimum System Requirements:
* Windows 7 (64Bit) or later
* macOS 10.9 (64Bit) or later
* Red Hat 7 or later versions
* Ubuntu 16.04 or later versions
* CentOS 7 or later versions
* SLES 12 or later versions
* Teradata Vantage Advanced SQL Engine:
    * Advanced SQL Engine 16.20 Feature Update 1 or later
* For a Teradata Vantage system with the ML Engine:
    * Teradata Machine Learning Engine 08.00.03.01 or later

### Installation

Use pip to install the Teradata Widgets Package for Advanced Analytics.

Platform       | Command
-------------- | ---
macOS/Linux    | `pip install teradatamlwidgets`
Windows        | `py -3 -m pip install teradatamlwidgets`

When upgrading to a new version of the Teradata Widgets Package, you may need to use pip install's `--no-cache-dir` option to force the download of the new version.

Platform       | Command
-------------- | ---
macOS/Linux    | `pip install --no-cache-dir -U teradatamlwidgets`
Windows        | `py -3 -m pip install --no-cache-dir -U teradatamlwidgets`

## Using the Teradata Python Package

Your Python script must import the `teradatamlwidgets` package in order to use the Teradata Widgets Package:

```
from teradatamlwidgets import login
ui = login.Ui()
```
```
from teradataml import *
from teradatamlwidgets import analytic_functions
Load the example data.
load_example_data("movavg", ["ibm_stock"])
load_example_data("teradataml", "titanic")
inputs = ["ibm_stock"]
outputs = ["Project_OutMovingAverageTest"]
ui = analytic_functions.Ui(
		function='MovingAverage',
		outputs=outputs, 
		inputs=inputs)
```
```
from teradataml import *
from teradatamlwidgets import plot
# Load the example data.
load_example_data("movavg", "ibm_stock")
load_example_data("teradataml", "iris_input")
# Plot
plot1 = plot.Ui(
		table_name="ibm_stock", 
		current_plot="Line", 
		x='period', 
		series='stockprice', 
		style='green')
plot2 = plot.Ui(
		table_name="iris_input", 
		current_plot="Scatter", 
		x='sepal_length', 
		series='petal_length', 
		xlabel='sepal_length',
		ylabel='petal_length',
		grid_color='black',
		grid_linewidth=1, 
		grid_linestyle="-",
		style='red', 
		title='Scatter Plot of sepal_length vs petal_length',
		heading= 'Scatter Plot Example')
# Combine Plots
plot.ShowPlots([plot1, plot2], nrows=1, ncols=2) 
```
```
from teradatamlwidgets import byom_functions 
# BYOM Scoring Functions
byom = byom_functions.Ui(
		function = "DataRobotPredict", 
		byom_location = "mldb", 
		input_table="iris_test", 
		model_id="dr_iris_rf", 
		model_table="byom_models")
```
```
from teradatamlwidgets import auto_ml
ui = auto_ml.Ui(
		task="Classification", 
		training_table=iris_train, 
		testing_table=iris_test,
		predict_table='iris_test', 
		algorithms=['xgboost', 'knn'],
		verbose=0,
		max_runtime_secs=300,
		max_models=5)
```

```
from teradatasqlalchemy import (CHAR, VARCHAR, CLOB, INTEGER, FLOAT)
from teradatamlwidgets import script 
ui = script.Ui(
		script_name='ex1pSco.py',
        files_local_path='.', 
        script_command='python3  ./<db_name>/ex1pScoViaDSS.py',
        returns=OrderedDict({"Cust_ID": INTEGER(), "Prob_0": FLOAT(), "Prob_1": FLOAT(), "Actual_Value": INTEGER()}))
```

```
from teradatamlwidgets import eda
from teradataml import DataFrame
df = DataFrame("ibm_stock")
ui = eda.Ui(df = df)
```

```
from teradatamlwidgets import describe
from teradataml import DataFrame
df = DataFrame("ibm_stock")
ui = describe.Ui(df = df)
```

```
from teradatamlwidgets import persist
from teradataml import DataFrame
df = DataFrame("ibm_stock")
ui = persist.Ui(df = df)
```
+ Details

	+ This package is useful to Data Scientists and Teradata users and provides following:
	
		+ A simple UI experience within Jupyter Notebook.

		+ Access to In-DB analytics
                
		+ Visualizations

		+ Integration with teradataml

		+ Enable simple and easy integration with 3rd party workbenches


	+ `teradatamlwidgets.login.Ui` Class
		+ Purpose
			+ Opens the function UI dialog in the notebook for the functions.
		+ Function Output 
			+ This function will return instance of notebook UI interface.
		+ Usage Considerations
			+ If you are not already logged in then this will only allow you to log out otherwise the login screen is shown.
			
	+ `teradatamlwidgets.analytic_functions.Ui` Class
		+ Purpose
			+ Opens the UI dialog in the notebook for the Analytic Functions (subset of the Analytics Database analytic functions, Vantage Analytics Library (VAL) functions, Unbounded Array Framework (UAF) time series functions).
		+ Function Output 
			+ This function will return instance of notebook UI interface for analytic functions.
		+ Usage Considerations
			+ If you are not already logged in, the first time this is called, the “Login” user interface will be displayed so the user can log into a Teradata instance which creates the internal instance.

	+ `teradatamlwidgets.analytic_functions.get_output_dataframe` Method
		+ Purpose
			+ Gets the DataFrame of the executed function.
		+ Function Output 
			+ Return Value: teradataml.DataFrame. Returns the output of the function as a teradataml DataFrame.
		+ Usage Considerations
			+ NA

	+ `teradatamlwidgets.plot.Ui` Class
		+ Purpose
			+ Allows a user interface for plotting that allows the user to set plotting parameters and then visualize the plots. The internal implementation uses the functionality of TD_PLOT exposed in teradataml DataFrame.
		+ Function Output 
			+ This function will return instance of notebook UI interface for TD_PLOT.
		+ Usage Considerations
			+ If you are not already logged in, the first time this is called, the “Login” user interface will be displayed so the user can log into a Teradata instance which creates the internal instance.

	+ `teradatamlwidgets.plot.ShowPlots` Method
		+ Purpose
			+ ShowPlots combines multiple plots together into one figure.

	+ `teradatamlwidgets.eda.Ui` Class
		+ Purpose
			+ The Exploratory Data Analysis UI allows the user to take a deeper look into their dataset. The tabs include Data, Analyze, Visualize, Describe, and Persist. This provides visual components for scaled, in-Database Analytics with data that you keep in the Teradata Vantage Analytics Database within a notebook.
		+ Function Output 
			+ This function will return instance of notebook EDA UI interface.
		+ Usage Considerations
			+ You must login before either using Login UI Class, or using teradataml create_context().
		
	+ `teradatamlwidgets.byom_functions.Ui` Class
		+ Purpose
			+ Opens the UI dialog in the notebook for the BYOM functions.
		+ Function Output 
			+ This function will return instance of notebook BYOM functions UI interface.
		+ Usage Considerations
			+ If you are not already logged in, the first time this is called, the “Login” user interface will be displayed so the user can log into a Teradata instance which creates the internal instance.

	+ `teradatamlwidgets.byom_functions.get_output_dataframe` Method
		+ Purpose
			+ Gets the DataFrame of the executed function.
		+ Function Output 
			+ Return Value: teradataml.DataFrame. Returns the output of the function as a teradataml DataFrame.
		+ Usage Considerations
			+ NA

	+ `teradatamlwidgets.auto_ml.Ui` Class
		+ Purpose
			+ Opens the UI dialog in the notebook for the AutoML functions.
		+ Function Output 
			+ This function will return instance of notebook AutoML UI interface.
		+ Usage Considerations
			+ If you are not already logged in, the first time this is called, the “Login” user interface will be displayed so the user can log into a Teradata instance which creates the internal instance.

	+ `teradatamlwidgets.auto_ml.get_prediction_dataframe` Method
		+ Purpose
			+ To access the predicted output table.
		+ Function Output 
			+ Return Value: teradataml.DataFrame.
		+ Usage Considerations
			+ NA

	+ `teradatamlwidgets.auto_ml.get_auto_ml` Method
		+ Purpose
			+ To access the AutoML instance.
		+ Function Output 
			+ Return Value: Pandas DataFrame.
		+ Usage Considerations
			+ NA

	+ `teradatamlwidgets.auto_ml.get_leaderboard` Method
		+ Purpose
			+ To access the leaderboard. 
		+ Function Output 
			+ Return Value: teradataml.automl.AutoClassifier or teradataml.automl.AutoRegressor. 
		+ Usage Considerations
			+ NA

	+ `teradatamlwidgets.script.Ui` Class
		+ Purpose
			+ Opens the UI dialog in the notebook for the Script function.
		+ Function Output 
			+ This function will return instance of notebook Script UI interface.
		+ Usage Considerations
			+ If you are not already logged in, the first time this is called, the “Login” user interface will be displayed so the user can log into a Teradata instance which creates the internal instance.

	+ `teradatamlwidgets.script.get_output_dataframe` Method
		+ Purpose
			+ Gets the DataFrame of the script result.
		+ Function Output 
			+ Return Value: teradataml.DataFrame. Returns the output of the function as a teradataml DataFrame.
		+ Usage Considerations
			+ NA

	+ `teradatamlwidgets.describe.Ui` Class
		+ Purpose
			+ Allows user to see the dataFrame description and information, including Shape and Size, Column Statistics, Column Types, Column Summary, Categorical Summary, Futile Columns and Source Query.
		+ Function Output 
			+ This function will return instance of notebook Describe UI interface.
		+ Usage Considerations
			+ You must login before either using Login UI Class, or using teradataml create_context().

	+ `teradatamlwidgets.persist.Ui` Class
		+ Purpose
			+ Allows user to write records stored in a teradataml DataFrame to Teradata Vantage.
		+ Function Output 
			+ This function will return instance of notebook Persist UI interface.
		+ Usage Considerations
			+ You must login before either using Login UI Class, or using teradataml create_context().

## Documentation

General product information, including installation instructions, is available in the [Teradata Documentation website](https://docs.teradata.com/search/documents?query=package+python+-lake&filters=category~%2522Programming+Reference%2522_%2522User+Guide%2522*prodname~%2522Teradata+Package+for+Python%2522_%2522Teradata+Python+Package%2522&sort=last_update&virtual-field=title_only&content-lang=)

## License

Use of the Teradata Widgets Package is governed by the *License Agreement for the Teradata Widgets Package for Advanced Analytics*. 
After installation, the `LICENSE` and `LICENSE-3RD-PARTY` files are located in the `teradata_widget` directory of the Python installation directory.





