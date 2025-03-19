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
import ipywidgets
from IPython.display import clear_output, HTML,Javascript, display
import pandas as pd
import teradataml
from teradatamlwidgets.base_ui import _BaseUi

class _BasePlot:
    """
    Private class that is base class for all plot UI instances
    """

    # Maximum number of series allowed in the UI
    NUM_Y_SERIES = 16

    def __init__(self, base, df):
        """
        DESCRIPTION:
            Constructor to private class that is base class for all plot UI instances
        """
        self._base = base
        self._df = df
        
    def _get_ui(self):
        """
        Private method that returns the ipywidgets of this plot instance  

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            ipywidgets instance 
        """
        return self._plot_ui

    def _get_columns_of_type(self, valid_types):
        """
        Private method that gets the columns that can be used in XY UI menus

        PARAMETERS:
            valid_types:
                Limits the columns returned if supports these valid types
                Types: list of str
                valid types in the list can be "int" or "float"

        RAISES:
            None.

        RETURNS:
            list of call columns of dataframe that can be shown in UI menu
            Type: str list
        """
        result = []
        for column_name, column_type in self._df.dtypes._column_names_and_types:
            if column_type not in valid_types:
                if column_type == "datetime.date" and "int" in valid_types:
                    pass
                elif column_type == "datetime.date" and "float" in valid_types:
                    pass
                else:
                    continue
            result.append(column_name)
        return result

    def _show_plot(self, base):
        """
        Private method that shows the plot in the cell

        PARAMETERS:
            base:
                The UI private instance that this plot instance is created in
                Types: instance of UiImpl
        RAISES:
            None.

        RETURNS:
            None
        """
        try:
            # Remove old plot
            if os.path.exists("plot.png"):
                os.remove("plot.png")
            # Currently we save this to a file
            self._plot.save("plot")
            # Then we load the save image
            file = open("plot.png", "rb")
            # Read the loaded image
            image = file.read()
            # And then show in ipwidgets
            base._image.value = image
            # Show ipwidgets Image widget
            base._image.layout.display = "inline"
            base._image.layout.visibility = "visible"
            base._message_widget.value = ""
        except Exception as e:
            base._message_widget.value = "<i style='color:red;'>TD_Plot Error</i>"
            base._image.layout.display = "none"
            print("Plot failed", e)
            output_value = '''
                require(
                    ["base/js/dialog"], 
                    function(dialog) {
                        dialog.modal({
                            title: "Error",
                            body: $("<div></div>").append('__BODY__'),
                            buttons: {
                                "OK": {
                                }}
                        });
                    }
                );'''
            error_message = str(e)
            error_list = error_message.split("\n")
            filter_error_list = [line for line in error_list if not line.strip(" ").startswith("at")]
            error_message = "\n".join(filter_error_list)
            error_message = error_message.replace("'", '"')
            error_message = error_message.replace('\n', '<br>');
            output_value = output_value.replace("__BODY__", error_message)
            if _BaseUi.show_native_dialog:
                display(HTML(error_message))
            else:
                display(Javascript(output_value))

    def _get_num_series_visible(self):
        """
        Private method that returns the number of visible series

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            Types: int
        """
        result = 1
        for index in range(1, _BasePlot.NUM_Y_SERIES):
            if self._Y[index].value != "" and self._Y[index].layout.visibility == "visible":
                result += 1
        return result

    def _create_y_series(self, columns):
        """
        Private method that creates the series list of Drop Down ipywidgets 

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            Types: list of Drop Down ipywidgets 
        """
        self._Y = {}
        result = []

        arguments = []
        # Check is series is in constructor arguments
        if 'series' in self._base._kwargs:
            arguments = self._base._kwargs['series']
            if type(arguments)==str:
                # Make it into an array
                arguments = [arguments]
        for index in range(_BasePlot.NUM_Y_SERIES):
            value = arguments[index] if index < len(arguments) else ""
            if value not in columns:
                columns.append(value)
            self._Y[index] = ipywidgets.Dropdown(
                options=[""] + columns,
                value= value,
                description="Y[{}]".format(index),
                disabled=False)
            if index <= len(arguments):
                self._Y[index].layout.visibility = "visible"
            else:
                self._Y[index].layout.visibility = "hidden"
            self._Y[index].y_index = index
            self._Y[index].observe(lambda change : self._update_y_series(change.owner.y_index), names='value')
            result.append(self._Y[index])
        return result
        
    def _update_y_series(self, index):
        """
        Private method that shows/hides the Y series on how many the user has selected

        PARAMETERS:
            index:
                The number of Y series UI that should be shown
                Type: int

        RAISES:
            None.

        RETURNS:
            None.
        """
        # Hide all series to right
        if self._Y[index].value == "":
            for i in range(index+1, _BasePlot.NUM_Y_SERIES):
                self._Y[i].layout.visibility = "hidden"
                self._Y[i].value = ""
        else:
            # Show the series just to right
            if index+1 < _BasePlot.NUM_Y_SERIES:
                self._Y[index+1].layout.visibility = "visible"
        self._base._change_plot()

    def _get_xy_settings(self, plot_settings):
        try:
            y = []
            for index in range(_BasePlot.NUM_Y_SERIES):
                if self._Y[index].value != "" and self._Y[index].layout.visibility == "visible":
                    y.append(self._Y[index].value)
            plot_settings['x'] = self._X.value
            plot_settings['series'] = y
        except:
            plot_settings['x'] = ""
            plot_settings['series'] = []

    def _get_y_series(self):
        """
        Private method that series list of Drop Down ipywidgets 

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            Types: list of Drop Down ipywidgets 
        """
        y = []
        for index in range(_BasePlot.NUM_Y_SERIES):
            if self._Y[index].value != "" and self._Y[index].layout.visibility == "visible":
                y.append(self._df[self._Y[index].value])
        return y

    def _create_ui(self, x_columns, y_columns, is_scale=False):
        """
        Private method that creates the ipywidget UI for this plot instance

        PARAMETERS:
            x_columns
                The valid options for Dropdown widget for the X value of series 
                Type: list of str

            y_columns
                The valid options for Dropdown widget for the Y value of series 
                Type: list of str

            is_scale
                Optional argument
                When True will add scale UI control
                Default Value: False

        RAISES:
            None.

        RETURNS:
            The resulting row of ipywidgets that represents this plot instance
            Type: list of ipywidgets 
        """
        rows = []
        # Get the X value from constructor arguments
        X = self._base._kwargs.get('x', x_columns[0])
        # Make sure the X value is in the columns choices
        if X not in x_columns:
            x_columns.append(X)
        self._X = ipywidgets.Dropdown(
            options=x_columns,
            value=X,
            description='X:',
            disabled=False)
        rows.append(self._X)
        if is_scale:
            scale = self._base._kwargs.get('scale', x_columns[0])
            if scale not in x_columns:
                x_columns.append(scale)
            self._Scale = ipywidgets.Dropdown(
                value=scale,
                options=x_columns,
                description='Scale:',
                disabled=False)
            rows.append(self._Scale)
        # Arrange 4 in a row
        y_series = self._create_y_series(y_columns)
        for i in range(0, _BasePlot.NUM_Y_SERIES, 4):
            series_row = []
            series_row.append(y_series[i])
            series_row.append(y_series[i+1])
            series_row.append(y_series[i+2])
            series_row.append(y_series[i+3])
            rows.append(ipywidgets.HBox(series_row))
        return rows

class _LinePlot(_BasePlot):
    """
    Private class that is the instance of a Line Plot UI
    """
    def __init__(self, base, df):
        """
        Constructor to Private class that is the instance of a Line Plot UI
        """
        super().__init__(base, df)
        self._create_ui()
        
    def _do_plot(self, base_args, show=True, ax=None, figure=None):
        """
        Private method that executes the teradataml Plot function and shows the result in cell

        PARAMETERS:
            base_args
                The Plot's parameter values set in the UI
                Type: dict of parameter values

            show:
                Optional Argument
                When True will show the result in the cell
                Default Value: True
                Type: bool

            ax:
                Optional Argument
                Matplotlib axis for plot display
                Type: matplotlib axis

           ax:
                Optional Argument
                Matplotlib figure for plot display
                Type: matplotlib figure

        RAISES:
            None.

        RETURNS:
            Plot instance returned from teradataml plot call
            Type: matplotlib plot instance
        """
        y = self._get_y_series()

        self._plot =  self._df.plot(kind='line', x=self._df[self._X.value], y=y, 
            title = self._base._title.value if self._base._title.value else None,
            heading = self._base._heading.value if self._base._heading.value else None, 
            ax=ax,
            figure=figure,
            **base_args)
        if show:
            self._show_plot(self._base)
        return self._plot

    def _create_ui(self):
        """
        Private method that creates the ipywidget UI for this plot instance

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None. 
        """
        x_columns = self._get_columns_of_type(['int', 'float'])
        y_columns = self._get_columns_of_type(['int', 'float'])
        rows = _BasePlot._create_ui(self, x_columns, y_columns)
        self._plot_ui = ipywidgets.VBox(rows)

class _BarPlot(_BasePlot):
    """
    Private class that is the instance of a Bar Plot UI
    """
    def __init__(self, base, df):
        """
        Constructor to Private class that is the instance of a Bar Plot UI
        """
        super().__init__(base, df)
        self._create_ui()
        
    def _do_plot(self, base_args, show=True, ax=None, figure=None):
        """
        Private method that executes the teradataml Plot function and shows the result in cell

        PARAMETERS:
            base_args
                The Plot's parameter values set in the UI
                Type: dict of parameter values

            show:
                Optional Argument
                When True will show the result in the cell
                Default Value: True
                Type: bool

            ax:
                Optional Argument
                Matplotlib axis for plot display
                Type: matplotlib axis

           ax:
                Optional Argument
                Matplotlib figure for plot display
                Type: matplotlib figure

        RAISES:
            None.

        RETURNS:
            Plot instance returned from teradataml plot call
            Type: matplotlib plot instance
        """
        y = self._get_y_series()

        self._plot =  self._df.plot(kind='bar', x=self._df[self._X.value], y=y, 
            title = self._base._title.value if self._base._title.value else None,
            heading = self._base._heading.value if self._base._heading.value else None, 
            ax=ax,
            figure=figure,
            **base_args)

        if show:
            self._show_plot(self._base)
        return self._plot

    def _create_ui(self):
        """
        Private method that creates the ipywidget UI for this plot instance

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None. 
        """
        x_columns = self._get_columns_of_type(['float', 'int'])
        y_columns = self._get_columns_of_type(['float', 'int'])
        rows = _BasePlot._create_ui(self, x_columns, y_columns)
        self._plot_ui = ipywidgets.VBox(rows)

class _ScatterPlot(_BasePlot):
    """
    Private class that is the instance of a Scatter Plot UI
    """
    def __init__(self, base, df):
        """
        Constructor to Private class that is the instance of a Scatter Plot UI
        """
        super().__init__(base, df)
        self._create_ui()
        
    def _do_plot(self, base_args, show=True, ax=None, figure=None):
        """
        Private method that executes the teradataml Plot function and shows the result in cell

        PARAMETERS:
            base_args
                The Plot's parameter values set in the UI
                Type: dict of parameter values

            show:
                Optional Argument
                When True will show the result in the cell
                Default Value: True
                Type: bool

            ax:
                Optional Argument
                Matplotlib axis for plot display
                Type: matplotlib axis

           ax:
                Optional Argument
                Matplotlib figure for plot display
                Type: matplotlib figure

        RAISES:
            None.

        RETURNS:
            Plot instance returned from teradataml plot call
            Type: matplotlib plot instance
        """
        y = self._get_y_series()

        self._plot =  self._df.plot(kind='scatter', x=self._df[self._X.value], y=y, 
            title = self._base._title.value if self._base._title.value else None,
            heading = self._base._heading.value if self._base._heading.value else None, 
            ax=ax,
            figure=figure,
            **base_args)

        if show:
            self._show_plot(self._base)
        return self._plot

    def _create_ui(self):
        """
        Private method that creates the ipywidget UI for this plot instance

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None. 
        """
        x_columns = self._get_columns_of_type(['float', 'int'])
        y_columns = self._get_columns_of_type(['float', 'int'])
        rows = _BasePlot._create_ui(self, x_columns, y_columns)
        self._plot_ui = ipywidgets.VBox(rows)

class _CorrPlot(_BasePlot):
    """
    Private class that is the instance of a Correlation Plot UI
    """
    def __init__(self, base, df):
        """
        Constructor to Private class that is the instance of a Correlation Plot UI
        """
        super().__init__(base, df)
        self._create_ui()
        
    def _do_plot(self, base_args, show=True, ax=None, figure=None):
        """
        Private method that executes the teradataml Plot function and shows the result in cell

        PARAMETERS:
            base_args
                The Plot's parameter values set in the UI
                Type: dict of parameter values

            show:
                Optional Argument
                When True will show the result in the cell
                Default Value: True
                Type: bool

            ax:
                Optional Argument
                Matplotlib axis for plot display
                Type: matplotlib axis

           ax:
                Optional Argument
                Matplotlib figure for plot display
                Type: matplotlib figure

        RAISES:
            None.

        RETURNS:
            Plot instance returned from teradataml plot call
            Type: matplotlib plot instance
        """
        y = self._get_y_series()

        self._plot =  self._df.plot(kind='corr', x=self._df[self._X.value], y=y, 
            title = self._base._title.value if self._base._title.value else None,
            heading = self._base._heading.value if self._base._heading.value else None, 
            ax=ax,
            figure=figure,
            **base_args)

        if show:
            self._show_plot(self._base)
        return self._plot

    def _create_ui(self):
        """
        Private method that creates the ipywidget UI for this plot instance

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None. 
        """
        x_columns = self._get_columns_of_type(['float', 'int'])
        y_columns = self._get_columns_of_type(['float', 'int'])
        rows = _BasePlot._create_ui(self, x_columns, y_columns)
        self._plot_ui = ipywidgets.VBox(rows)

class _WigglePlot(_BasePlot):
    """
    Private class that is the instance of a Wiggle Plot UI
    """
    def __init__(self, base, df):
        """
        Constructor to Private class that is the instance of a Wiggle Plot UI
        """
        super().__init__(base, df)
        self._create_ui()
        
    def _do_plot(self, base_args, show=True, ax=None, figure=None):
        """
        Private method that executes the teradataml Plot function and shows the result in cell

        PARAMETERS:
            base_args
                The Plot's parameter values set in the UI
                Type: dict of parameter values

            show:
                Optional Argument
                When True will show the result in the cell
                Default Value: True
                Type: bool

            ax:
                Optional Argument
                Matplotlib axis for plot display
                Type: matplotlib axis

           ax:
                Optional Argument
                Matplotlib figure for plot display
                Type: matplotlib figure

        RAISES:
            None.

        RETURNS:
            Plot instance returned from teradataml plot call
            Type: matplotlib plot instance
        """
        y = self._get_y_series()

        self._plot =  self._df.plot(
            kind='wiggle', 
            x=self._df[self._X.value], 
            y=y, 
            scale = self._df[self._Scale.value],
            title = self._base._title.value if self._base._title.value else None,
            heading = self._base._heading.value if self._base._heading.value else None, 
            ax=ax,
            figure=figure,
            **base_args)

        if show:
            self._show_plot(self._base)
        return self._plot

    def _create_ui(self):
        """
        Private method that creates the ipywidget UI for this plot instance

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None. 
        """
        x_columns = self._get_columns_of_type(['float', 'int'])
        y_columns = self._get_columns_of_type(['float', 'int'])
        rows = _BasePlot._create_ui(self, x_columns, y_columns, True)
        wiggle_row = []
        self._wiggle_fill = ipywidgets.ToggleButton(
            value=False,
            description='Wiggle Fill',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Fill Wiggle Area',
            icon='check' # (FontAwesome names without the `fa-` prefix)
        )       
        wiggle_row.append(self._wiggle_fill)
        self._wiggle_scale = ipywidgets.ToggleButton(
            value=False,
            description='Wiggle Scale',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Specifies the scale of the wiggle',
            icon='check' # (FontAwesome names without the `fa-` prefix)
        )
        wiggle_row.append(self._wiggle_scale)
        self._plot_ui = ipywidgets.VBox([ipywidgets.HBox(wiggle_row)] + rows)

class _MeshPlot(_BasePlot):
    """
    Private class that is the instance of a Mesh Plot UI
    """
    def __init__(self, base, df):
        """
        Constructor to Private class that is the instance of a Mesh Plot UI
        """
        super().__init__(base, df)
        self._create_ui()
        
    def _do_plot(self, base_args, show=True, ax=None, figure=None):
        """
        Private method that executes the teradataml Plot function and shows the result in cell

        PARAMETERS:
            base_args
                The Plot's parameter values set in the UI
                Type: dict of parameter values

            show:
                Optional Argument
                When True will show the result in the cell
                Default Value: True
                Type: bool

            ax:
                Optional Argument
                Matplotlib axis for plot display
                Type: matplotlib axis

           ax:
                Optional Argument
                Matplotlib figure for plot display
                Type: matplotlib figure

        RAISES:
            None.

        RETURNS:
            Plot instance returned from teradataml plot call
            Type: matplotlib plot instance
        """
        y = self._get_y_series()

        self._plot =  self._df.plot(kind='mesh', 
            x=self._df[self._X.value], 
            y=y, 
            scale = self._df[self._Scale.value],
            title = self._base._title.value if self._base._title.value else None,
            heading = self._base._heading.value if self._base._heading.value else None, 
            ax=ax,
            figure=figure,
            **base_args)

        if show:
            self._show_plot(self._base)
        return self._plot

    def _create_ui(self):
        """
        Private method that creates the ipywidget UI for this plot instance

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None. 
        """
        x_columns = self._get_columns_of_type(['float', 'int'])
        y_columns = self._get_columns_of_type(['float', 'int'])
        rows = _BasePlot._create_ui(self, x_columns, y_columns, True)
        wiggle_row = []
        self._wiggle_scale = ipywidgets.ToggleButton(
            value=False,
            description='Wiggle Scale',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Specifies the scale of the wiggle',
            icon='check' # (FontAwesome names without the `fa-` prefix)
        )
        wiggle_row.append(self._wiggle_scale)
        #rows.append(self._wiggle_scale)
        self._plot_ui = ipywidgets.VBox([ipywidgets.HBox(wiggle_row)] + rows)

class _GeomPlot(_BasePlot):
    """
    Private class that is the instance of a Geometry Plot UI
    """
    def __init__(self, base, df):
        """
        Constructor to Private class that is the instance of a Geometry Plot UI
        """
        super().__init__(base, df)
        self._create_ui()
        
    def _do_plot(self, base_args, show=True, ax=None, figure=None):
        """
        Private method that executes the teradataml Plot function and shows the result in cell

        PARAMETERS:
            base_args
                The Plot's parameter values set in the UI
                Type: dict of parameter values

            show:
                Optional Argument
                When True will show the result in the cell
                Default Value: True
                Type: bool

            ax:
                Optional Argument
                Matplotlib axis for plot display
                Type: matplotlib axis

           ax:
                Optional Argument
                Matplotlib figure for plot display
                Type: matplotlib figure

        RAISES:
            None.

        RETURNS:
            Plot instance returned from teradataml plot call
            Type: matplotlib plot instance
        """
        y = self._get_y_series()

        self._plot =  self._df.plot(kind='geometry', 
            # Dont need x
            #x=self._df[self._X.value], 
            y=y, 
            title = self._base._title.value if self._base._title.value else None,
            heading = self._base._heading.value if self._base._heading.value else None, 
            ax=ax,
            figure=figure,
            **base_args)

        if show:
            self._show_plot(self._base)
        return self._plot

    def _create_ui(self):
        """
        Private method that creates the ipywidget UI for this plot instance

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None. 
        """
        x_columns = self._get_columns_of_type(['float', 'int'])
        y_columns = self._get_columns_of_type(['float', 'int'])
        rows = _BasePlot._create_ui(self, x_columns, y_columns)
        self._plot_ui = ipywidgets.VBox(rows)
